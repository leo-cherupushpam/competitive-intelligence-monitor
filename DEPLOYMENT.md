# 🚀 Deployment Guide

Deploy Competitive Intelligence Monitor to Streamlit Cloud in 5 minutes.

---

## Step 1: Create GitHub Repository

1. Go to [github.com/new](https://github.com/new)
2. Create a new repository named `competitive-intelligence-monitor`
3. Choose **Public** (unless you want private)
4. Click "Create repository"
5. Copy the repository URL (e.g., `https://github.com/YOUR-USERNAME/competitive-intelligence-monitor.git`)

---

## Step 2: Push Code to GitHub

From your local machine:

```bash
cd /Users/leocherupushpam/Downloads/Competitive-Intelligence-Monitor

# Add GitHub remote
git remote add origin https://github.com/YOUR-USERNAME/competitive-intelligence-monitor.git

# Verify remote is set
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main
```

**Verify:** Go to your GitHub repo URL and confirm all files are there.

---

## Step 3: Deploy to Streamlit Cloud

### 3a. Sign Up for Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "Sign in with GitHub"
3. Authorize Streamlit to access your GitHub repos

### 3b. Deploy the App
1. Click "Create app"
2. Select:
   - **Repository:** `YOUR-USERNAME/competitive-intelligence-monitor`
   - **Branch:** `main`
   - **Main file path:** `app.py`
3. Click "Deploy"

Streamlit will automatically:
- Clone your repo
- Install `requirements.txt`
- Run `streamlit run app.py`
- Assign you a public URL (e.g., `https://yourappname.streamlit.app`)

### 3c. Configure Secrets
1. Go to your app URL
2. Click the hamburger menu (☰) → "Settings"
3. Go to "Secrets" tab
4. Paste this and fill in your keys:

```toml
OPENAI_API_KEY = "sk-..."
NEWSAPI_KEY = "your-newsapi-key"
```

5. Click "Save"

The app will automatically restart with your secrets loaded.

---

## Step 4: Test Live Data Collection

Once deployed:

1. **Add a competitor** (Settings → Competitors)
   - Name: `HubSpot`
   - Website: `https://www.hubspot.com`
   - Threat: `MEDIUM`

2. **Configure data sources** (Settings → Data Sources)
   - Website URL: `https://www.hubspot.com/pricing`
   - RSS Feed: `https://blog.hubspot.com/feed`
   - LinkedIn: `https://linkedin.com/company/hubspot`

3. **Trigger first collection** (Sidebar → "🔄 Trigger All Collectors Now")
   - Website monitor will fetch HubSpot pricing page
   - RSS parser will fetch latest blog posts
   - Job board will check for hiring
   - NewsAPI will find recent news mentions

4. **Review results** (Intelligence Queue)
   - Auto-detected moves should appear
   - Validate/dismiss to confirm findings

5. **View dashboards**
   - Market Dashboard: See threat analysis
   - Competitor Profile: Deep dive into HubSpot
   - Roadmap Signals: Configure your features and see strategic alignment

---

## ⚠️ Important: Background Jobs on Streamlit Cloud

Streamlit Cloud **does not** support persistent background jobs (APScheduler won't run continuously).

### Option A: Manual Triggers (Recommended for MVP)
- Users click "🔄 Trigger All Collectors Now" in Settings
- Perfect for small teams, daily checks
- **Zero cost, no extra infrastructure needed**

### Option B: External Scheduler (Production)
For automated collection without manual triggers:

**Use AWS Lambda + EventBridge (FREE tier eligible):**

1. Create Lambda function with your collector code
2. Set up EventBridge rule (daily at 2am UTC)
3. Lambda runs collectors, stores to database
4. Streamlit Cloud reads from database

**Or use: GitHub Actions (FREE)**

Create `.github/workflows/collect.yml`:

```yaml
name: Data Collection
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2am UTC
jobs:
  collect:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run collectors
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          NEWSAPI_KEY: ${{ secrets.NEWSAPI_KEY }}
        run: python -c "
          from background_jobs import trigger_all_collectors
          trigger_all_collectors()
        "
```

Then add secrets to GitHub repo (Settings → Secrets and variables → Actions)

---

## 🔧 Local Testing Before Deployment

Test everything works locally first:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env
# Edit .env with your API keys

# 3. Run app
streamlit run app.py

# 4. Open http://localhost:8501
# 5. Test workflows from QUICK_START.md
```

---

## 📊 Live Data Collection on Deployed App

Once deployed, here's what happens:

### When User Clicks "Trigger All Collectors Now":

```
1. Website Monitor (Playwright)
   ├─ Fetches competitor pricing/features pages
   ├─ Hash-based diff detection (5% threshold)
   └─ Stores raw HTML to raw_competitive_data

2. RSS Parser (feedparser)
   ├─ Fetches RSS feeds for all competitors
   ├─ Extracts 10 latest blog posts
   └─ Detects duplicates (skip if seen in 30 days)

3. Product Hunt API
   ├─ Searches for competitor launches
   └─ Stores to raw_competitive_data

4. Job Board Monitor (LinkedIn)
   ├─ Scrapes LinkedIn public job listings
   ├─ Analyzes job titles for product signals
   └─ Detects hiring in: AI/ML, Platform, Mobile, Security, etc.

5. News Monitor (NewsAPI)
   ├─ Searches news for competitor mentions
   ├─ Detects: M&A, funding, partnerships, leadership
   └─ Respects 1,000/month free tier quota

6. Intelligence Engine (OpenAI - optional)
   ├─ Analyzes each raw_competitive_data entry
   ├─ Extracts: title, threat_level, dimension, confidence
   └─ Creates competitive_move records for PM validation

7. PM Validation Queue
   ├─ User reviews auto-detected moves
   ├─ Validates or dismisses (trains system)
   └─ Reduces noise over time
```

### Data Flow:
```
Raw Data Sources → raw_competitive_data → Intelligence Engine → competitive_moves → PM Validation
                   ↓
            data_collection_log (for monitoring)
```

---

## 💾 Database Notes

On Streamlit Cloud:
- **Default:** SQLite stored in `/tmp/` (ephemeral - data lost on redeploy)
- **Recommended for production:** Use PostgreSQL or external database

### Upgrade to PostgreSQL:

1. Create Heroku PostgreSQL database (or any Postgres provider)
2. Update `db.py` to use PostgreSQL instead of SQLite
3. Set `DATABASE_URL` environment variable in Streamlit Cloud secrets
4. Redeploy

For now, SQLite is fine for MVP - just know data resets on redeploy.

---

## 🎯 Deployment Checklist

- [ ] GitHub repo created
- [ ] Code pushed to GitHub (`git push origin main`)
- [ ] Streamlit Cloud app deployed
- [ ] API keys configured in Streamlit Cloud secrets
- [ ] App loads at public URL
- [ ] First competitor added (Settings)
- [ ] Data sources configured (Settings)
- [ ] Collectors triggered successfully
- [ ] Moves appear in Intelligence Queue
- [ ] PMs can validate/dismiss moves
- [ ] Market Dashboard shows threat data
- [ ] Team can access app URL

---

## 🆘 Troubleshooting

### App crashes on load
- Check Streamlit logs (View logs in Streamlit Cloud)
- Verify all imports work: `python -c "import streamlit; import openai; import playwright"`
- Check `requirements.txt` has all dependencies

### Data collection fails
- Verify API keys in Streamlit Cloud secrets
- Check NewsAPI quota (free tier: 1,000/month)
- Website monitor needs Playwright: `pip install playwright && python -m playwright install`

### Database errors
- SQLite on Streamlit Cloud is ephemeral
- Data resets on redeploy
- For persistence, use PostgreSQL (see upgrade section)

### "No competitors to monitor"
- Add at least one competitor in Settings
- Configure data sources for that competitor
- Click "Trigger All Collectors Now"

---

## 📈 Production Readiness

Current MVP features:
- ✅ Live data collection from 5 FREE sources
- ✅ Real-time Streamlit UI
- ✅ PM validation workflow
- ✅ Executive dashboards
- ✅ Strategic roadmap alignment

For production scaling:
- [ ] Migrate SQLite to PostgreSQL
- [ ] Set up external scheduler (GitHub Actions or Lambda)
- [ ] Add Slack/email alerts for HIGH threats
- [ ] Implement team authentication
- [ ] Add audit logging for all validations
- [ ] Set up monitoring/alerting for collector failures

---

## 🔗 Useful Links

- **Streamlit Cloud:** https://share.streamlit.io
- **GitHub:** https://github.com
- **OpenAI API:** https://platform.openai.com/account/api-keys
- **NewsAPI:** https://newsapi.org
- **Heroku Postgres:** https://www.heroku.com/postgres (for persistent database)

---

**Estimated time to live deployment: 5-10 minutes**

Enjoy your competitive intelligence platform! 🎯
