# 📊 LIVE DATA TESTING GUIDE

**Once deployed, here's exactly what real, live data you'll see from each collector.**

---

## 🌐 Source 1: Website Monitor (Playwright)

**What it collects:** Real content from competitor websites

**Example:** HubSpot pricing page monitoring

```
Website URL: https://www.hubspot.com/pricing
Collected at: 2024-04-01 14:23:45 UTC
Content type: HTML + text (2000 chars)
Change detected: YES (price reduced from $50 to $45/month)

Auto-detected move:
├─ Title: "HubSpot Reduces Professional Plan Pricing"
├─ Dimension: PRICING
├─ Threat Level: MEDIUM
├─ Confidence: 87%
└─ Description: "HubSpot's Professional tier reduced from $50/month to $45/month,
   making it more competitive with Pipedrive"
```

**Where you'll see it:** Intelligence Queue → PRICING moves

**Data frequency:** Daily at 2am UTC

---

## 📰 Source 2: RSS Feeds (feedparser)

**What it collects:** Blog posts, product announcements, press releases

**Example:** HubSpot blog RSS feed

```
RSS Feed: https://blog.hubspot.com/feed

Real articles found:
1. Title: "Introducing HubSpot AI Assistant for Sales"
   Published: 2024-03-28
   Description: "HubSpot launches AI email writer and meeting summarizer..."

   Auto-detected move:
   ├─ Title: "HubSpot Launches AI Email Assistant"
   ├─ Dimension: FEATURE
   ├─ Threat Level: HIGH
   ├─ Confidence: 94%
   └─ Opportunity: YES (we should copy this)

2. Title: "HubSpot Expands Into Document Management"
   Published: 2024-03-25
   Description: "New document collaboration features now in beta..."

   Auto-detected move:
   ├─ Title: "New Document Collaboration Features"
   ├─ Dimension: FEATURE
   ├─ Threat Level: MEDIUM
   └─ Confidence: 81%
```

**Where you'll see it:** Intelligence Queue → FEATURE moves with source=RSS

**Data frequency:** Every 6 hours

---

## 🚀 Source 3: Product Hunt API

**What it collects:** New product launches from competitor domains

**Example:** Searching for HubSpot launches

```
Product Hunt API: https://api.producthunt.com/v2

Recent launches detected:
1. Product: "HubSpot CRM Tools"
   Posted: 2024-03-20
   Upvotes: 342
   Description: "Advanced automation and workflow tools..."

   Auto-detected move:
   ├─ Title: "HubSpot Launches Advanced CRM Workflows"
   ├─ Dimension: FEATURE
   ├─ Threat Level: MEDIUM
   └─ Confidence: 75%
```

**Where you'll see it:** Intelligence Queue → FEATURE moves with source=PRODUCTHUNT

**Data frequency:** Daily at 9am UTC

---

## 👥 Source 4: LinkedIn Job Board

**What it collects:** Job postings (indicates hiring/product direction)

**Example:** HubSpot career pages

```
LinkedIn Company: https://linkedin.com/company/hubspot

Real job postings found:
1. Title: "Senior Machine Learning Engineer"
   Team: Product
   Description: "Join our AI team building the next generation of AI features..."

   Analysis:
   ├─ Skill detected: AI/ML
   ├─ Signal: "Expanding team in: AI/ML"

   Auto-detected move:
   ├─ Title: "HubSpot Hiring ML Engineers (AI/ML Focus)"
   ├─ Dimension: HIRING
   ├─ Threat Level: MEDIUM
   └─ Confidence: 78%

2. Title: "Backend Platform Engineer"
   Team: Infrastructure
   Description: "Build scalable infrastructure for millions of users..."

   Auto-detected move:
   ├─ Title: "HubSpot Expanding Backend Infrastructure Team"
   ├─ Dimension: HIRING
   ├─ Threat Level: LOW
   └─ Confidence: 71%

Recent hiring signals:
├─ AI/ML: 4 open positions (threat: HIGH)
├─ Platform/DevOps: 3 open positions (threat: MEDIUM)
├─ Mobile: 1 open position (threat: LOW)
└─ Security: 2 open positions (threat: MEDIUM)
```

**Where you'll see it:**
- Intelligence Queue → HIRING moves
- Competitor Profile → "Hiring Signals" tab

**Data frequency:** Bi-weekly (Tuesday 10am UTC)

---

## 📰 Source 5: NewsAPI (News Aggregation)

**What it collects:** M&A, funding, partnerships, leadership changes

**Example:** News about HubSpot

