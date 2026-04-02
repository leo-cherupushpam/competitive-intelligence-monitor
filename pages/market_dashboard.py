"""
Market Dashboard — Executive view of competitive landscape.
Shows: threats, opportunities, recent moves, collection status, market trends.
"""

import streamlit as st
import db
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta


def show():
    """Render the Market Dashboard page."""

    st.header("📊 Market Dashboard")

    try:
        # Get all data
        competitors = db.get_all_competitors()
        all_moves = db.get_all_moves()
        stats = db.get_stats()
        last_run = db.get_last_collection_run()

        # Empty state
        if not all_moves:
            st.info("### No competitive intelligence collected yet")
            st.write("Go to **Intelligence Queue** to run data collection. You'll see:")
            st.write("- 🚨 Critical threats from competitors")
            st.write("- 💡 Opportunities to capitalize on")
            st.write("- 📊 Market trends and activity patterns")
            st.write("- 🔄 Data freshness from all sources")
            return

        st.divider()

        # Executive KPI Row
        st.subheader("📈 Executive KPIs")
        exec_kpi_cols = st.columns(4)

        with exec_kpi_cols[0]:
            high_threats = len([m for m in all_moves if m["threat_level"] == "HIGH"])
            st.metric("🚨 Critical Threats", high_threats)

        with exec_kpi_cols[1]:
            opportunities = len([m for m in all_moves if m["opportunity"]])
            st.metric("💡 Opportunities Detected", opportunities)

        with exec_kpi_cols[2]:
            # Feature gaps (rough estimate: features we don't have that competitors have)
            feature_moves = len([m for m in all_moves if m["dimension"] == "FEATURE"])
            st.metric("🆕 Competitor Features Detected", feature_moves)

        with exec_kpi_cols[3]:
            # Market momentum (trend of recent moves)
            recent_moves = [m for m in all_moves if (datetime.utcnow() - datetime.fromisoformat(m["collected_at"])).days <= 7]
            st.metric("📊 Activity Last 7 Days", len(recent_moves))

        st.divider()

        # Tab layout for different views
        tab1, tab2, tab3, tab4 = st.tabs([
            "🎯 Threat Matrix",
            "💰 Pricing War",
            "📰 Recent Intel",
            "🔄 Collection Health"
        ])

        # TAB 1: Threat Matrix
        with tab1:
            st.subheader("Competitive Threat Matrix")

            if all_moves and competitors:
                # Create threat matrix data
                threat_data = []
                for competitor in competitors:
                    comp_moves = [m for m in all_moves if m["competitor_id"] == competitor["id"]]

                    if comp_moves:
                        threat_level_num = {
                            "HIGH": 3,
                            "MEDIUM": 2,
                            "LOW": 1
                        }
                        avg_threat = sum(threat_level_num.get(m["threat_level"], 1) for m in comp_moves) / len(comp_moves)
                        high_count = len([m for m in comp_moves if m["threat_level"] == "HIGH"])

                        threat_data.append({
                            "Competitor": competitor["name"],
                            "Threat Score": avg_threat,
                            "Recent Activity": len([m for m in comp_moves if (datetime.utcnow() - datetime.fromisoformat(m["collected_at"])).days <= 7]),
                            "High Threats": high_count,
                            "Total Moves": len(comp_moves)
                        })

                if threat_data:
                    threat_df = pd.DataFrame(threat_data)

                    # Scatter plot: Threat Score vs Recent Activity
                    fig = px.scatter(
                        threat_df,
                        x="Threat Score",
                        y="Recent Activity",
                        size="Total Moves",
                        color="High Threats",
                        hover_name="Competitor",
                        title="Competitive Threat Heat Map",
                        labels={"Threat Score": "Average Threat Level (1=Low, 3=High)", "Recent Activity": "Moves (Last 7 Days)"},
                        color_continuous_scale="Reds"
                    )

                    fig.update_layout(height=500, width=800)
                    st.plotly_chart(fig, use_container_width=True)

                    # Show threat ranking
                    st.write("**Threat Ranking**")
                    threat_ranking = threat_df.sort_values("Threat Score", ascending=False)
                    for idx, row in threat_ranking.iterrows():
                        threat_emoji = {
                            3: "🔴",
                            2: "🟡",
                            1: "🟢"
                        }.get(int(row["Threat Score"]), "⚪")
                        st.write(f"{threat_emoji} **{row['Competitor']}** - Threat: {row['Threat Score']:.1f}, Recent: {row['Recent Activity']} moves")
                else:
                    st.info("No threat data available")
            else:
                st.info("No competitors or moves to analyze")

        # TAB 2: Pricing War
        with tab2:
            st.subheader("Pricing Strategy Trends")

            pricing_moves = [m for m in all_moves if m["dimension"] == "PRICING"]

            if pricing_moves:
                st.write(f"**{len(pricing_moves)} Pricing Changes Detected**")

                # Pricing by competitor
                pricing_by_competitor = {}
                for move in pricing_moves:
                    comp_name = move["competitor_name"]
                    pricing_by_competitor[comp_name] = pricing_by_competitor.get(comp_name, 0) + 1

                if pricing_by_competitor:
                    pricing_df = pd.DataFrame([
                        {"Competitor": comp, "Pricing Changes": count}
                        for comp, count in sorted(pricing_by_competitor.items(), key=lambda x: x[1], reverse=True)
                    ])

                    fig = px.bar(
                        pricing_df,
                        x="Competitor",
                        y="Pricing Changes",
                        title="Pricing Changes by Competitor",
                        color_discrete_sequence=["#FF6B6B"]
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Show recent pricing moves
                    st.write("**Recent Pricing Changes**")
                    for move in sorted(pricing_moves, key=lambda x: x["collected_at"], reverse=True)[:5]:
                        st.write(f"• **{move['competitor_name']}**: {move['title']}")
                        st.caption(move['description'][:100] + "..." if len(move['description']) > 100 else move['description'])
            else:
                st.info("No pricing changes detected recently")

        # TAB 3: Recent Intelligence
        with tab3:
            st.subheader("📰 Latest Competitive Intelligence")

            if all_moves:
                # Sort by date, most recent first
                recent_moves = sorted(all_moves, key=lambda x: x["collected_at"], reverse=True)[:10]

                for move in recent_moves:
                    threat_color = {
                        "HIGH": "🔴",
                        "MEDIUM": "🟡",
                        "LOW": "🟢"
                    }.get(move["threat_level"], "⚪")

                    with st.container(border=True):
                        col1, col2 = st.columns([3, 1])

                        with col1:
                            st.write(f"{threat_color} **{move['competitor_name']}** — {move['title']}")
                            st.write(f"*{move['description']}*")
                            st.caption(f"{move['source_type']} | {move['collected_at'][:10]}")

                        with col2:
                            if move["opportunity"]:
                                st.write("💡 Opportunity")
                            status_badge = "✅" if move["validation_status"] == "VALIDATED" else "⏳"
                            st.write(f"{status_badge} {move['validation_status']}")
            else:
                st.info("No intelligence collected yet")

        # TAB 4: Collection Health
        with tab4:
            st.subheader("🔄 Data Collection Health")

            if last_run:
                col1, col2, col3 = st.columns(3)
                with col1:
                    last_time = datetime.fromisoformat(last_run["ran_at"])
                    time_diff = datetime.utcnow() - last_time
                    st.metric("Last Run", f"{int(time_diff.total_seconds() / 3600)}h ago")

                with col2:
                    st.metric("Items Found", last_run.get("items_found", 0))

                with col3:
                    st.metric("Items Processed", last_run.get("items_processed", 0))

                if last_run.get("errors"):
                    st.warning(f"Errors: {last_run['errors']}")

            # Collection run history
            st.write("**Collection History (Last 10 Runs)**")
            try:
                collection_logs = db.get_collection_logs(limit=10)
                if collection_logs:
                    logs_df = pd.DataFrame([
                        {
                            "Date": log["ran_at"][:10],
                            "Collector": log["collector_name"],
                            "Found": log["items_found"],
                            "Processed": log["items_processed"],
                            "Status": "✅ OK" if not log.get("errors") else "⚠️ Error"
                        }
                        for log in collection_logs
                    ])
                    st.dataframe(logs_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No collection history yet")
            except:
                st.info("Collection logs not available")

            # NewsAPI quota
            try:
                usage = db.get_newsapi_usage()
                st.metric("NewsAPI Usage", f"{usage['used']}/1000 requests this month")
                st.progress(usage['used'] / 1000)
            except:
                pass

    except Exception as e:
        st.error(f"Error loading dashboard: {e}")


if __name__ == "__main__":
    show()
