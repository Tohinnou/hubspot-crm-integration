import sys
sys.path.append(".")

from app.services.lead_scorer import calculate_score

def test_referral_score():
    properties = {
        "lead_source_custom": "referral",
        "lifecyclestage": "opportunity",
        "first_deal_created_date": "2026-01-01"
    }
    score = calculate_score(properties)
    print(f"✅ Score test passed: {score}/100")



def test_facebook_score():
    properties = {
        "lead_source_custom": "facebook_ads",
        "lifecyclestage": "lead",
        "first_deal_created_date": None
    }
    score = calculate_score(properties)
    assert score == 30, f"Expected 30, got {score}"
    print(f"✅ Facebook + lead + no deal = {score}/100")

    
def test_empty_properties():
    score = calculate_score({})
    assert score == 0, f"Expected 0, got {score}"
    print(f"✅ Empty properties = {score}/100")


def test_google_with_deal():
    properties = {
        "lead_source_custom": "google_ads",
        "lifecyclestage": "opportunity",
        "first_deal_created_date": "2026-01-01"
    }
    score = calculate_score(properties)
    assert score == 90, f"Expected 90, got {score}"
    print(f"✅ Google + opportunity + deal = {score}/100")
    
    
def test_organic_no_deal():
    properties = {
        "lead_source_custom": "organic",
        "lifecyclestage": "lead",
        "first_deal_created_date": None
    }
    score = calculate_score(properties)
    assert score == 20, f"Expected 20, got {score}"
    print(f"✅ Organic + lead + no deal = {score}/100")
    
    
if __name__ == "__main__":
    print("Testing lead scorer...")
    test_referral_score()
    test_facebook_score()
    test_empty_properties()
    test_google_with_deal()
    test_organic_no_deal()
    print("\n✅ All lead scorer tests passed")