"""
Competitive Intelligence Monitor — Main Streamlit App
Dual-persona design: PMs validate moves + executives view strategic dashboards.
"""

import streamlit as st
import db
from datetime import datetime
import pandas as pd

# Configure page FIRST (must be before all other Streamlit commands)
st.set_page_config(
    page_title="Competitive Intelligence Monitor",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database once per session
@st.cache_resource
def init_database():
    db.init_db()
    return True

init_database()

# Initialize session state
if "current_page" not in st.session_state:
    st.session_state.current_page = "Intelligence Queue"

# Check if onboarding is needed (no competitors configured)
try:
    competitors = db.get_all_competitors()
    needs_onboarding = len(competitors) == 0
except:
    needs_onboarding = True

# Custom CSS for dark theme
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: 2rem;
    }
    .metric-card {
        background-color: #1e1e1e;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #0066cc;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation (only show if not onboarding)
if not needs_onboarding:
    with st.sidebar:
        st.title("🎯 Competitive Intelligence")
        st.write("Track competitor moves. Validate intelligence. Inform strategy.")

        st.divider()

        # Navigation
        page = st.radio(
            "Navigate to:",
            options=[
                "Intelligence Queue",
                "Competitor Profile",
                "Market Dashboard",
                "Roadmap Signals",
                "Settings"
            ],
            label_visibility="collapsed"
        )

        st.session_state.current_page = page

        st.divider()

        # Sidebar Stats
        st.subheader("📊 Quick Stats")

        try:
            stats = db.get_stats()

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Competitors", stats.get("total_competitors", 0))
                st.metric("Total Moves", stats.get("total_moves", 0))

            with col2:
                st.metric("HIGH Threats", stats.get("high_threats", 0))
                st.metric("Validated", stats.get("validated_moves", 0))
        except Exception as e:
            st.warning(f"Error loading stats: {e}")

        st.divider()

        # Collection Status
        st.subheader("🔄 Collection Status")
        try:
            last_run = db.get_last_collection_run()
            if last_run:
                last_time = datetime.fromisoformat(last_run["ran_at"])
                time_diff = datetime.utcnow() - last_time

                # Color code based on freshness
                if time_diff.total_seconds() < 3600:  # Less than 1 hour
                    status_color = "🟢"
                    status_text = f"Healthy (updated {int(time_diff.total_seconds()/60)}m ago)"
                elif time_diff.total_seconds() < 86400:  # Less than 24 hours
                    status_color = "🟡"
                    status_text = f"Overdue (last updated {time_diff.days}d ago)"
                else:
                    status_color = "🔴"
                    status_text = f"Stale (last updated {time_diff.days}d ago)"

                st.write(f"{status_color} {status_text}")
                st.write(f"Items found: {last_run.get('items_found', 0)}")
                st.write(f"Items processed: {last_run.get('items_processed', 0)}")
            else:
                st.warning("No collection runs yet")
        except Exception as e:
            st.warning(f"Status unavailable: {e}")

        # Manual trigger (for Settings page to use)
        if st.button("🔄 Trigger All Collectors Now"):
            from background_jobs import trigger_all_collectors
            with st.spinner("Running data collectors..."):
                trigger_all_collectors()
            st.success("Data collection triggered!")


# Main Content Area
if not needs_onboarding:
    st.title("🎯 Competitive Intelligence Monitor")

    # KPI Header Row
    st.subheader("Live Competitive Intelligence")

    try:
        stats = db.get_stats()

        # Create KPI columns
        kpi_cols = st.columns(5)

        with kpi_cols[0]:
            st.metric(
                "🏢 Tracked Competitors",
                stats.get("total_competitors", 0),
                help="Total number of competitors being monitored"
            )

        with kpi_cols[1]:
            st.metric(
                "📊 Auto-Detected Moves",
                stats.get("auto_detected_moves", 0),
                help="Moves awaiting PM validation"
            )

        with kpi_cols[2]:
            st.metric(
                "🚨 HIGH Threats",
                stats.get("high_threats", 0),
                help="Critical competitive threats"
            )

        with kpi_cols[3]:
            st.metric(
                "✅ Validated Moves",
                stats.get("validated_moves", 0),
                help="Confirmed competitive intelligence"
            )

        with kpi_cols[4]:
            # Collection status badge
            last_run = db.get_last_collection_run()
            if last_run:
                last_time = datetime.fromisoformat(last_run["ran_at"])
                time_diff = datetime.utcnow() - last_time
                hours_ago = int(time_diff.total_seconds() / 3600)
                status_badge = f"{hours_ago}h ago"
            else:
                status_badge = "Never"

            st.metric(
                "⏱️ Last Updated",
                status_badge,
                help="When data collection last ran"
            )

    except Exception as e:
        st.error(f"Error loading KPIs: {e}")

    st.divider()

# Show onboarding if no competitors configured
if needs_onboarding:
    from pages import onboarding
    onboarding.show()
else:
    # Route to selected page
    if st.session_state.current_page == "Intelligence Queue":
        from pages import intelligence_queue
        intelligence_queue.show()

    elif st.session_state.current_page == "Competitor Profile":
        from pages import competitor_profile
        competitor_profile.show()

    elif st.session_state.current_page == "Market Dashboard":
        from pages import market_dashboard
        market_dashboard.show()

    elif st.session_state.current_page == "Roadmap Signals":
        from pages import roadmap_signals
        roadmap_signals.show()

    elif st.session_state.current_page == "Settings":
        from pages import settings
        settings.show()

    else:
        st.error("Page not found")


# Footer (only show if not onboarding)
if not needs_onboarding:
    st.divider()
    st.caption("Competitive Intelligence Monitor v1.0 | Built with Streamlit")
