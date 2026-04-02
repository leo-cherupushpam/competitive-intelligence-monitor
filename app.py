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
    # Set default page - Onboarding if no competitors, else Intelligence Queue
    try:
        competitors = db.get_all_competitors()
        default_page = "Onboarding" if len(competitors) == 0 else "Intelligence Queue"
    except:
        default_page = "Onboarding"
    st.session_state.current_page = default_page

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

# Sidebar Navigation
with st.sidebar:
    st.title("🎯 Competitive Intelligence")
    st.write("Track competitor moves. Validate intelligence. Inform strategy.")

    st.divider()

    # Navigation Menu
    st.write("**📑 Navigation**")

    # Get data for badges
    try:
        moves = db.get_all_moves()
        pending_count = len([m for m in moves if m["validation_status"] == "AUTO_DETECTED"])
    except:
        pending_count = 0

    # Define navigation items with icons and optional badges
    nav_items = [
        ("🚀 Setup", "Onboarding"),
        (f"📋 Validation {f'({pending_count})' if pending_count > 0 else ''}", "Intelligence Queue"),
        ("🔍 Profiles", "Competitor Profile"),
        ("📊 Dashboard", "Market Dashboard"),
        ("🛣️ Strategy", "Roadmap Signals"),
        ("⚙️ Settings", "Settings"),
    ]

    # Navigation using selectbox
    current = st.session_state.current_page
    selected = st.selectbox(
        "Go to:",
        options=[item[1] for item in nav_items],
        index=[item[1] for item in nav_items].index(current),
        format_func=lambda x: next(item[0] for item in nav_items if item[1] == x),
        label_visibility="collapsed"
    )

    if selected != current:
        st.session_state.current_page = selected
        st.rerun()

    st.divider()

    # Sidebar Stats (only show if not onboarding)
    if st.session_state.current_page != "Onboarding":
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
                    status_text = f"Healthy ({int(time_diff.total_seconds()/60)}m ago)"
                elif time_diff.total_seconds() < 86400:  # Less than 24 hours
                    status_color = "🟡"
                    status_text = f"Overdue ({time_diff.days}d ago)"
                else:
                    status_color = "🔴"
                    status_text = f"Stale ({time_diff.days}d ago)"

                st.write(f"{status_color} {status_text}")
                st.caption(f"Found: {last_run.get('items_found', 0)} | Processed: {last_run.get('items_processed', 0)}")
            else:
                st.info("No collection runs yet")
        except Exception as e:
            st.caption(f"Status: {str(e)[:30]}")

        st.divider()

        # Manual trigger
        if st.button("🚀 Run Data Collection", use_container_width=True, type="primary"):
            from background_jobs import trigger_all_collectors
            with st.spinner("Running collectors…"):
                try:
                    trigger_all_collectors()
                    st.success("✅ Collection triggered!")
                except Exception as e:
                    st.error(f"Error: {e}")
        st.caption("Scan all data sources for competitive moves")


# Main Content Area
if st.session_state.current_page != "Onboarding":
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

# Route to selected page
page = st.session_state.current_page

if page == "Onboarding":
    from pages import onboarding
    onboarding.show()
elif page == "Intelligence Queue":
    from pages import intelligence_queue
    intelligence_queue.show()
elif page == "Competitor Profile":
    from pages import competitor_profile
    competitor_profile.show()
elif page == "Market Dashboard":
    from pages import market_dashboard
    market_dashboard.show()
elif page == "Roadmap Signals":
    from pages import roadmap_signals
    roadmap_signals.show()
elif page == "Settings":
    from pages import settings
    settings.show()
else:
    st.error(f"Page not found: {page}")


# Footer
if st.session_state.current_page != "Onboarding":
    st.divider()
    st.caption("Competitive Intelligence Monitor v1.0 | Built with Streamlit")
