def calculate_score(properties: dict) -> int:
    score = 0

    source = properties.get("lead_source_custom", "")
    if source == "referral":
        score += 40
    elif source == "google_ads":
        score += 30
    elif source == "facebook_ads":
        score += 20
    elif source == "organic":
        score += 10

    if properties.get("first_deal_created_date"):
        score += 30

    stage = properties.get("lifecyclestage", "")
    if stage == "opportunity":
        score += 30
    elif stage == "lead":
        score += 10

    return score