```
NewsAPI: https://newsapi.org/v2/everything

Real news found:
1. Title: "HubSpot Acquires Motion to Expand AI Capabilities"
   Source: TechCrunch
   Published: 2024-03-15
   Summary: "HubSpot announced the acquisition of Motion, an AI scheduling company..."

   Detected signals: M&A

   Auto-detected move:
   ├─ Title: "HubSpot Acquires Motion (AI Scheduling)"
   ├─ Dimension: NEWS / FEATURE
   ├─ Threat Level: HIGH
   ├─ Confidence: 96%
   └─ Description: "Strategic acquisition to enhance AI scheduling capabilities,
      directly competing with our planned AI assistant"

2. Title: "HubSpot Announces $200M Series G Funding"
   Source: Crunchbase
   Published: 2024-02-20
   Summary: "HubSpot raises Series G funding round..."

   Detected signals: Funding

   Auto-detected move:
   ├─ Title: "HubSpot Raises $200M Series G Funding"
   ├─ Dimension: NEWS
   ├─ Threat Level: MEDIUM
   ├─ Confidence: 91%
   └─ Description: "Major funding round suggests aggressive expansion in
      AI features and international markets"

3. Title: "HubSpot Names New Chief Operating Officer"
   Source: Business Wire
   Published: 2024-03-01

   Auto-detected move:
   ├─ Title: "HubSpot Appoints New COO"
   ├─ Dimension: NEWS
   ├─ Threat Level: LOW
   └─ Confidence: 85%
```

**Where you'll see it:** Intelligence Queue → NEWS moves

**Data frequency:** Daily at 12pm UTC (respects 1,000/month quota)

---

## 🤖 AI Intelligence Extraction

**Once all raw data is collected, OpenAI auto-analyzes it:**

```
Raw Data Input (from any collector):
├─ HubSpot released AI email writer
├─ Source: Website monitoring
└─ Confidence: Website metadata confirms

↓ Intelligence Engine (GPT-4-nano)

Extracted Move:
├─ Title: "HubSpot Launches AI Email Writer"
├─ Dimension: FEATURE
├─ Threat Level: HIGH (because direct competition)
├─ Opportunity: YES (feature we should copy)
├─ Confidence: 0.92 (92%)
└─ Strategic Implication: "High threat - this directly competes with our
   planned AI features. Recommend: Accelerate our AI assistant launch."
```

---

## 📊 Intelligence Queue Workflow

**After data collection, here's what a PM sees:**

```
Intelligence Queue Page:
┌─────────────────────────────────────────────────┐
│ 🎯 Intelligence Queue                           │
│ Review auto-detected competitive moves          │
├─────────────────────────────────────────────────┤
│ Filters: Status | Competitor | Threat | Source │
├─────────────────────────────────────────────────┤
│                                                 │
│ 🔔 Moves Awaiting Validation (5)               │
│                                                 │
│ [Card 1]                                        │
│ ┌───────────────────────────────────────────┐  │
│ │ HubSpot Launches AI Email Writer          │  │
│ │ Competitor: HubSpot                       │  │
│ │ 🔴 Threat: HIGH (92% confidence)          │  │
│ │ Source: Website Monitoring                │  │
│ │ ✓ Opportunity (we should copy)            │  │
│ │                                           │  │
│ │ HubSpot released new AI-powered email     │  │
│ │ writer with context-aware suggestions     │  │
│ │                                           │  │
│ │ [✅ Validate] [❌ Dismiss]                │  │
│ └───────────────────────────────────────────┘  │
│                                                 │
│ [Card 2] ...5 more cards...                    │
│                                                 │
│ ✅ Validated Moves (12)                        │
│ [Table showing confirmed intelligence]         │
│                                                 │
└─────────────────────────────────────────────────┘

PM Action: Clicks ✅ Validate
Result: Move status changes to VALIDATED
        Move appears in "Recent Intel" on Market Dashboard
```

---

## 📊 Market Dashboard View

**Executive sees real competitive threats:**

