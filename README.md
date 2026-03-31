# Lead Sync — Automated CRM Lead Management

### CSV validation · HubSpot API integration · UAE Customer Data Localization

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square)
![HubSpot](https://img.shields.io/badge/HubSpot-CRM%20API-FF7A59?style=flat-square)
![pytest](https://img.shields.io/badge/pytest-tested-0A9EDC?style=flat-square)

---

## Overview

A Python automation tool that reads lead data from a CSV file, validates it against formatting and regional business rules, and syncs clean records directly to HubSpot CRM via API — replacing a manual data entry process that was slow and error-prone.

Each lead passes through a validation pipeline before any API call is made, ensuring only high-quality data enters the CRM.

---

## Business Context

Lead data is often collected through forms, spreadsheets, event registration tools, or exported reports. CSV remains the most common interchange format because it is widely supported and does not depend on direct API access from the source system.

A CSV file on its own is only a transport format. The value comes from converting that raw export into structured CRM records that can be used immediately by sales and operations teams.

**This tool automates that handoff:**

* Reads raw lead data from CSV
* Validates email format and UAE mobile number standards
* Rejects invalid records with clear logging — without stopping the batch
* Formats data to HubSpot's API specification
* Creates contacts directly in HubSpot CRM
* Respects API rate limits for reliable bulk processing

The practical benefit is reduced manual handling between lead capture and CRM entry. Instead of exporting a file, opening HubSpot, importing the data, mapping columns, and correcting issues row by row, the workflow handles validation and sync automatically in seconds.

---

## Architecture

```text
sample_leads.csv
      │
      ▼
  validate_lead()
  ├── Email format check (regex)
  └── UAE phone format check (regex · +971 mobile prefixes)
      │
      ▼
  format_hubspot_payload()
  └── Structures data to HubSpot API spec
      │
      ▼
  send_to_hubspot()
  ├── POST /crm/v3/objects/contacts
  ├── 201 Created → success
  ├── 409 Conflict → already exists, skip
  └── Other → log error, continue batch
```

---

## Tech Stack

| Layer           | Tools                |
| --------------- | -------------------- |
| Language        | Python 3.10+         |
| CRM Integration | HubSpot CRM API (v3) |
| Validation      | Python `re` (regex)  |
| Testing         | pytest               |
| Environment     | python-dotenv        |

---

## Key Design Decisions

**Validation before API calls**
Every lead is validated locally before any network request is made. Invalid records are logged and skipped — a single bad row never interrupts the rest of the batch.

**UAE-specific phone validation**
Phone numbers are validated against UAE mobile standards: `+971` followed by a valid mobile prefix (50, 52, 54, 55, 56, 58) and 7 digits. Landlines, invalid prefixes, and malformed numbers are rejected. This keeps the tool aligned with the intended regional format.

**Environment variable token management**
The HubSpot API token is loaded from a `.env` file via `python-dotenv`, keeping credentials out of source code. If no token is present, the script runs in test mode — logging what would have been sent without making any API calls.

**Rate limit handling**
A 100ms delay between requests stays within HubSpot's limit of 100 requests per 10 seconds, ensuring consistent execution at scale without triggering throttling.

**Non-destructive error handling**
`409 Conflict` responses (duplicate contacts) are treated as safe skips rather than failures. The script continues processing and reports an accurate final count.

---

## Setup

**1. Clone the repo and install dependencies**

```bash
pip install -r requirements.txt
```

**2. Add your HubSpot API token**
Create a `.env` file in the project root:

```env
HUBSPOT_API_TOKEN=your_token_here
```

To get a token: HubSpot → Settings → Integrations → Private Apps → Create App → copy the token.

**3. Run the sync**

```bash
python lead_sync.py
```

**4. Run tests**

```bash
pytest test_lead_sync.py -v
```

> If no `.env` file is present, the script runs in **test mode** — no data is sent to HubSpot.

---

## Sample Output

```text
Lead Sync — Starting...

Found 12 leads to process.

Processing: Amr Sherif
  ✓ Synced successfully.

Processing: Fatima Rashid
  Invalid email: fatima.rashid@INVALID
  ✗ Validation failed — skipping.

Processing: Khalid Nasser
  Invalid UAE phone: +97141234567 (expected +971XXXXXXXXX)
  ✗ Validation failed — skipping.

Processing: Faisal Salamah
  ✓ Synced successfully.

...

=============================================
Sync complete — 9 succeeded, 3 failed.
=============================================
```

---

## Repository Structure

```text
├── lead_sync.py          # Main script — validation, formatting, API sync
├── test_lead_sync.py     # pytest test suite
├── sample_leads.csv      # Dummy lead data for testing
├── requirements.txt      # Dependencies
├── .env.example          # Environment variable template
└── README.md
```

---

## Demo

📺 [Watch the demo on YouTube](#) ← *(link coming)*

The demo runs the full pipeline against `sample_leads.csv`, showing validation rejections, successful syncs, and the resulting contacts appearing live in HubSpot CRM.

## Limitations & Roadmap

This tool is functional for bulk lead validation and CRM syncing in a UAE context. The following enhancements would be required for full production deployment:

* **Update logic** — currently, existing contacts (`409 Conflict`) are skipped rather than updated. A production version would perform a lookup and patch the existing record
* **Pre-flight deduplication** — duplicate detection before the API call to reduce unnecessary network requests
* **UAE landline support** — extends phone validation to accept landline formats (`+9714xxxxxxx`) for B2B use cases
* **Arabic name handling** — robust name parsing for Arabic-script input
* **Output reporting** — export a post-run CSV log of successful syncs, failures, and skips
* **Encoding handling** — explicit UTF-8 enforcement to support Arabic characters in CSV input

## Data & Privacy

All leads in `sample_leads.csv` are entirely fictitious. Names, emails, phone numbers, and company names are randomly generated and do not correspond to any real individual or organization. This project was developed in the UAE, where data privacy is governed by Federal Decree-Law No. 45 of 2021. No real personal data was used at any stage of development or testing.

