"""
Intelligence Queue — PM validation workflow for auto-detected moves.
PMs review auto-detected moves, validate/dismiss, and provide feedback.
"""

import streamlit as st
import db
import pandas as pd
from datetime import datetime, timedelta


def show():
    """Render the Intelligence Queue page."""

    st.header("📋 Intelligence Queue")
    st.write("Review auto-detected competitive moves. Validate to confirm, dismiss to filter noise.")

    # Filters
    st.subheader("Filters")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        status_filter = st.multiselect(
            "Status",
            ["AUTO_DETECTED", "VALIDATED", "DISMISSED"],
            default=["AUTO_DETECTED"],
            label_visibility="collapsed"
        )

    with col2:
        competitors = db.get_all_competitors()
        competitor_names = [c["name"] for c in competitors]
        competitor_filter = st.multiselect(
            "Competitor",
            competitor_names,
            label_visibility="collapsed"
        )

    with col3:
        threat_filter = st.multiselect(
            "Threat Level",
            ["LOW", "MEDIUM", "HIGH"],
            label_visibility="collapsed"
        )

    with col4:
        source_filter = st.multiselect(
            "Source Type",
            ["WEBSITE", "RSS", "JOBS", "NEWS", "PRODUCTHUNT"],
            label_visibility="collapsed"
        )

    st.divider()

    # Get moves with filters applied
    try:
        moves = db.get_all_moves()

        # Apply filters
        if competitor_filter:
            moves = [m for m in moves if m["competitor_name"] in competitor_filter]
        if threat_filter:
            moves = [m for m in moves if m["threat_level"] in threat_filter]
        if source_filter:
            moves = [m for m in moves if m["source_type"] in source_filter]
        if status_filter:
            moves = [m for m in moves if m["validation_status"] in status_filter]

        # Separate by status
        auto_detected = [m for m in moves if m["validation_status"] == "AUTO_DETECTED"]
        validated = [m for m in moves if m["validation_status"] == "VALIDATED"]
        dismissed = [m for m in moves if m["validation_status"] == "DISMISSED"]

        # Display stats
        stats_cols = st.columns(3)
        with stats_cols[0]:
            st.metric("Auto-Detected (Awaiting Review)", len(auto_detected))
        with stats_cols[1]:
            st.metric("Validated", len(validated))
        with stats_cols[2]:
            st.metric("Dismissed", len(dismissed))

        st.divider()

        # AUTO_DETECTED moves (main workflow)
        if auto_detected:
            st.subheader(f"🔔 Moves Awaiting Validation ({len(auto_detected)})")

            for idx, move in enumerate(auto_detected):
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        # Move header
                        st.markdown(f"### {move['title']}")
                        st.write(f"**Competitor:** {move['competitor_name']}")

                        # Move details
                        detail_cols = st.columns(4)
                        with detail_cols[0]:
                            threat_color = {
                                "HIGH": "🔴",
                                "MEDIUM": "🟡",
                                "LOW": "🟢"
                            }.get(move["threat_level"], "⚪")
                            st.write(f"{threat_color} **Threat:** {move['threat_level']}")

                        with detail_cols[1]:
                            st.write(f"**Source:** {move['source_type']}")

                        with detail_cols[2]:
                            st.write(f"**Confidence:** {move['confidence'] * 100:.0f}%")

                        with detail_cols[3]:
                            if move["opportunity"]:
                                st.write("✓ **Opportunity**")
                            else:
                                st.write("- Not an opportunity")

                        # Description
                        st.write(f"**Description:** {move['description']}")

                        # Source URL if available
                        if move.get("source_url"):
                            st.markdown(f"🔗 [View Source]({move['source_url']})")

                        # Detected date
                        st.caption(f"Detected: {move['collected_at']}")

                    with col2:
                        # Action buttons
                        st.write("**Actions:**")

                        validate_btn = st.button(
                            "✅ Validate",
                            key=f"validate_{move['id']}",
                            use_container_width=True
                        )

                        dismiss_btn = st.button(
                            "❌ Dismiss",
                            key=f"dismiss_{move['id']}",
                            use_container_width=True
                        )

                        if validate_btn:
                            db.validate_move(move["id"])
                            st.success("Move validated!")
                            st.rerun()

                        if dismiss_btn:
                            db.dismiss_move(move["id"])
                            st.info("Move dismissed")
                            st.rerun()

        else:
            if "AUTO_DETECTED" in status_filter:
                st.info("✨ No moves awaiting validation. Great job staying on top of competitive intelligence!")

        st.divider()

        # VALIDATED moves (confirmed intelligence)
        if validated and ("VALIDATED" in status_filter or not status_filter):
            st.subheader(f"✅ Validated Moves ({len(validated)})")

            # Show as table for quick scanning
            validated_df = pd.DataFrame([
                {
                    "Date": move["validated_at"][:10] if move.get("validated_at") else move["collected_at"][:10],
                    "Competitor": move["competitor_name"],
                    "Title": move["title"],
                    "Threat": move["threat_level"],
                    "Source": move["source_type"],
                    "Dimension": move["dimension"]
                }
                for move in sorted(validated, key=lambda x: x["collected_at"], reverse=True)
            ])

            st.dataframe(validated_df, use_container_width=True, hide_index=True)

        # DISMISSED moves (reference for filtering patterns)
        if dismissed and "DISMISSED" in status_filter:
            with st.expander(f"📁 Dismissed Moves ({len(dismissed)})"):
                dismissed_df = pd.DataFrame([
                    {
                        "Date": move["collected_at"][:10],
                        "Competitor": move["competitor_name"],
                        "Title": move["title"],
                        "Source": move["source_type"]
                    }
                    for move in sorted(dismissed, key=lambda x: x["collected_at"], reverse=True)
                ])

                st.dataframe(dismissed_df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Error loading moves: {e}")


if __name__ == "__main__":
    show()
