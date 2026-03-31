"""
Lead Sync — Automated CRM Lead Management
Validates and syncs lead data from CSV to HubSpot CRM
"""

import re
import csv
import sys
import os
import requests
from time import sleep
from dotenv import load_dotenv

load_dotenv()


def main():
    print("Lead Sync — Starting...\n")

    # Read leads from CSV
    try:
        with open("sample_leads.csv", "r") as file:
            reader = csv.DictReader(file)
            leads = list(reader)
    except FileNotFoundError:
        print("Error: sample_leads.csv not found.")
        sys.exit(1)

    print(f"Found {len(leads)} leads to process.\n")

    successful = 0
    failed = 0

    for lead in leads:
        name = lead.get("name", "Unknown")
        print(f"Processing: {name}")

        validated = validate_lead(lead)

        if validated is None:
            print(f"  ✗ Validation failed — skipping.\n")
            failed += 1
            continue

        payload = format_hubspot_payload(validated)
        success = send_to_hubspot(payload)

        if success:
            print(f"  ✓ Synced successfully.\n")
            successful += 1
        else:
            print(f"  ✗ Sync failed.\n")
            failed += 1

        sleep(0.1)  # Respect HubSpot rate limit (100 req / 10s)

    print("=" * 45)
    print(f"Sync complete — {successful} succeeded, {failed} failed.")
    print("=" * 45)


def validate_lead(lead_dict):
    """
    Validates lead data against formatting and regional rules.

    Args:
        lead_dict (dict): Raw lead data from CSV row.

    Returns:
        dict: Cleaned lead data if valid, None if invalid.
    """
    name    = lead_dict.get("name", "").strip()
    email   = lead_dict.get("email", "").strip()
    phone   = lead_dict.get("phone", "").strip()
    company = lead_dict.get("company", "").strip()

    # Email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        print(f"  Invalid email: {email}")
        return None

    # UAE mobile validation (+971 followed by valid mobile prefix and 7 digits)
    uae_phone_pattern = r'^\+971(50|52|54|55|56|58)\d{7}$'
    if not re.match(uae_phone_pattern, phone):
        print(f"  Invalid UAE phone: {phone} (expected +971XXXXXXXXX)")
        return None

    return {
        "name":    name,
        "email":   email,
        "phone":   phone,
        "company": company
    }


def format_hubspot_payload(cleaned_data):
    """
    Formats validated lead data into HubSpot API payload structure.

    Args:
        cleaned_data (dict): Validated lead data.

    Returns:
        dict: HubSpot-compliant contact payload.
    """
    name_parts = cleaned_data["name"].split(" ", 1)
    firstname  = name_parts[0]
    lastname   = name_parts[1] if len(name_parts) > 1 else ""

    return {
        "properties": {
            "email":     cleaned_data["email"],
            "firstname": firstname,
            "lastname":  lastname,
            "phone":     cleaned_data["phone"],
            "company":   cleaned_data["company"]
        }
    }


def send_to_hubspot(payload):
    """
    Sends a formatted contact payload to the HubSpot CRM API.

    Args:
        payload (dict): HubSpot-formatted contact data.

    Returns:
        bool: True if contact was created or already exists, False on error.
    """
    api_token = os.getenv("HUBSPOT_API_TOKEN")

    # Test mode — no token provided
    if not api_token:
        print(f"  [Test Mode] Would sync: {payload['properties']['email']}")
        return True

    url     = "https://api.hubapi.com/crm/v3/objects/contacts"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type":  "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 201:    # Created
            return True
        elif response.status_code == 409:  # Conflict — contact already exists
            print(f"  Contact already exists in HubSpot.")
            return True
        else:
            print(f"  API Error: {response.status_code} — {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"  Network error: {e}")
        return False


if __name__ == "__main__":
    main()
