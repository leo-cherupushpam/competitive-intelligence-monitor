"""
Intelligence Engine — AI-powered analysis of raw competitive data.
Extracts structured moves from raw content, generates threat assessments, and identifies opportunities.
"""

import json
import re
from openai import OpenAI
import os


def get_secret(key: str) -> str:
    """Read a secret from env vars, Streamlit Cloud secrets, or the database."""
    # 1. Environment variable (local dev)
    value = os.getenv(key)
    if value:
        return value

    # 2. Streamlit Cloud secrets
    try:
        import streamlit as st
        value = st.secrets.get(key)
        if value:
            return value
    except Exception:
        pass

    # 3. Database (saved via Settings page in the app)
    try:
        import db
        value = db.get_setting(key)
        if value:
            return value
    except Exception:
        pass

    return None


def get_client():
    """Get OpenAI client — checks env vars and Streamlit Cloud secrets."""
    api_key = get_secret("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def extract_move_from_raw_data(raw_content: str, source_type: str, competitor_name: str = None) -> dict:
    """
    Use AI to extract structured competitive move from raw data.
    Returns: {title, description, dimension, threat_level, opportunity, confidence_score}
    """
    client = get_client()
    if not client:
        return fallback_extract_move(raw_content, source_type)

    prompt = f"""
You are a product manager analyzing competitive intelligence.

Source Type: {source_type}
Competitor: {competitor_name or 'Unknown'}
Raw Data:
{raw_content[:500]}  # Limit to 500 chars to save tokens

Extract a competitive move from this data. Respond ONLY with valid JSON (no markdown):
{{
    "title": "Brief title (max 50 chars) of the competitive move",
    "description": "1-2 sentence description of what they did",
    "dimension": "One of: FEATURE, PRICING, POSITIONING, HIRING, NEWS",
    "threat_level": "LOW, MEDIUM, or HIGH",
    "is_opportunity": true/false (should we copy this?),
    "confidence": 0.0 to 1.0 (how confident are you this is a real move?)
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-5-nano-2025-08-07",
            messages=[
                {"role": "system", "content": "You are a product manager analyzing competitive intelligence. Respond ONLY with valid JSON, no markdown or explanation."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=300
        )

        result_text = response.choices[0].message.content.strip()
        # Remove markdown code blocks if present
        result_text = re.sub(r'^```json\n?', '', result_text)
        result_text = re.sub(r'\n?```$', '', result_text)

        move = json.loads(result_text)
        return {
            "title": move.get("title", "Untitled Move")[:50],
            "description": move.get("description", ""),
            "dimension": move.get("dimension", "NEWS").upper(),
            "threat_level": move.get("threat_level", "MEDIUM").upper(),
            "opportunity": move.get("is_opportunity", False),
            "confidence": min(max(float(move.get("confidence", 0.7)), 0.0), 1.0)
        }
    except Exception as e:
        print(f"AI extraction error: {e}")
        return fallback_extract_move(raw_content, source_type)


def fallback_extract_move(raw_content: str, source_type: str) -> dict:
    """
    Rule-based fallback when OpenAI is unavailable.
    Uses keyword matching to classify moves.
    """
    content_lower = raw_content.lower()

    # Dimension detection
    if any(word in content_lower for word in ["feature", "launch", "released", "new", "launch", "update"]):
        dimension = "FEATURE"
    elif any(word in content_lower for word in ["price", "pricing", "discount", "cost", "$", "upgrade"]):
        dimension = "PRICING"
    elif any(word in content_lower for word in ["announc", "position", "brand", "rebrand", "message"]):
        dimension = "POSITIONING"
    elif any(word in content_lower for word in ["hiring", "job", "position", "recruiting", "team"]):
        dimension = "HIRING"
    else:
        dimension = "NEWS"

    # Threat detection
    if any(word in content_lower for word in ["major", "critical", "significant", "revolutionary", "breakthrough"]):
        threat_level = "HIGH"
    elif any(word in content_lower for word in ["update", "minor", "improvement", "enhancement"]):
        threat_level = "LOW"
    else:
        threat_level = "MEDIUM"

    # Extract title from first line or first 50 chars
    title = raw_content.split('\n')[0][:50].strip() or "Competitive Move"

    return {
        "title": title,
        "description": raw_content[:100] + "..." if len(raw_content) > 100 else raw_content,
        "dimension": dimension,
        "threat_level": threat_level,
        "opportunity": threat_level != "HIGH",
        "confidence": 0.6
    }


def generate_insight(move_title: str, move_description: str, threat_level: str, dimension: str) -> dict:
    """
    Generate strategic insight and recommendation.
    Returns: {summary, implication, recommended_response}
    """
    client = get_client()
    if not client:
        return fallback_generate_insight(move_title, threat_level, dimension)

    prompt = f"""
You are a product strategist. Given a competitive move, generate a strategic insight.

Move: {move_title}
Description: {move_description}
Threat Level: {threat_level}
Dimension: {dimension}

Respond ONLY with valid JSON (no markdown):
{{
    "summary": "1-sentence summary of why this matters (max 100 chars)",
    "implication": "Strategic implication for our product strategy",
    "recommended_action": "What should we do about this move?"
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-5-nano-2025-08-07",
            messages=[
                {"role": "system", "content": "You are a product strategist. Respond ONLY with valid JSON, no markdown."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=250
        )

        result_text = response.choices[0].message.content.strip()
        result_text = re.sub(r'^```json\n?', '', result_text)
        result_text = re.sub(r'\n?```$', '', result_text)

        insight = json.loads(result_text)
        return {
            "summary": insight.get("summary", move_title),
            "implication": insight.get("implication", "Strategic competitive move"),
            "recommended_action": insight.get("recommended_action", "Monitor and assess impact")
        }
    except Exception as e:
        print(f"Insight generation error: {e}")
        return fallback_generate_insight(move_title, threat_level, dimension)


def fallback_generate_insight(move_title: str, threat_level: str, dimension: str) -> dict:
    """Rule-based insight generation."""

    threat_multiplier = {"HIGH": 3, "MEDIUM": 1.5, "LOW": 0.5}
    severity = threat_multiplier.get(threat_level, 1)

    implication_map = {
        "FEATURE": f"Competitor is advancing {dimension.lower()}. Consider feature parity assessment.",
        "PRICING": f"Pricing strategy shift detected. Review competitive positioning.",
        "POSITIONING": f"Competitor repositioning. Monitor customer perception impact.",
        "HIRING": f"Team expansion in strategic area. Talent competition increasing.",
        "NEWS": f"Market announcement. Assess strategic implications."
    }

    return {
        "summary": move_title[:100],
        "implication": implication_map.get(dimension, "Competitive activity detected"),
        "recommended_action": f"{'Urgent action needed' if threat_level == 'HIGH' else 'Monitor closely' if threat_level == 'MEDIUM' else 'Track and assess'}"
    }


def analyze_roadmap_impact(move_title: str, our_roadmap_features: list = None) -> dict:
    """
    Analyze how a competitive move impacts our roadmap.
    Returns: {signal_type, reasoning, confidence_score}
    """
    client = get_client()
    if not client:
        return {"signal_type": "MONITOR", "reasoning": "No AI analysis available", "confidence": 0.5}

    roadmap_text = ", ".join(our_roadmap_features) if our_roadmap_features else "No roadmap provided"

    prompt = f"""
You are a product strategist evaluating competitive threats against our roadmap.

Competitor Move: {move_title}
Our Planned Features: {roadmap_text}

Analyze impact. Respond ONLY with JSON (no markdown):
{{
    "signal_type": "One of: VALIDATES (move confirms we're right), INVALIDATES (move makes feature less important), ACCELERATES (we need to ship faster), DEPRIORITIZES (we can delay this feature), or MONITOR (watch but no action yet)",
    "reasoning": "Brief explanation (max 150 chars)",
    "confidence": 0.0 to 1.0
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-5-nano-2025-08-07",
            messages=[
                {"role": "system", "content": "You are a product strategist. Respond ONLY with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=200
        )

        result_text = response.choices[0].message.content.strip()
        result_text = re.sub(r'^```json\n?', '', result_text)
        result_text = re.sub(r'\n?```$', '', result_text)

        signal = json.loads(result_text)
        return {
            "signal_type": signal.get("signal_type", "MONITOR").upper(),
            "reasoning": signal.get("reasoning", ""),
            "confidence": min(max(float(signal.get("confidence", 0.7)), 0.0), 1.0)
        }
    except Exception as e:
        print(f"Roadmap impact analysis error: {e}")
        return {"signal_type": "MONITOR", "reasoning": "Impact assessment needed", "confidence": 0.5}


def find_competitors(company_name: str, market_segment: str = None) -> list:
    """
    Use AI to find likely competitors for a given company.
    Returns: [{"name": "CompetitorName", "website": "url"}, ...]
    """
    client = get_client()
    if not client:
        return []

    prompt = f"""
You are a market research analyst. Given a company, identify 5 likely competitors.

Company: {company_name}
{f"Market Segment: {market_segment}" if market_segment else ""}

Respond ONLY with valid JSON (no markdown):
{{
    "competitors": [
        {{
            "name": "Competitor Name",
            "website": "https://www.competitor.com",
            "threat_baseline": "HIGH/MEDIUM/LOW",
            "reason": "Why they're a competitor"
        }}
    ]
}}

Focus on direct competitors in the same market/product category.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-5-nano-2025-08-07",
            messages=[
                {"role": "system", "content": "You are a market research analyst. Respond ONLY with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=500
        )

        result_text = response.choices[0].message.content.strip()
        result_text = re.sub(r'^```json\n?', '', result_text)
        result_text = re.sub(r'\n?```$', '', result_text)

        data = json.loads(result_text)
        return data.get("competitors", [])

    except Exception as e:
        raise


if __name__ == "__main__":
    # Test extraction
    test_data = "HubSpot released a new AI email writer feature in their platform. Customers can now compose emails with AI assistance."
    result = extract_move_from_raw_data(test_data, "WEBSITE", "HubSpot")
    print("Extracted move:", json.dumps(result, indent=2))
