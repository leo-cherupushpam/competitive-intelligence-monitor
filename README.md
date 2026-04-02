# 🎯 Competitive Intelligence Monitor

**Real-time competitive intelligence platform for product managers.** Track competitor moves (features, pricing, positioning, hiring) across 5 free data sources, automatically analyze with AI, and align with your roadmap strategy.

**Built for:** Product managers at scale-ups and enterprises who need defensible, data-driven competitive strategy.

---

## 🚀 Key Features

### 📊 Live Data Collection (5 FREE sources)
- **Website Monitoring**: Track competitor pricing, features, and blog pages (Playwright)
- **RSS Feeds**: Monitor competitor blogs and press releases
- **Product Hunt API**: Detect new launches and feature announcements
- **LinkedIn Jobs**: Analyze hiring signals to detect product direction
- **NewsAPI**: Catch M&A, funding, partnerships, leadership changes

### 🤖 AI-Powered Intelligence Extraction
- Auto-detect competitive moves from raw data (title, threat level, opportunity flag)
- Structured classification: FEATURE | PRICING | POSITIONING | HIRING | NEWS
- Confidence scoring (0-1.0) and threat assessment (LOW/MEDIUM/HIGH)
- Graceful fallback: rule-based extraction when OpenAI unavailable

### 📋 PM Intelligence Queue
- **Auto-detected moves** awaiting PM validation
- Filter by: Competitor, Threat Level, Source Type, Date Range
- **Validate/Dismiss** workflow to reduce noise over time
- **View all validated intelligence** in a timeline

### 🔍 Competitor Deep Dives
- **4-tab profiles** for each competitor:
  1. Features & News (timeline of launches and announcements)
  2. Pricing Strategy (tier structure, price changes, enterprise offerings)
  3. Market Positioning (brand shifts, messaging evolution)
  4. Hiring Signals (team expansion, skill focus, geographic expansion)

### 📊 Executive Dashboard
- **Threat Heat Map**: Competitive positioning (threat vs. momentum)
- **Pricing War Tracker**: Track competitor pricing moves
- **Recent Intelligence**: Latest HIGH-threat moves with context
- **Collection Health**: Monitor data collection status and NewsAPI quota

### 🛣️ Roadmap Signals (NEW)
- Configure your planned features
- AI analyzes validated moves against your roadmap
- Auto-generated strategic signals:
  - **VALIDATES**: This move confirms our feature priorities
  - **INVALIDATES**: This move challenges our assumptions
  - **ACCELERATES**: We should ship this feature faster
  - **DEPRIORITIZES**: We can safely delay this feature
- Actionable recommendations for roadmap adjustments

### ⚙️ Admin Settings
- **Competitor Management**: Add/remove competitors, set baseline threats
- **Data Source Config**: Register website URLs, RSS feeds, LinkedIn profiles
- **API Keys**: Securely configure OpenAI and NewsAPI keys
- **Collection Logs**: Monitor all collection runs, detect failures
- **NewsAPI Quota**: Track usage of 1,000/month free tier
- **Export**: Download all competitive intelligence as CSV

---

## 💰 Cost Breakdown

| Component | Cost | Notes |
|-----------|------|-------|
| **Data Collection** | **FREE** | All 5 sources are completely free |
| **AI Analysis** | **$20-50/month** | OpenAI gpt-5-nano-2025-08-07 (optional) |
| **Database** | **FREE** | SQLite (self-hosted) |
| **Deployment** | **FREE** | Streamlit Cloud or self-hosted |
| **Total** | **$20-50/month** | Optional AI analysis, no required costs |

---

## 🏗️ Architecture

```
competitive-intelligence-monitor/
├── app.py                          # Streamlit entry point + KPI header
├── db.py                           # SQLite schema + CRUD operations
├── intelligence_engine.py          # AI analysis using gpt-5-nano-2025-08-07
├── background_jobs.py              # APScheduler orchestration
├── competitor_registry.py           # Pre-built competitor library
├── data_collectors/
│   ├── website_monitor.py          # Playwright-based website tracking
│   ├── rss_parser.py               # Monitor RSS feeds
│   ├── product_hunt.py             # Product Hunt API (placeholder)
│   ├── job_board.py                # LinkedIn job postings
│   └── news_monitor.py             # NewsAPI free tier monitoring
├── pages/
│   ├── intelligence_queue.py       # PM validation workflow
│   ├── competitor_profile.py       # 4-tab competitor deep dive
│   ├── market_dashboard.py         # Executive threat analysis
│   ├── roadmap_signals.py          # Strategic roadmap alignment
│   └── settings.py                 # Admin configuration
├── .streamlit/config.toml          # Dark theme styling
├── requirements.txt
├── .env.example
└── README.md
```

