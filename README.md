Here’s your fully updated project README, tailored for your new app name **NewsBlitz** and GitHub repo `Siddhantshetty/AI-Journalist`:


# **NewsBlitz – Lightning-Fast AI Journalist** ⚡

Your personal AI-powered news analyst that strikes fast — scraping headlines, reading Reddit reactions, and delivering rich audio briefings. *No scroll, no stress — just stories.*


### 🚀 FEATURES

* 🗞️ Scrapes premium news websites (bypasses paywalls like a pro)
* 🔍 Gathers real-time Reddit reactions (handles JS-heavy threads)
* 🧠 Summarizes content using advanced LLMs (Claude or GPT-based)
* 🔊 Converts summaries into natural audio with ElevenLabs
* ⚡ Real-time updates via Bright Data’s Model Context Protocol (MCP)


### 🧰 PREREQUISITES

* Python 3.9+
* [Bright Data](https://brightdata.com) account
* [ElevenLabs](https://elevenlabs.io) account


### ⚡ QUICK START

**1. Clone the Repo**

```bash
git clone https://github.com/Siddhantshetty/AI-Journalist.git
cd AI-Journalist
```

**2. Install Dependencies**

```bash
pipenv install
pipenv shell
```

**3. Configure Secrets**

```bash
cp .env.example .env
```

Then edit `.env`:

```env
# Bright Data
BRIGHTDATA_MCP_KEY="your_mcp_api_key"
BROWSER_AUTH="your_browser_auth_token"

# ElevenLabs 
ELEVENLABS_API_KEY="your_text_to_speech_key"
```

**4. Set Up Bright Data MCP**

* Create a new MCP zone at: [brightdata.com/cp/zones](https://brightdata.com/cp/zones)
* Enable browser emulation
* Copy keys into your `.env`


### 🧪 RUNNING NEWSBLITZ

**Terminal 1 – Backend**

```bash
pipenv run python backend.py
```

**Terminal 2 – Frontend**

```bash
pipenv run streamlit run frontend.py
```


### 📁 PROJECT STRUCTURE

```
.
├── frontend.py          # Streamlit interface
├── backend.py           # Main backend logic
├── utils.py             # Helper functions
├── news_scraper.py      # News scraper logic
├── reddit_scraper.py    # Reddit thread handler
├── models.py            # Pydantic data models
├── Pipfile              # Dependency manifest
├── .env.example         # Sample env config
└── requirements.txt     # Alternative deps
```


### 📝 NOTES

* First run might take 15–20 seconds as it fetches & processes content
* Reddit scraping uses real browser emulation (not simple HTTP)
* Keep your `.env` secure — *ninjas and journalists never reveal their sources*


### 📞 SUPPORT

* Open an issue: [GitHub Issues](https://github.com/Siddhantshetty/AI-Journalist/issues)
* Bright Data support: [brightdata.com/support](https://brightdata.com/support)


> *“In a world drowning in headlines, be the one who listens — fast.”* 📰⚡


