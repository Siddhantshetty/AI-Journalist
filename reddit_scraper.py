from typing import List
import os
from utils import *
from typing import List
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from tenacity import (
    retry, 
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from aiolimiter import AsyncLimiter
from tenacity import retry, stop_after_attempt, wait_exponential
from datetime import datetime, timedelta


load_dotenv()


two_weeks_ago = datetime.today() - timedelta(days=14) 
two_weeks_ago_str = two_weeks_ago.strftime('%Y-%m-%d')


class MCPOverloadedError(Exception):
    pass


mcp_limiter = AsyncLimiter(1, 15)

# Initialize Groq model (will be created when needed)
model = None

def get_groq_model():
    """Get or create Groq model instance"""
    global model
    if model is None:
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set. Please check your .env file.")
        
        model = ChatGroq(
            model="llama-3.3-70b-versatile",  # Updated to current supported model
            api_key=groq_api_key,
            temperature=0.3
        )
    return model

server_params = StdioServerParameters(
    command="npx",
    env={
        "API_TOKEN": os.getenv("API_TOKEN"),
        "WEB_UNLOCKER_ZONE": os.getenv("WEB_UNLOCKER_ZONE"),
    },
    args=["@brightdata/mcp"],
)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=15, max=60),
    retry=retry_if_exception_type(MCPOverloadedError),
    reraise=True
)
async def process_topic(agent, topic: str):
    async with mcp_limiter:
        messages = [
            {
                "role": "system",
                "content": f"""You are a Reddit analysis expert. Use available tools to:
                1. Find top 2 posts about the given topic BUT only after {two_weeks_ago_str}, NOTHING before this date strictly!
                2. Analyze their content and sentiment
                3. Create a summary of discussions and overall sentiment"""
            },
            {
                "role": "user",
                "content": f"""Analyze Reddit posts about '{topic}'. 
                Provide a comprehensive summary including:
                - Main discussion points
                - Key opinions expressed
                - Any notable trends or patterns
                - Summarize the overall narrative, discussion points and also quote interesting comments without mentioning names
                - Overall sentiment (positive/neutral/negative)"""
            }                   
        ]
        
        try:
            response = await agent.ainvoke({"messages": messages})
            return response["messages"][-1].content
        except Exception as e:
            if "Overloaded" in str(e):
                raise MCPOverloadedError("Service overloaded")
            else:
                raise


async def scrape_reddit_topics(topics: List[str]) -> dict[str, dict]:
    """Process list of topics and return analysis results"""
    try:
        # Try MCP approach first
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await load_mcp_tools(session)
                model = get_groq_model()
                agent = create_react_agent(model, tools)
                
                reddit_results = {}
                for topic in topics:
                    try:
                        summary = await process_topic(agent, topic)
                        reddit_results[topic] = summary
                        await asyncio.sleep(5)
                    except Exception as e:
                        print(f"Error processing topic {topic}: {e}")
                        reddit_results[topic] = f"Error analyzing {topic}: {str(e)}"
                    
                return {"reddit_analysis": reddit_results}
                
    except Exception as e:
        print(f"MCP Reddit scraping failed: {e}")
        # Fallback to simple Groq analysis without MCP tools
        return await scrape_reddit_topics_fallback(topics)


async def scrape_reddit_topics_fallback(topics: List[str]) -> dict[str, dict]:
    """Fallback Reddit analysis using Groq API directly"""
    print("Using fallback Reddit analysis...")
    reddit_results = {}
    
    for topic in topics:
        try:
            model = get_groq_model()
            
            prompt = f"""You are a Reddit analysis expert. Provide a comprehensive analysis of recent Reddit discussions about '{topic}'.

Since I cannot access live Reddit data, please provide:
- What types of discussions would typically be happening about this topic on Reddit
- Common opinions and sentiment patterns you'd expect to find
- Key discussion points and trends
- Overall sentiment analysis (positive/neutral/negative)
- Sample of the kind of interesting quotes or comments that might appear (without usernames)

Make this analysis realistic and based on typical Reddit discussion patterns for this topic.

Topic to analyze: {topic}
Time frame: Recent discussions (last 2 weeks)
"""
            
            from langchain_core.messages import HumanMessage
            response = model.invoke([HumanMessage(content=prompt)])
            reddit_results[topic] = response.content
            
            await asyncio.sleep(2)  # Rate limiting
            
        except Exception as e:
            print(f"Error in fallback analysis for {topic}: {e}")
            reddit_results[topic] = f"Error analyzing {topic}: {str(e)}"
    
    return {"reddit_analysis": reddit_results}