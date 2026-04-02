# 🚀 Quick Start Guide

## 1-Minute Setup

```bash
# Clone repo
cd /Users/leocherupushpam/Downloads/Competitive-Intelligence-Monitor

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 2-Minute First-Time Setup

1. **Go to Settings** → **Competitors**
   - Add a test competitor (e.g., "HubSpot", "https://www.hubspot.com")
   - Set threat level to "MEDIUM"

2. **Configure Data Sources** (Settings → Data Sources)
   - Website: `https://www.hubspot.com/pricing`
   - RSS Feed: `https://blog.hubspot.com/feed`
   - LinkedIn: `https://linkedin.com/company/hubspot`

3. **Trigger Data Collection**
   - Click "🔄 Trigger All Collectors Now" in sidebar
   - Watch as collectors gather data

4. **Review Intelligence Queue**
   - Go to Intelligence Queue page
   - You'll see auto-detected moves
   - Click **Validate** to confirm or **Dismiss** to filter

---

## Testing Workflows

### Test 1: Data Collection (5 min)
1. Settings → Click "Trigger All Collectors Now"
2. Settings → Logs & Status → View recent collection runs
3. Expected: See items_found > 0 for website/RSS/jobs collectors

### Test 2: PM Validation Workflow (5 min)
1. Intelligence Queue page
2. Review auto-detected moves (should show 3-5 for HubSpot)
3. Click **Validate** on a FEATURE move
4. Check that move now appears in "Validated Moves" section

### Test 3: Competitor Profile Deep Dive (3 min)
1. Competitor Profile page
2. Select "HubSpot"
3. Click through each tab:
   - Features & News (shows detected launches)
   - Pricing (shows pricing-related moves)
   - Positioning (shows brand/messaging changes)
   - Hiring Signals (shows job postings detected)

### Test 4: Executive Dashboard (3 min)
1. Market Dashboard page
2. View KPI chips at top
3. Check Threat Heat Map (should plot competitors)
4. Review "Recent Intel" table
5. Check Collection Health status

### Test 5: Roadmap Signals (3 min)
1. Roadmap Signals page
2. Paste sample features:
   ```
   AI email writer
   Advanced analytics
   Mobile app
   ```
3. Click "Save Roadmap"
4. Review signals generated from validated moves
5. Check recommended actions

### Test 6: Export (2 min)
1. Settings → "Export All Intelligence as CSV"
2. Download and open CSV in Excel/Google Sheets
3. Verify moves, dimensions, threat levels

---

## Common Issues & Fixes

### Issue: "ModuleNotFoundError: No module named 'streamlit'"
**Fix:** Activate venv and install requirements
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "No competitors to monitor" in data collectors
**Fix:** Add at least one competitor in Settings first

### Issue: NewsAPI returning empty results
**Fix:** Set NEWSAPI_KEY environment variable
```bash
export NEWSAPI_KEY=your-key-here
```
Or comment out news monitoring in background_jobs.py

### Issue: Playwright errors on first run
**Fix:** Download browser binaries
```bash
python -m playwright install
```

---

## Next Steps After Testing

1. **Add Real Competitors**
   - Use competitor_registry.py suggestions
   - Configure actual RSS feeds and pricing pages
   - Add OpenAI API key for AI analysis

2. **Configure Scheduled Collection**
   - Run background_jobs.py in a separate terminal
   - Or deploy to Streamlit Cloud (see README)

3. **Team Rollout**
   - Share app with PMs for validation workflow
   - Track metrics in Settings → Logs & Status
   - Export weekly intelligence reports as CSV

4. **Deploy to Streamlit Cloud**
   - Push code to GitHub
   - Connect GitHub repo to Streamlit Cloud
   - Set environment variables (OPENAI_API_KEY, NEWSAPI_KEY)
   - Share public URL with team

---

## Architecture Files Reference

| File | Purpose | Key Functions |
|------|---------|----------------|
| **db.py** | Database operations | `create_competitor()`, `log_move()`, `validate_move()` |
| **intelligence_engine.py** | AI analysis | `extract_move_from_raw_data()`, `analyze_roadmap_impact()` |
| **data_collectors/*.py** | Data collection | `monitor_competitor_websites()`, `monitor_rss_feeds()`, etc. |
| **background_jobs.py** | Scheduling | `start_scheduler()`, `trigger_manual_collection()` |
| **app.py** | Streamlit entry | Main app routing and KPI header |
| **pages/*.py** | UI pages | Intelligence Queue, Profiles, Dashboard, Settings |

---

## Cost Tracking

- **Database:** FREE (SQLite)
- **Data Collection:** FREE (all sources)
- **AI Analysis:** ~$0.03 per move (optional)
  - 100 moves/week × $0.03 = ~$12/month
  - With roadmap analysis: $20-50/month
- **Deployment:** FREE (Streamlit Cloud) or costs for VPS

**Total minimum cost: $0 (completely free if you skip AI)**

---

For more details, see README.md
