"""
Onboarding — First-time setup for users.
Asks for company name, AI searches for competitors, auto-adds them.
"""

import streamlit as st
import db
from intelligence_engine import find_competitors, get_secret
from competitor_registry import get_all_segments, get_competitors_for_segment


def show():
    """Render the onboarding page."""

    st.title("🚀 Welcome to Competitive Intelligence Monitor")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.write("""
        Track what your competitors are doing and stay ahead of the market.

        Let's get started! Tell us about your company and we'll automatically find
        your competitors to monitor.
        """)

    with col2:
        st.info("⏱️ Takes 2 minutes")

    st.divider()

    # Step 1: Company name
    st.subheader("📋 Step 1: Your Company")

    company_name = st.text_input(
        "What company do you work at?",
        placeholder="e.g., HubSpot, Asana, Mixpanel",
        label_visibility="collapsed"
    )

    if not company_name:
        st.warning("Please enter your company name to continue")
        return

    st.divider()

    # Step 2: Market segment (optional, helps with competitor search)
    st.subheader("🎯 Step 2: Market Segment (Optional)")

    st.write("Selecting a market segment helps us find more relevant competitors.")

    segments = get_all_segments()
    selected_segment = st.selectbox(
        "What market are you in?",
        options=["Auto-detect"] + segments,
        help="If you're not sure, we can auto-detect based on your company name",
        label_visibility="collapsed"
    )

    st.divider()

    # Step 3: OpenAI API Key (if not already configured)
    has_key = bool(get_secret("OPENAI_API_KEY"))
    if not has_key:
        st.subheader("🔑 Step 3: OpenAI API Key")
        st.write("Required to search for competitors. [Get one free →](https://platform.openai.com/account/api-keys)")

        inline_key = st.text_input(
            "Paste your OpenAI API key",
            type="password",
            placeholder="sk-...",
            label_visibility="collapsed"
        )
        if inline_key:
            db.save_setting("OPENAI_API_KEY", inline_key)
            st.success("✅ Key saved!")
            has_key = True

        if not has_key:
            st.info("Enter your key above, then click Search.")
            return

        st.divider()

    # Step 4: Find competitors
    st.subheader("🔍 Step 3: Find Competitors")

    if st.button("🤖 Search for Competitors", use_container_width=True, type="primary"):
        market_segment = None if selected_segment == "Auto-detect" else selected_segment
        competitors = []
        ai_error = None

        with st.spinner("🔍 AI is searching for competitors..."):
            try:
                competitors = find_competitors(company_name, market_segment)
            except Exception as e:
                ai_error = str(e)

        # Fallback: use built-in registry if AI failed or returned nothing
        if not competitors and market_segment:
            competitors = get_competitors_for_segment(market_segment)
            if competitors:
                st.info(f"Used built-in {market_segment} competitor list (AI unavailable).")
            elif ai_error:
                st.error(f"❌ AI search failed: {ai_error}")
                st.stop()
        elif not competitors and ai_error:
            st.error(f"❌ AI search failed: {ai_error}")
            st.stop()

        if competitors:
            # Store in session state for display and next steps
            st.session_state.found_competitors = competitors
            st.rerun()
        elif not competitors:
            st.error("❌ No competitors found. Select a market segment above to use the built-in library.")

    # Display found competitors if available
    if "found_competitors" in st.session_state and st.session_state.found_competitors:
        competitors = st.session_state.found_competitors

        st.success(f"✅ Found {len(competitors)} competitors!")
        st.write("**Competitors to Monitor:**")

        for idx, comp in enumerate(competitors, 1):
            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                st.write(f"{idx}. **{comp['name']}**")
                st.caption(comp.get('reason', ''))

            with col2:
                threat = comp.get('threat_baseline', 'MEDIUM')
                threat_emoji = {
                    "HIGH": "🔴",
                    "MEDIUM": "🟡",
                    "LOW": "🟢"
                }.get(threat, "⚪")
                st.write(f"{threat_emoji} {threat}")

            with col3:
                st.caption(f"[Website]({comp['website']})")

        st.divider()

        # Step 4: Add to database
        st.subheader("📊 Step 4: Add to Database")

        if st.button("✨ Start Monitoring", use_container_width=True, type="primary", key="start_monitoring"):
            with st.spinner("Adding competitors to database..."):
                added = 0
                errors = []
                existing = db.get_all_competitors()
                existing_names = {c['name'].lower() for c in existing}

                for comp in st.session_state.found_competitors:
                    try:
                        # Check if competitor already exists (case-insensitive)
                        if comp['name'].lower() in existing_names:
                            st.write(f"⏭️ Already tracking: {comp['name']}")
                        else:
                            db.create_competitor(
                                comp['name'],
                                comp.get('website', ''),
                                selected_segment if selected_segment != "Auto-detect" else "General",
                                comp.get('threat_baseline', 'MEDIUM')
                            )
                            st.write(f"✅ Added: {comp['name']}")
                            added += 1
                    except Exception as e:
                        error_msg = f"❌ {comp['name']}: {str(e)}"
                        st.write(error_msg)
                        errors.append(error_msg)

                st.divider()

                if added > 0:
                    st.success(f"✅ Successfully added {added} competitors to the database!")
                    st.balloons()

                    st.info("🎉 **Setup complete!** Your competitive intelligence system is ready.")
                    st.write("""
                    **Next steps:**
                    1. Click **Intelligence Queue** in the sidebar
                    2. Click **🚀 Run Data Collection** to gather competitive data
                    3. Validate moves as they arrive
                    4. Check **Market Dashboard** for executive insights
                    """)
                else:
                    st.error(f"❌ Failed to add competitors. {len(errors)} error(s):")
                    if errors:
                        for err in errors:
                            st.write(f"  {err}")


def should_show_onboarding():
    """Check if onboarding should be shown (no competitors configured yet)."""
    try:
        competitors = db.get_all_competitors()
        return len(competitors) == 0
    except:
        return False


if __name__ == "__main__":
    show()
