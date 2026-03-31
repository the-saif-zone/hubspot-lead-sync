"""
Tests for lead_sync.py — validation and payload formatting logic
"""

import pytest
from lead_sync import validate_lead, format_hubspot_payload


# --- validate_lead ---

def test_valid_lead():
    lead = {
        "name": "Ahmed Al Mansoori",
        "email": "ahmed@example.com",
        "phone": "+971501234567",
        "company": "Gulf Ventures"
    }
    result = validate_lead(lead)
    assert result is not None
    assert result["email"] == "ahmed@example.com"


def test_invalid_email_missing_at():
    lead = {
        "name": "Sara Al Farsi",
        "email": "saraexample.com",
        "phone": "+971521234567",
        "company": "Al Noor Group"
    }
    assert validate_lead(lead) is None


def test_invalid_email_missing_domain():
    lead = {
        "name": "James Whitfield",
        "email": "james@",
        "phone": "+971551234567",
        "company": "Orion Consulting"
    }
    assert validate_lead(lead) is None


def test_invalid_phone_landline():
    """UAE landline numbers (+9714...) should be rejected"""
    lead = {
        "name": "Khalid Nasser",
        "email": "khalid@example.com",
        "phone": "+97141234567",
        "company": "Abu Dhabi Logistics"
    }
    assert validate_lead(lead) is None


def test_invalid_phone_prefix():
    """Invalid mobile prefix (+97153...) should be rejected"""
    lead = {
        "name": "Fatima Rashid",
        "email": "fatima@example.com",
        "phone": "+971531234567",
        "company": "Dubai Holdings"
    }
    assert validate_lead(lead) is None


def test_valid_all_uae_mobile_prefixes():
    """All valid UAE mobile prefixes should pass"""
    prefixes = ["50", "52", "54", "55", "56", "58"]
    for prefix in prefixes:
        lead = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": f"+971{prefix}1234567",
            "company": "Test Co"
        }
        assert validate_lead(lead) is not None, f"Prefix {prefix} should be valid"


def test_whitespace_stripped():
    lead = {
        "name": "  Priya Sharma  ",
        "email": "  priya@example.com  ",
        "phone": "+971561234567",
        "company": "  Nexus Partners  "
    }
    result = validate_lead(lead)
    assert result["name"] == "Priya Sharma"
    assert result["email"] == "priya@example.com"


# --- format_hubspot_payload ---

def test_payload_structure():
    data = {
        "name": "Ahmed Al Mansoori",
        "email": "ahmed@example.com",
        "phone": "+971501234567",
        "company": "Gulf Ventures"
    }
    payload = format_hubspot_payload(data)
    assert "properties" in payload
    assert payload["properties"]["firstname"] == "Ahmed"
    assert payload["properties"]["lastname"] == "Al Mansoori"
    assert payload["properties"]["email"] == "ahmed@example.com"


def test_single_name_no_lastname():
    """Single-word names should set lastname to empty string"""
    data = {
        "name": "Madonna",
        "email": "madonna@example.com",
        "phone": "+971501234567",
        "company": "Pop Inc"
    }
    payload = format_hubspot_payload(data)
    assert payload["properties"]["firstname"] == "Madonna"
    assert payload["properties"]["lastname"] == ""


def test_multi_part_lastname():
    """Full name should split on first space only"""
    data = {
        "name": "Sara Al Farsi",
        "email": "sara@example.com",
        "phone": "+971521234567",
        "company": "Al Noor Group"
    }
    payload = format_hubspot_payload(data)
    assert payload["properties"]["firstname"] == "Sara"
    assert payload["properties"]["lastname"] == "Al Farsi"
