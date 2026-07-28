import requests, json, os
from datetime import date

API_KEY = os.environ["AGSI_API_KEY"]
COUNTRIES = [("DE", "Germany"), ("BE", "Belgium"), ("NL", "Netherlands")]
HEADERS = {"x-key": API_KEY}
START_DATE = "2026-01-01"

def fetch(base_url, code, **params):
    r = requests.get(base_url, params={"country": code, **params}, headers=HEADERS)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(f"{base_url} {code}: {data.get('message')}")
    return data["data"]

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
    result["latest"][code] = fetch("https://agsi.gie.eu/api", code, reverse="true", size="1")[0]
    result["series"][code] = fetch(
        "https://agsi.gie.eu/api", code, **{"from": START_DATE, "to": today, "size": "300"}
    )

    # ALSI - LNG terminals
    try:
        result["alsi_latest"][code] = fetch("https://alsi.gie.eu/api", code, reverse="true", size="1")[0]
        result["alsi_series"][code] = fetch(
            "https://alsi.gie.eu/api", code, **{"from": START_DATE, "to": today, "size": "300"}
        )
    except Exception as e:
        # some countries may not operate an LNG terminal - don't fail the whole run
        print(f"ALSI fetch failed for {code}: {e}")
        result["alsi_latest"][code] = None
        result["alsi_series"][code] = []

with open("data.json", "w") as f:
    json.dump(result, f)

print("Done. Countries fetched:", [c for c, _ in COUNTRIES])
