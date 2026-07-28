import requests, json, os
from datetime import date

API_KEY = os.environ["AGSI_API_KEY"]
COUNTRIES = [("DE", "Germany"), ("BE", "Belgium"), ("NL", "Netherlands")]
HEADERS = {"x-key": API_KEY}
START_DATE = "2026-01-01"


def fetch_paginated(base_url, code, **params):
    """Fetch all pages for a date range that might exceed 300 rows."""
    all_rows = []
    page = 1
    while True:
        r = requests.get(
            base_url,
            params={"country": code, "size": "300", "page": str(page), **params},
            headers=HEADERS,
        )
        r.raise_for_status()
        data = r.json()
        if data.get("error"):
            raise RuntimeError(f"{base_url} {code}: {data.get('message')}")
        all_rows.extend(data["data"])
        if page >= data.get("last_page", 1):
            break
        page += 1
    return all_rows


def fetch_latest(base_url, code):
    r = requests.get(
        base_url,
        params={"country": code, "reverse": "true", "size": "1"},
        headers=HEADERS,
    )
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(f"{base_url} {code}: {data.get('message')}")
    return data["data"][0]


today = date.today().isoformat()

result = {
    "generated_at": today,
    "from_date": START_DATE,
    "latest": {},
    "series": {},
    "alsi_latest": {},
    "alsi_series": {},
}

for code, name in COUNTRIES:
    # AGSI - underground gas storage
    result["latest"][code] = fetch_latest("https://agsi.gie.eu/api", code)
    result["series"][code] = fetch_paginated(
        "https://agsi.gie.eu/api", code, **{"from": START_DATE, "to": today}
    )

    # ALSI - LNG terminals
    try:
        result["alsi_latest"][code] = fetch_latest("https://alsi.gie.eu/api", code)
        result["alsi_series"][code] = fetch_paginated(
            "https://alsi.gie.eu/api", code, **{"from": START_DATE, "to": today}
        )
    except Exception as e:
        # some countries may not operate an LNG terminal - don't fail the whole run
        print(f"ALSI fetch failed for {code}: {e}")
        result["alsi_latest"][code] = None
        result["alsi_series"][code] = []

with open("data.json", "w") as f:
    json.dump(result, f)

print("Done. Countries fetched:", [c for c, _ in COUNTRIES])
