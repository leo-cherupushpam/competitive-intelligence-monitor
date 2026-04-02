# 🚀 DEPLOY TO STREAMLIT CLOUD — 5 MINUTE SETUP

**Everything is ready. Follow these 5 steps to go live with real data collection.**

---

## ✅ Step 1: Create GitHub Repository (2 min)

1. Go to https://github.com/new
2. Name it: `competitive-intelligence-monitor`
3. Description: "Real-time competitive intelligence platform"
4. Choose **Public** (for Streamlit Cloud free tier)
5. **DO NOT** initialize with README (we have one)
6. Click **Create repository**
7. You'll see: "…or push an existing repository from the command line"
8. Copy that command (looks like `git remote add origin https://github.com/YOUR-USERNAME/competitive-intelligence-monitor.git`)

---

## ✅ Step 2: Push Code to GitHub (2 min)

Paste and run in terminal:

```bash
cd /Users/leocherupushpam/Downloads/Competitive-Intelligence-Monitor

# Add GitHub remote (replace YOUR-USERNAME with your actual username)
git remote add origin https://github.com/YOUR-USERNAME/competitive-intelligence-monitor.git

# Verify it worked
git remote -v

# Push code to GitHub
git branch -M main
git push -u origin main
```

**Expected output:**
```
Enumerating objects: 25, done.
...
To https://github.com/YOUR-USERNAME/competitive-intelligence-monitor.git
 * [new branch]      main -> main
```

✅ **Verify:** Go to `https://github.com/YOUR-USERNAME/competitive-intelligence-monitor` and see all your files there.

---

## ✅ Step 3: Deploy to Streamlit Cloud (1 min)

1. Go to https://share.streamlit.io
2. Click **"Sign in with GitHub"** (authorize if prompted)
3. Click **"Create app"**
4. Fill in:
   - **Repository:** `YOUR-USERNAME/competitive-intelligence-monitor`
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Click **"Deploy"**

**Wait 30-60 seconds** for Streamlit to build and deploy.

✅ **You'll get a public URL** like: `https://competitive-intelligence-monitor-abc123.streamlit.app`

---

## ✅ Step 4: Configure API Keys (1 min)

1. In your Streamlit app, click **☰ menu** (top right)
2. Go to **"Settings"**
3. Click **"Secrets"** tab
4. Paste this (fill in your keys):

```toml
OPENAI_API_KEY = "sk-your-api-key-here"
NEWSAPI_KEY = "your-newsapi-key-here"
```

5. Click **"Save"**

**Note:** You can get free API keys:
- **OpenAI:** https://platform.openai.com/account/api-keys (pay-as-you-go, ~$0.03 per move)
- **NewsAPI:** https://newsapi.org (free tier: 1,000 requests/month)

**If you don't have these keys yet:** Leave them blank for now. The app works 100% without them (just won't do AI analysis). You can add keys later.

5. App restarts automatically ✅

---

## ✅ Step 5: Test Live Data Collection (1 min)

1. **Open your live app** at the public URL
2. Go to **Settings** → **Competitors** → **Add New Competitor**
   - Name: `HubSpot`
   - Website: `https://www.hubspot.com`
   - Threat: `MEDIUM`
   - Click **➕ Add Competitor**

3. Go to **Settings** → **Data Sources**
   - Select: `HubSpot`
   - Website Pricing page: `https://www.hubspot.com/pricing`
   - RSS Feed: `https://blog.hubspot.com/feed`
   - LinkedIn: `https://linkedin.com/company/hubspot`
   - Click **Register** buttons

4. **Sidebar** → Click **🔄 Trigger All Collectors Now**
   - Wait 30 seconds...
   - You'll see: "✓ Data collection triggered!"

5. Go to **Intelligence Queue**
   - 🎉 You should see 3-5 auto-detected moves!
   - These are REAL data from HubSpot website, RSS, and news APIs

6. Click **✅ Validate** on a move to confirm it

7. Go to **Market Dashboard** → See threat analysis
   - Threat Heat Map now shows HubSpot
   - Recent Intel shows all detected moves

8. Go to **Competitor Profile** → Select HubSpot
   - See Features, Pricing, Positioning, Hiring tabs
   - All populated with real live data!

---

## 📊 What Just Happened

Your app is now:
- ✅ **Live at public URL** (shareable with team)
- ✅ **Collecting real data** from:
  - HubSpot website (pricing page via Playwright)
  - HubSpot RSS feed (blog posts)
  - HubSpot news mentions (from NewsAPI)
  - HubSpot job postings (from LinkedIn)
- ✅ **Auto-analyzing** with AI (if keys configured)
- ✅ **Ready for PM validation** (Intelligence Queue workflow)
- ✅ **Showing executive dashboards** (threat analysis, recent intel)

---

## 🔄 Automated Data Collection (Optional)

Your GitHub repo includes `.github/workflows/collect-data.yml` which can automatically:
- Run website monitoring daily at 2am UTC
- Run RSS parsing every 6 hours
- Run job board monitoring bi-weekly
- Run news monitoring daily

To enable:
1. Go to your GitHub repo
2. Go to **Settings** → **Secrets and variables** → **Actions**
3. Add these secrets:
   - `OPENAI_API_KEY` = your OpenAI key
   - `NEWSAPI_KEY` = your NewsAPI key

GitHub Actions will then automatically run collectors on schedule (completely free, included with GitHub).

---

## 📈 Next Steps

### Immediate (This week)
- [ ] Share app URL with 2-3 PMs
- [ ] Have them test Intelligence Queue workflow
- [ ] Add 2-3 real competitors (from competitor_registry.py)
- [ ] Configure all their data sources

### Short-term (This month)
- [ ] PMs validate/dismiss moves daily (reduces noise)
- [ ] Track metrics in Settings → Logs & Status
- [ ] Configure Slack alerts for HIGH threats
- [ ] Export weekly competitive brief as CSV

### Production (Next quarter)
- [ ] Migrate database to PostgreSQL (for data persistence)
- [ ] Set up team authentication
- [ ] Implement Slack/email alerts
- [ ] Integrate with roadmap tool (Linear, Jira, etc.)

---

## ✅ Final Checklist

- [ ] GitHub repo created
- [ ] Code pushed to GitHub
- [ ] Streamlit Cloud app deployed
- [ ] Live URL obtained
- [ ] API keys configured (or skipped for now)
- [ ] First competitor added
- [ ] Data sources configured
- [ ] Data collection triggered
- [ ] Moves appear in Intelligence Queue
- [ ] Dashboards showing real data
- [ ] Ready to share with team

---

## 🆘 Quick Troubleshooting

**"App won't load"**
- Check Streamlit Cloud logs (View logs button)
- Verify all Python imports work locally

**"No moves found after trigger"**
- Check Settings → Logs & Status for errors
- Verify competitor and data sources are configured
- Try again in 30 seconds

**"AI analysis not working"**
- Check that OPENAI_API_KEY is in Streamlit Cloud secrets (not just locally)
- Verify API key is valid at https://platform.openai.com

**"NewsAPI not finding articles"**
- Check NewsAPI quota at Settings → Logs & Status
- Verify NEWSAPI_KEY is configured

---

**🎉 You're live! Your competitive intelligence platform is now running with real, live data.**

Share the app URL with your team and start validating competitive moves in the Intelligence Queue.

See **DEPLOYMENT.md** for more detailed info, production scaling, and database persistence options.
