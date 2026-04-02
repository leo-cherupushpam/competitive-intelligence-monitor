"""
Roadmap Signals — AI-powered strategic alignment.
Analyzes how validated competitive moves impact our roadmap.
"""

import streamlit as st
import db
import json
from intelligence_engine import analyze_roadmap_impact


def show():
    """Render the Roadmap Signals page."""

    st.header("🛣️ Roadmap Signals")
    st.write("How are competitive moves impacting our product strategy?")

    # Left side: Our Roadmap
    st.subheader("📋 Our Planned Features")

    # Get roadmap from session or database
    if "our_roadmap" not in st.session_state:
        st.session_state.our_roadmap = []

    col1, col2 = st.columns([3, 1])
    with col1:
        roadmap_input = st.text_area(
            "Paste your planned features (one per line)",
            value="\n".join(st.session_state.our_roadmap) if st.session_state.our_roadmap else "",
            height=200,
            placeholder="Example:\nAI email writer\nAdvanced analytics dashboard\nMobile app launch\nAPI rate limiting\nCypress integration",
            label_visibility="collapsed"
        )

    with col2:
        if st.button("💾 Save Roadmap", use_container_width=True):
            roadmap_features = [f.strip() for f in roadmap_input.split("\n") if f.strip()]
            st.session_state.our_roadmap = roadmap_features
            st.success("Roadmap saved!")

    if st.session_state.our_roadmap:
        st.write("**Your Features:**")
        for feature in st.session_state.our_roadmap:
            st.write(f"• {feature}")

    st.divider()

    # Right side: Competitive Signals
    st.subheader("🎯 Strategic Signals from Competitors")

    try:
        # Get validated moves
        all_moves = db.get_all_moves()
        validated_moves = [m for m in all_moves if m["validation_status"] == "VALIDATED"]

        if not validated_moves:
            st.info("No validated moves yet. Validate moves in the Intelligence Queue to analyze roadmap impact.")
        else:
            st.write(f"Analyzing {len(validated_moves)} validated competitive moves...")

            signal_summary = {
                "VALIDATES": [],
                "INVALIDATES": [],
                "ACCELERATES": [],
                "DEPRIORITIZES": [],
                "MONITOR": []
            }

            # Analyze each move against roadmap
            for move in validated_moves:
                if st.session_state.our_roadmap:
                    signal = analyze_roadmap_impact(move["title"], st.session_state.our_roadmap)
                else:
                    signal = {"signal_type": "MONITOR", "reasoning": "No roadmap configured", "confidence": 0.5}

                signal_type = signal.get("signal_type", "MONITOR")
                if signal_type not in signal_summary:
                    signal_type = "MONITOR"

                signal_summary[signal_type].append({
                    "move": move,
                    "signal": signal
                })

            # Display signals by type
            st.write("")

            # VALIDATES signals
            if signal_summary["VALIDATES"]:
                st.success(f"✅ VALIDATES ({len(signal_summary['VALIDATES'])} moves)")
                st.write("*These competitive moves confirm our feature priorities are correct.*")
                for item in signal_summary["VALIDATES"]:
                    move = item["move"]
                    signal = item["signal"]
                    with st.container(border=True):
                        st.write(f"**{move['title']}** from {move['competitor_name']}")
                        st.write(f"💡 {signal['reasoning']}")
                        st.caption(f"Confidence: {signal['confidence'] * 100:.0f}%")
                st.divider()

            # INVALIDATES signals
            if signal_summary["INVALIDATES"]:
                st.error(f"🚫 INVALIDATES ({len(signal_summary['INVALIDATES'])} moves)")
                st.write("*These moves suggest we should reconsider feature priorities.*")
                for item in signal_summary["INVALIDATES"]:
                    move = item["move"]
                    signal = item["signal"]
                    with st.container(border=True):
                        st.write(f"**{move['title']}** from {move['competitor_name']}")
                        st.write(f"💡 {signal['reasoning']}")
                        st.caption(f"Confidence: {signal['confidence'] * 100:.0f}%")
                st.divider()

            # ACCELERATES signals
            if signal_summary["ACCELERATES"]:
                st.warning(f"⚡ ACCELERATES ({len(signal_summary['ACCELERATES'])} moves)")
                st.write("*Competitors are moving fast. We should accelerate these features.*")
                for item in signal_summary["ACCELERATES"]:
                    move = item["move"]
                    signal = item["signal"]
                    with st.container(border=True):
                        st.write(f"**{move['title']}** from {move['competitor_name']}")
                        st.write(f"💡 {signal['reasoning']}")
                        st.caption(f"Confidence: {signal['confidence'] * 100:.0f}%")
                st.divider()

            # DEPRIORITIZES signals
            if signal_summary["DEPRIORITIZES"]:
                st.info(f"⏸️ DEPRIORITIZES ({len(signal_summary['DEPRIORITIZES'])} moves)")
                st.write("*These moves suggest we can safely deprioritize certain features.*")
                for item in signal_summary["DEPRIORITIZES"]:
                    move = item["move"]
                    signal = item["signal"]
                    with st.container(border=True):
                        st.write(f"**{move['title']}** from {move['competitor_name']}")
                        st.write(f"💡 {signal['reasoning']}")
                        st.caption(f"Confidence: {signal['confidence'] * 100:.0f}%")
                st.divider()

            # MONITOR signals
            if signal_summary["MONITOR"]:
                with st.expander(f"📍 MONITOR ({len(signal_summary['MONITOR'])} moves)"):
                    st.write("*Watch these moves but no action needed yet.*")
                    for item in signal_summary["MONITOR"]:
                        move = item["move"]
                        signal = item["signal"]
                        with st.container(border=True):
                            st.write(f"**{move['title']}** from {move['competitor_name']}")
                            st.write(f"💡 {signal['reasoning']}")
                            st.caption(f"Confidence: {signal['confidence'] * 100:.0f}%")

            # Summary recommendations
            st.divider()
            st.subheader("🎯 Recommended Actions")

            actions = []

            if signal_summary["ACCELERATES"]:
                accelerate_count = len(signal_summary["ACCELERATES"])
                actions.append(f"1. **Accelerate {accelerate_count} features** — {accelerate_count} competitor move(s) suggest urgent prioritization")

            if signal_summary["INVALIDATES"]:
                invalidate_count = len(signal_summary["INVALIDATES"])
                actions.append(f"2. **Reconsider {invalidate_count} features** — {invalidate_count} move(s) challenge our assumptions")

            if signal_summary["VALIDATES"]:
                validate_count = len(signal_summary["VALIDATES"])
                actions.append(f"3. **Confirm {validate_count} features** — {validate_count} move(s) validate our strategy")

            if not actions:
                st.write("No immediate actions recommended based on current intelligence.")
            else:
                for action in actions:
                    st.write(action)

    except Exception as e:
        st.error(f"Error analyzing roadmap signals: {e}")


if __name__ == "__main__":
    show()
