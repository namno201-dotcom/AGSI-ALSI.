import requests, json, os
from datetime import date

API_KEY = os.environ["AGSI_API_KEY"]
COUNTRIES = [("DE","Đức"), ("BE","Bỉ"), ("NL","Hà Lan")]
HEADERS = {"x-key": API_KEY}

START_DATE = "2026-01-01"

def fetch(code, **params):
    r = requests.get("https://agsi.gie.eu/api", params={"country": code, **params}, headers=HEADERS)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(f"{code}: {data.get('message')}")
    return data["data"]

today = date.today().isoformat()

result = {"generated_at": today, "from_date": START_DATE, "latest": {}, "series": {}}
for code, name in COUNTRIES:
    result["latest"][code] = fetch(code, reverse="true", size="1")[0]
    result["series"][code] = fetch(code, **{"from": START_DATE, "to": today, "size": "300"})

with open("data.json", "w") as f:
    json.dump(result, f)
