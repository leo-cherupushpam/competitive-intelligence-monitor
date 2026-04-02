"""
Competitor Profile — Deep dive into a single competitor.
Shows: Features & News, Pricing, Positioning, Hiring Signals (4 tabs).
"""

import streamlit as st
import db
import pandas as pd
from datetime import datetime


def show():
    """Render the Competitor Profile page."""

    st.header("🔍 Competitor Profile")
    st.write("Deep dive into competitor moves across key dimensions.")

    # Select competitor
    competitors = db.get_all_competitors()
    if not competitors:
        st.warning("No competitors configured. Go to Settings to add competitors.")
        return

    competitor_names = {c["name"]: c["id"] for c in competitors}
    selected_competitor = st.selectbox("Select Competitor", options=list(competitor_names.keys()))

    if not selected_competitor:
        return

    competitor_id = competitor_names[selected_competitor]
    competitor = next(c for c in competitors if c["id"] == competitor_id)

    # Header with competitor info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader(selected_competitor)
    with col2:
        threat_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(competitor["threat_baseline"], "⚪")
        threat_level = competitor["threat_baseline"]
        st.metric("Threat Level", threat_level)
    with col3:
        if competitor["website"]:
            st.markdown(f"🔗 [{competitor['website'][:40]}]({competitor['website']})")
        else:
            st.write("No website configured")

    st.caption(f"Last monitored: {competitor.get('last_monitored_at', 'Never')}")
    st.divider()

    # Tabs for different dimensions
    tab1, tab2, tab3, tab4 = st.tabs([
        "📰 Features & News",
        "💰 Pricing",
        "🎯 Positioning",
        "👥 Hiring Signals"
    ])

    # Get moves for this competitor
    try:
        all_moves = db.get_all_moves()
        moves = [m for m in all_moves if m["competitor_id"] == competitor_id]
    except:
        moves = []

    # TAB 1: Features & News
    with tab1:
        st.subheader("📰 Features & News")

        feature_moves = [m for m in moves if m["dimension"] == "FEATURE"]
        news_moves = [m for m in moves if m["dimension"] == "NEWS"]

        if feature_moves:
            st.write(f"**{len(feature_moves)} Feature Updates**")
            for move in sorted(feature_moves, key=lambda x: x["collected_at"], reverse=True):
                with st.container(border=True):
                    st.write(f"**{move['title']}**")
                    st.write(move['description'])
                    st.caption(f"Detected: {move['collected_at'][:10]} | Source: {move['source_type']}")
        else:
            st.info("No feature updates detected")

        st.divider()

        if news_moves:
            st.write(f"**{len(news_moves)} News Mentions**")
            for move in sorted(news_moves, key=lambda x: x["collected_at"], reverse=True):
                with st.container(border=True):
                    st.write(f"**{move['title']}**")
                    st.write(move['description'])
                    st.caption(f"Detected: {move['collected_at'][:10]} | Source: {move['source_type']}")
        else:
            st.info("No news mentions detected")

    # TAB 2: Pricing
    with tab2:
        st.subheader("💰 Pricing Strategy")

        pricing_moves = [m for m in moves if m["dimension"] == "PRICING"]

        if pricing_moves:
            st.write(f"**{len(pricing_moves)} Pricing Changes**")
            pricing_df = pd.DataFrame([
                {
                    "Date": move["collected_at"][:10],
                    "Description": move["description"][:100] + "..." if len(move["description"]) > 100 else move["description"],
                    "Threat": move["threat_level"],
                    "Source": move["source_type"]
                }
                for move in sorted(pricing_moves, key=lambda x: x["collected_at"], reverse=True)
            ])
            st.dataframe(pricing_df, use_container_width=True, hide_index=True)
        else:
            st.info("No pricing changes detected")

        st.write("💡 **Insight:** Monitor /pricing page for changes in tier structure, pricing per seat, and enterprise offerings.")

    # TAB 3: Positioning
    with tab3:
        st.subheader("🎯 Market Positioning")

        positioning_moves = [m for m in moves if m["dimension"] == "POSITIONING"]

        if positioning_moves:
            st.write(f"**{len(positioning_moves)} Positioning Shifts**")
            for move in sorted(positioning_moves, key=lambda x: x["collected_at"], reverse=True):
                with st.container(border=True):
                    st.write(f"**{move['title']}**")
                    st.write(move['description'])
                    st.caption(f"Detected: {move['collected_at'][:10]} | Source: {move['source_type']}")
        else:
            st.info("No positioning changes detected")

        st.write("💡 **Insight:** Positioning changes detected from website messaging, brand updates, and press releases.")

    # TAB 4: Hiring Signals
    with tab4:
        st.subheader("👥 Hiring & Team Expansion")

        hiring_moves = [m for m in moves if m["dimension"] == "HIRING"]

        if hiring_moves:
            st.write(f"**{len(hiring_moves)} Hiring Signals**")

            # Analyze skills from hiring moves
            skills_dict = {}
            for move in hiring_moves:
                # Extract job titles/skills from description
                text = move['description'].lower()
                if any(word in text for word in ["ai", "machine learning", "llm", "nlp"]):
                    skills_dict["AI/ML"] = skills_dict.get("AI/ML", 0) + 1
                if any(word in text for word in ["backend", "devops", "platform", "infrastructure"]):
                    skills_dict["Platform/DevOps"] = skills_dict.get("Platform/DevOps", 0) + 1
                if any(word in text for word in ["mobile", "ios", "android", "react native"]):
                    skills_dict["Mobile"] = skills_dict.get("Mobile", 0) + 1
                if any(word in text for word in ["security", "privacy", "compliance"]):
                    skills_dict["Security"] = skills_dict.get("Security", 0) + 1

            if skills_dict:
                st.write("**Hiring Focus Areas**")
                skills_df = pd.DataFrame([
                    {"Area": skill, "Count": count}
                    for skill, count in sorted(skills_dict.items(), key=lambda x: x[1], reverse=True)
                ])
                st.bar_chart(skills_df.set_index("Area"))

            st.write("\n**Recent Job Postings**")
            for move in sorted(hiring_moves, key=lambda x: x["collected_at"], reverse=True):
                with st.container(border=True):
                    st.write(f"**{move['title']}**")
                    st.write(move['description'][:150] + "..." if len(move['description']) > 150 else move['description'])
                    st.caption(f"Detected: {move['collected_at'][:10]}")
        else:
            st.info("No hiring signals detected")

        st.write("💡 **Insight:** Job postings indicate product direction. New AI/ML hires suggest feature expansion in that area.")

    # Right panel: AI Insights (summary)
    st.divider()
    st.subheader("🤖 AI Insights for This Competitor")

    try:
        # Get insights for all moves of this competitor
        insights = []
        for move in moves:
            move_insights = db.get_insights_for_move(move["id"])
            insights.extend(move_insights)

        if insights:
            insight_cols = st.columns(3)
            with insight_cols[0]:
                st.write("**Key Threats**")
                high_threats = [m for m in moves if m["threat_level"] == "HIGH"]
                if high_threats:
                    for threat in high_threats[:3]:
                        st.write(f"• {threat['title']}")
                else:
                    st.write("No major threats detected")

            with insight_cols[1]:
                st.write("**Opportunities for Us**")
                opportunities = [m for m in moves if m["opportunity"]]
                if opportunities:
                    for opp in opportunities[:3]:
                        st.write(f"• {opp['title']}")
                else:
                    st.write("No opportunities identified")

            with insight_cols[2]:
                st.write("**Market Trends**")
                st.write(f"• Total moves detected: {len(moves)}")
                recent_moves = [m for m in moves if (datetime.utcnow() - datetime.fromisoformat(m["collected_at"])).days <= 30]
                st.write(f"• Activity in last 30 days: {len(recent_moves)}")
        else:
            st.info("No AI insights generated yet")

    except Exception as e:
        st.warning(f"Could not load insights: {e}")


if __name__ == "__main__":
    show()
