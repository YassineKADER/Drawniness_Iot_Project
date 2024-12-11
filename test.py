import requests

BASE_URL = "http://127.0.0.1:8000"  # Change to the actual server URL if hosted remotely


def test_event_endpoint():
    url = f"{BASE_URL}/event/"
    payload = {
        "user_id": "12345",
        "event_type": "drowsiness_detected",
        "confidence": 0.95,
    }
    try:
        response = requests.post(url, json=payload)
        print("Event Endpoint Response:", response.status_code, response.json())
    except Exception as e:
        print("Error testing event endpoint:", e)


def test_sos_endpoint():
    url = f"{BASE_URL}/sos/"
    payload = {
        "user_id": "12345",
        "event_id": "67890",
        "message": "Driver is in distress",
        "latitude": 34.0522,
        "longitude": -118.2437,
    }
    try:
        response = requests.post(url, json=payload)
        print("SOS Endpoint Response:", response.status_code, response.json())
    except Exception as e:
        print("Error testing SOS endpoint:", e)


if __name__ == "__main__":
    print("Testing Event Endpoint...")
    test_event_endpoint()

    print("\nTesting SOS Endpoint...")
    test_sos_endpoint()
