import json
import urllib.request
import urllib.error

payload = {
    "temp": 25.5,
    "humidity": 70.0,
    "moisture": 40.0,
    "dryness": 20.0,
    "crop_details": {
        "Item": "Potatoes",
        "average_rain_fall_mm_per_year": 1485.0,
        "avg_temp": 16.37,
        "crop_img": "graph.png",
        "current_date": "2025-11-14",
        "disease_detect": False,
        "growth": "vegetative",
        "lat": 11.42,
        "lon": 11.56,
        "pesticides_tonnes": 121.0,
        "soil_img": "https://www.eurokidsindia.com/blog/wp-content/uploads/2023/11/different-types-of-soils-and-their-charachterstics-870x570.jpg",
        "sowing_date": "2025-08-01",
        "storage_availability": "No",
    },
}

req = urllib.request.Request(
    "http://127.0.0.1:8000/generate-report",
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)

try:
    with urllib.request.urlopen(req, timeout=180) as resp:
        print(resp.status)
        print(resp.read().decode())
except urllib.error.HTTPError as e:
    print("HTTP", e.code)
    print(e.read().decode())
except Exception:
    import traceback
    traceback.print_exc()