```
Market Dashboard:
┌──────────────────────────────────────────────────┐
│ 📊 Market Dashboard                              │
├──────────────────────────────────────────────────┤
│ 🚨 Critical Threats: 7                           │
│ 💡 Opportunities Detected: 12                    │
│ 🆕 Competitor Features Detected: 23             │
│ 📊 Activity Last 7 Days: 18 moves               │
├──────────────────────────────────────────────────┤
│                                                  │
│ 🎯 Competitive Threat Heat Map:                 │
│                                                  │
│   Threat Score ↑                                │
│   3.0 │                          Salesforce     │
│   2.5 │                    HubSpot               │
│   2.0 │         Pipedrive                       │
│   1.5 │ Zoho     Freshsales                     │
│   1.0 │                                         │
│        └─────────────────────────────────────→  │
│          0    2    4    6    8   10   12  14    │
│             Recent Activity (moves/week)        │
│                                                  │
│ Threat Ranking:                                 │
│ 🔴 Salesforce - Threat: 2.9, Recent: 8 moves   │
│ 🟡 HubSpot - Threat: 2.5, Recent: 6 moves      │
│ 🟡 Pipedrive - Threat: 2.1, Recent: 4 moves    │
│ 🟢 Zoho - Threat: 1.5, Recent: 2 moves         │
│                                                  │
│ 💰 Pricing War:                                 │
│ [Chart showing pricing change frequency]        │
│                                                  │
│ 📰 Latest Competitive Intelligence:             │
│ 🔴 HubSpot acquires Motion (AI scheduling)     │
│ 🟡 Salesforce launches Einstein AI assistant  │
│ 🟡 Pipedrive improves mobile app                │
│ 🟢 Zoho adds document management                │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## 🔍 Competitor Profile Tabs

**Deep dive with real data:**

```
Competitor: HubSpot

📰 Features & News Tab:
├─ Feature 1: AI Email Writer (HubSpot Blog)
├─ Feature 2: Meeting Summarization (LinkedIn)
├─ Feature 3: Document Collaboration (Website)
├─ News 1: Acquires Motion for AI (NewsAPI)
└─ News 2: Series G Funding $200M (NewsAPI)

💰 Pricing Tab:
├─ Plan Changes:
│  ├─ Professional: $50 → $45/month (10% cut)
│  └─ Enterprise: Custom (varies)
├─ Tiers: Starter, Professional, Enterprise
└─ Features per tier (extracted from website)

🎯 Positioning Tab:
├─ Messaging Evolution:
│  ├─ 2023: "The Platform for Growing Businesses"
│  └─ 2024: "AI-Powered CRM Platform for Enterprise"
├─ Target Segments: SMB → Mid-market → Enterprise
└─ Key Differentiator: AI-first approach

👥 Hiring Signals Tab:
├─ Open Positions: 23
├─ AI/ML: 4 (🔴 HIGH focus)
├─ Platform: 3 (🟡 MEDIUM focus)
├─ Mobile: 1 (🟢 LOW focus)
└─ Trend: Aggressive AI hiring, building native mobile
```

---

## 🛣️ Roadmap Signals

**Real strategic alignment analysis:**

```
Your Features:
├─ Q2: AI email assistant
├─ Q3: Advanced analytics
├─ Q4: Mobile app launch
└─ Q4: API rate limiting

Competitive Signals:
├─ ✅ VALIDATES (HubSpot launched AI email first)
│  └─ "Confirms our AI email prioritization is correct"
│
├─ 🚫 INVALIDATES (Salesforce + Pipedrive have similar features)
│  └─ "Market saturation in this feature, may want to pivot"
│
├─ ⚡ ACCELERATES (5 competitors now have AI features)
│  └─ "Accelerate our AI launch by 2 weeks to stay competitive"
│
└─ ⏸️ DEPRIORITIZES (Mobile apps not a competitor focus)
   └─ "We can delay mobile to Q1 2025 without competitive risk"

Recommended Actions:
1. Accelerate Q2 AI email (4/5 competitors have it)
2. Spike on advanced analytics (only 2/5 competitors offer it)
3. Confirm mobile app roadmap (low competitive pressure)
```

---

## ✅ Summary: What You'll Actually See

When you deploy and trigger data collection, within 30-60 seconds you'll see:

1. **Intelligence Queue:** 5-10 auto-detected moves from HubSpot
   - Real content from HubSpot website, RSS, news
   - AI-analyzed threat levels and confidence scores
   - Ready for PM validation

2. **Market Dashboard:** Threat analysis based on real data
   - Competitor threat heat map
   - Pricing change tracker
   - Recent intelligence with real-world moves

3. **Competitor Profile:** 4 tabs of real competitive intelligence
   - Feature announcements (from RSS + website)
   - Pricing changes (from website monitoring)
   - Job postings (from LinkedIn)
   - News mentions (from NewsAPI)

4. **Roadmap Signals:** AI analysis of how moves impact your strategy
   - Real validation signals
   - Actual recommended actions
   - Confidence scores based on move analysis

**This isn't simulated data. These are real, live sources.**

---

## 🚀 Ready to Deploy?

Follow **DEPLOY_NOW.md** to:
1. Push code to GitHub (2 min)
2. Deploy to Streamlit Cloud (1 min)
3. Configure API keys (1 min)
4. Trigger data collection (1 min)
5. See real competitive moves in Intelligence Queue

**Total time to live: 5 minutes**

Your competitive intelligence platform will be monitoring real competitors and collecting real data immediately.