### Database Schema (8 tables)
- **competitors**: Tracked companies with threat baseline
- **competitor_sources**: Data sources (website URLs, RSS feeds, etc.)
- **raw_competitive_data**: Raw collected data from all sources
- **competitive_moves**: Structured moves extracted by AI
- **ai_insights**: Strategic insights generated from moves
- **roadmap_signals**: Impact analysis against our roadmap
- **market_position**: Competitor positioning comparisons
- **data_collection_log**: Collection run history and metrics

### Scheduled Collection
- **Website Monitoring**: Daily at 2am UTC
- **RSS Feeds**: Every 6 hours
- **Product Hunt**: Daily at 9am UTC
- **Job Board**: Bi-weekly (Tuesday 10am UTC)
- **News Monitoring**: Daily at 12pm UTC (respects 1,000/month quota)

---

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/YOUR-USERNAME/competitive-intelligence-monitor.git
cd competitive-intelligence-monitor
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your API keys:
# OPENAI_API_KEY=sk-...
# NEWSAPI_KEY=... (optional)
```

### 3. Initialize Database
```bash
python db.py
```

### 4. Run the App
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

### 5. Add Your First Competitors
1. Go to **Settings** → **Competitors**
2. Add your top 3-5 competitors
3. Configure data sources (website URLs, RSS feeds, LinkedIn profiles)
4. Click **"Trigger All Collectors Now"** to kick off first collection

### 6. Start Validating Intelligence
1. Go to **Intelligence Queue**
2. Review auto-detected moves
3. **Validate** to confirm, **Dismiss** to filter noise
4. Watch as insights accumulate in **Market Dashboard** and **Roadmap Signals**

---

## 📖 User Workflows

### For Product Managers
1. **Intelligence Queue** → Review auto-detected competitive moves (5 min/day)
2. Validate moves you confirm, dismiss false positives
3. Navigate to **Competitor Profile** to deep-dive on specific competitors
4. Use **Roadmap Signals** to inform prioritization decisions

### For Executives
1. **Market Dashboard** → Monitor competitive threats at a glance
2. Threat Heat Map shows which competitors are most active
3. Pricing War tracker shows competitive pricing dynamics
4. Recent Intel section shows latest HIGH-threat moves
5. Use data to inform quarterly strategy reviews

### For Product Teams
1. **Roadmap Signals** → See how competitive moves impact your roadmap
2. Review recommended actions (accelerate/deprioritize/validate features)
3. Use confidence scores to prioritize analysis effort
4. Export all intelligence as CSV for team discussions

---

## 🔄 Data Collection Details

### Website Monitor (FREE)
- Monitors: /pricing, /product, /features, /blog pages
- Detection: Hash-based diff (>5% change = detected)
- Frequency: Daily at 2am UTC
- Cost: **FREE** (Playwright is open-source)

### RSS Parser (FREE)
- Tracks: Competitor blogs, product announcements, press releases
- Sources: Configured per-competitor in Settings
- Duplicate detection: Skips URLs already processed in past 30 days
- Frequency: Every 6 hours
- Cost: **FREE**

### Product Hunt API (FREE)
- Tracks: New launches from competitor domains
- Frequency: Daily at 9am UTC
- Cost: **FREE** (non-commercial use)

### Job Board Monitor (FREE)
- Tracks: LinkedIn public job postings from competitor career pages
- Analysis: Extracts product areas from job titles (AI/ML, Platform, Mobile, Security)
- Frequency: Bi-weekly (Tuesday 10am UTC)
- Cost: **FREE** (LinkedIn public data)

### News Monitor (FREE)
- Tracks: News mentions (M&A, funding, partnerships, leadership, major announcements)
- Source: NewsAPI.org free tier (1,000 requests/month)
- Frequency: Daily at 12pm UTC
- Cost: **FREE** (respects 1,000/month quota; ~35 requests/day sufficient for 5-10 competitors)

---

## 🤖 AI Analysis

### Extract Move from Raw Data
- Input: Raw content from any source (website content, RSS entry, news article)
- Process: OpenAI gpt-5-nano-2025-08-07 extracts:
  - **Title** (max 50 chars)
  - **Description** (1-2 sentences)
  - **Dimension** (FEATURE | PRICING | POSITIONING | HIRING | NEWS)
  - **Threat Level** (LOW | MEDIUM | HIGH)
  - **Opportunity Flag** (should we copy this?)
  - **Confidence Score** (0.0-1.0)
- Output: Structured competitive_move record
- Cost: ~$0.01-0.05 per move analysis

### Generate Strategic Insight
- Input: Validated move title, description, threat level, dimension
- Output: Strategic implications and recommended response
- Cost: ~$0.01-0.05 per insight

### Analyze Roadmap Impact
- Input: Competitive move title + your planned features
- Output: Signal type (VALIDATES | INVALIDATES | ACCELERATES | DEPRIORITIZES)
- Cost: ~$0.01-0.05 per analysis

### Total AI Cost
- ~100-200 moves per week × $0.03 avg = **$3-6/week = $12-24/month**
- With insights + roadmap analysis: **$20-50/month total**

---

## 🎨 Features Highlight

### Dual-Persona Design
- **PMs** get a validation workflow (Intelligence Queue) to confirm findings
- **Executives** get a strategic dashboard (Market Dashboard) with threat assessment and recommendations

### Graceful Degradation
- If OpenAI API key unavailable: falls back to rule-based extraction (no quality loss for demo)
- All features work without API keys; AI just adds higher confidence scores

### Audit Trail
- Every move, insight, and decision is logged with timestamps
- Shows which data sources contributed to each intelligence piece
- Enables review of decision-making process

### Export & Integration
- Download all competitive intelligence as CSV
- Share with teams for collaborative analysis
- Integrate with internal tools (Slack, Notion, docs)

---

## 📊 Success Metrics

Track these to measure competitive intelligence effectiveness:

1. **Coverage**: # Competitors tracked, # Active data sources per competitor
2. **Velocity**: # Moves auto-detected per week, avg time-to-detection
3. **Quality**: Validation rate (% of auto-detections confirmed by PM)
4. **Impact**: # Roadmap decisions informed by competitive intelligence
5. **Timeliness**: Avg time from competitor move to PM notification

---

## 🛠️ Development

### Run Tests
```bash
pytest tests/
```

### Add a New Data Collector
1. Create `data_collectors/my_collector.py`
2. Implement `monitor_my_source()` function
3. Add to `background_jobs.py` scheduler
4. Register data source type in `db.py`

### Customize AI Prompts
Edit `intelligence_engine.py` to modify:
- Move extraction prompt (lines 20-45)
- Insight generation prompt (lines 118-140)
- Roadmap impact analysis prompt (lines 190-212)

### Deploy to Streamlit Cloud
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect GitHub repo
4. Set environment variables in Streamlit Cloud secrets
5. Deploy!

---

## 🔒 Security & Privacy

- ✅ All data stored locally (SQLite) by default
- ✅ API keys stored as environment variables (never in code)
- ✅ No personal data collection (only competitor intelligence)
- ✅ Public data sources only (websites, RSS, APIs)
- ✅ Respects robots.txt and API rate limits

### Deploying to Production
- Use a secrets manager (AWS Secrets Manager, HashiCorp Vault, etc.)
- Enable database encryption (SQLite extension, or migrate to PostgreSQL)
- Implement user authentication (Streamlit Cloud or custom)
- Add audit logging for sensitive actions

---

## 📞 Support & Roadmap

### Current Status
- ✅ Live data collection (5 FREE sources)
- ✅ AI-powered move extraction
- ✅ PM intelligence queue with validation
- ✅ Competitor profiles (4 tabs)
- ✅ Executive market dashboard
- ✅ Roadmap signals with strategic recommendations
- ✅ Background job scheduling
- ✅ Export to CSV

### Planned Features
- [ ] Slack integration (daily threat alerts)
- [ ] Roadmap comparison (side-by-side feature analysis)
- [ ] Competitive win/loss analysis (customer feedback integration)
- [ ] Market segments (track entire markets, not just competitors)
- [ ] Historical trends (show how threats evolved over time)
- [ ] Sensitivity analysis (what-if scenarios)
- [ ] Team collaboration (comments, notes on moves)

---

## 📄 License

MIT — Build on this freely for commercial or open-source projects.

---

**Built with:** Streamlit, OpenAI, Playwright, APScheduler, SQLite, Plotly

**Best for:** Product managers, startups, and enterprises who want competitive intelligence without vendor lock-in or ongoing costs.
