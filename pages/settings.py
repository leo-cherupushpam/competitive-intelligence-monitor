"""
Settings — Configuration and administration.
Manage competitors, data sources, API keys, collection schedules.
"""

import streamlit as st
import db
import os
from datetime import datetime
import pandas as pd


def show():
    """Render the Settings page."""

    st.header("⚙️ Settings")
    st.write("Configure competitors, data sources, and system settings.")

    # Tabs for different settings sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏢 Competitors",
        "📡 Data Sources",
        "🔑 API Keys",
        "📊 Logs & Status"
    ])

    # TAB 1: Competitor Management
    with tab1:
        st.subheader("Manage Tracked Competitors")

        # Add new competitor
        st.write("**Add New Competitor**")
        col1, col2, col3 = st.columns(3)

        with col1:
            comp_name = st.text_input("Company Name", placeholder="e.g., HubSpot")

        with col2:
            comp_website = st.text_input("Website URL", placeholder="https://example.com")

        with col3:
            comp_threat = st.selectbox("Initial Threat Level", ["LOW", "MEDIUM", "HIGH"])

        if st.button("➕ Add Competitor", use_container_width=True):
            if comp_name and comp_website:
                try:
                    db.create_competitor(comp_name, comp_website, "General", comp_threat)
                    st.success(f"✅ Added {comp_name}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Please fill in all fields")

        st.divider()

        # List existing competitors
        st.write("**Tracked Competitors**")
        try:
            competitors = db.get_all_competitors()

            if competitors:
                comp_df = pd.DataFrame([
                    {
                        "Name": c["name"],
                        "Website": c["website"][:40] + "..." if len(c["website"]) > 40 else c["website"],
                        "Threat": c["threat_baseline"],
                        "Status": c["status"],
                        "Last Updated": c.get("last_monitored_at", "Never")[:10]
                    }
                    for c in competitors
                ])
                st.dataframe(comp_df, use_container_width=True, hide_index=True)

                # Remove competitor
                st.write("**Remove Competitor**")
                comp_to_remove = st.selectbox(
                    "Select competitor to remove",
                    options=[c["name"] for c in competitors],
                    label_visibility="collapsed"
                )

                if st.button("🗑️ Remove Selected Competitor", use_container_width=True, type="secondary"):
                    if comp_to_remove:
                        comp_id = next(c["id"] for c in competitors if c["name"] == comp_to_remove)
                        try:
                            db.update_competitor_status(comp_id, "ARCHIVED")
                            st.success(f"Archived {comp_to_remove}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
            else:
                st.info("No competitors configured yet. Add your first competitor above.")

        except Exception as e:
            st.error(f"Error loading competitors: {e}")

    # TAB 2: Data Source Configuration
    with tab2:
        st.subheader("Data Source Configuration")

        st.write("Configure which data sources to monitor for each competitor.")

        try:
            competitors = db.get_all_competitors()

            if competitors:
                selected_comp = st.selectbox("Select Competitor", [c["name"] for c in competitors])

                if selected_comp:
                    comp_id = next(c["id"] for c in competitors if c["name"] == selected_comp)

                    st.write(f"**Data Sources for {selected_comp}**")

                    # Website monitoring
                    st.write("**Website Monitoring (FREE)**")
                    website_url = st.text_input(
                        "Pricing page URL",
                        placeholder="https://example.com/pricing",
                        label_visibility="collapsed"
                    )
                    if st.button("Register Website", key="website"):
                        if website_url:
                            db.register_source(comp_id, "WEBSITE", website_url)
                            st.success("Website source registered")
                        st.rerun()

                    # RSS Feed
                    st.write("**RSS Feed Monitoring (FREE)**")
                    rss_url = st.text_input(
                        "RSS Feed URL",
                        placeholder="https://example.com/blog/feed",
                        label_visibility="collapsed"
                    )
                    if st.button("Register RSS Feed", key="rss"):
                        if rss_url:
                            db.register_source(comp_id, "RSS", rss_url)
                            st.success("RSS feed registered")
                        st.rerun()

                    # LinkedIn Jobs
                    st.write("**LinkedIn Job Monitoring (FREE)**")
                    linkedin_url = st.text_input(
                        "LinkedIn Company URL",
                        placeholder="https://linkedin.com/company/example",
                        label_visibility="collapsed"
                    )
                    if st.button("Register LinkedIn", key="linkedin"):
                        if linkedin_url:
                            db.register_source(comp_id, "JOBS", linkedin_url)
                            st.success("LinkedIn source registered")
                        st.rerun()

                    st.divider()

                    # Show registered sources
                    st.write("**Active Data Sources**")
                    try:
                        sources = db.get_sources_for_competitor(comp_id, active_only=True)
                        if sources:
                            for source in sources:
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.write(f"**{source['source_type']}** → {source['source_url'][:50]}...")
                                with col2:
                                    if st.button("❌ Deactivate", key=f"deactivate_{source['id']}"):
                                        db.update_source_status(source["id"], False)
                                        st.rerun()
                        else:
                            st.info("No active data sources for this competitor")
                    except:
                        st.info("No sources registered yet")

            else:
                st.warning("Add competitors first")

        except Exception as e:
            st.error(f"Error: {e}")

    # TAB 3: API Key Management
    with tab3:
        st.subheader("API Key Configuration")

        st.write("Store API keys securely for data collection services.")

        # OpenAI API Key
        st.write("**OpenAI API Key** (for AI analysis)")
        st.write("🔗 [Get your API key](https://platform.openai.com/account/api-keys)")

        openai_key = st.text_input(
            "OPENAI_API_KEY",
            type="password",
            placeholder="sk-...",
            label_visibility="collapsed"
        )

        # Show current status
        from intelligence_engine import get_secret
        current_openai = get_secret("OPENAI_API_KEY")
        if current_openai:
            st.success(f"✅ OpenAI key active (ends in ...{current_openai[-4:]})")
        else:
            st.warning("⚠️ No OpenAI key configured")

        if st.button("💾 Save OpenAI Key"):
            if openai_key:
                db.save_setting("OPENAI_API_KEY", openai_key)
                st.success("✅ OpenAI API key saved!")
                st.rerun()
            else:
                st.warning("Please enter your API key")

        st.divider()

        # NewsAPI Key (optional)
        st.write("**NewsAPI Key** (for news monitoring)")
        st.write("🔗 [Get free API key](https://newsapi.org)")

        newsapi_key = st.text_input(
            "NEWSAPI_KEY",
            type="password",
            placeholder="Your NewsAPI key",
            label_visibility="collapsed"
        )

        current_newsapi = get_secret("NEWSAPI_KEY")
        if current_newsapi:
            st.success(f"✅ NewsAPI key active (ends in ...{current_newsapi[-4:]})")
        else:
            st.caption("NewsAPI key not set — news monitoring disabled")

        if st.button("💾 Save NewsAPI Key"):
            if newsapi_key:
                db.save_setting("NEWSAPI_KEY", newsapi_key)
                st.success("✅ NewsAPI key saved!")
                st.rerun()
            else:
                st.warning("Please enter your NewsAPI key")

        st.divider()

        st.info("💡 **Security Note:** For production, use environment variables or a secrets manager instead of storing keys in the app.")

    # TAB 4: Logs & Status
    with tab4:
        st.subheader("Collection Logs & System Status")

        # Collection Schedule Info
        st.write("**Scheduled Collection Runs**")
        schedule_info = {
            "Website Monitor": "Daily at 2am UTC",
            "RSS Parser": "Every 6 hours",
            "Product Hunt": "Daily at 9am UTC",
            "Job Board": "Bi-weekly (Tuesday 10am UTC)",
            "News Monitor": "Daily at 12pm UTC"
        }

        for collector, schedule in schedule_info.items():
            st.write(f"• **{collector}**: {schedule}")

        st.divider()

        # Collection History
        st.write("**Recent Collection Runs**")
        try:
            logs = db.get_collection_logs(limit=20)

            if logs:
                logs_df = pd.DataFrame([
                    {
                        "Date": log["ran_at"][:19],
                        "Collector": log["collector_name"],
                        "Found": log["items_found"],
                        "Processed": log["items_processed"],
                        "Duration (s)": round(log["duration_seconds"], 1),
                        "Status": "✅ OK" if not log.get("errors") else "⚠️ Error"
                    }
                    for log in logs
                ])
                st.dataframe(logs_df, use_container_width=True, hide_index=True)

                # Show errors if any
                error_logs = [log for log in logs if log.get("errors")]
                if error_logs:
                    st.warning(f"⚠️ {len(error_logs)} recent collection errors")
                    for log in error_logs:
                        with st.expander(f"{log['collector_name']} — {log['ran_at'][:10]}"):
                            st.write(log["errors"])
            else:
                st.info("No collection logs yet")

        except Exception as e:
            st.error(f"Error loading logs: {e}")

        st.divider()

        # NewsAPI Quota
        st.write("**NewsAPI Quota**")
        try:
            usage = db.get_newsapi_usage()
            remaining = 1000 - usage["used"]
            st.metric("Requests Used This Month", f"{usage['used']}/1000")
            st.progress(usage["used"] / 1000)

            if usage["used"] > 900:
                st.warning("⚠️ Approaching quota limit!")
            elif usage["used"] > 750:
                st.info("ℹ️ Using 75% of monthly quota")

        except Exception as e:
            st.info("NewsAPI quota tracking not available")

        st.divider()

        # Export Data
        st.write("**Export & Integration**")

        if st.button("📥 Export All Intelligence as CSV"):
            try:
                all_moves = db.get_all_moves()
                if all_moves:
                    export_df = pd.DataFrame([
                        {
                            "Date": move["collected_at"][:10],
                            "Competitor": move["competitor_name"],
                            "Title": move["title"],
                            "Dimension": move["dimension"],
                            "Threat": move["threat_level"],
                            "Description": move["description"][:100],
                            "Source": move["source_type"],
                            "Status": move["validation_status"]
                        }
                        for move in all_moves
                    ])

                    csv = export_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"competitive-intelligence-{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No data to export")
            except Exception as e:
                st.error(f"Export error: {e}")


if __name__ == "__main__":
    show()
