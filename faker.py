import influxdb
import uuid
import time
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize InfluxDB client
client = influxdb.InfluxDBClient(
    host=os.getenv("INFLUXDB_HOST"),
    port=int(os.getenv("INFLUXDB_PORT", 8086)),
    username=os.getenv("INFLUXDB_USERNAME"),
    password=os.getenv("INFLUXDB_PASSWORD"),
    database=os.getenv("INFLUXDB_DATABASE"),
)

# User ID to generate data for
user_id = "driver_955f8457-4d6f-4d0f-91af-89cea88a76cf"

# Start time for data generation
start_time = datetime.utcnow()

# List of cities/regions in Morocco and Europe with approximate latitudes and longitudes
morocco_locations = [
    {"city": "Casablanca", "latitude": 33.5731, "longitude": -7.5898},
    {"city": "Rabat", "latitude": 34.020882, "longitude": -6.84165},
    {"city": "Marrakech", "latitude": 31.6295, "longitude": -7.9811},
    {"city": "Fes", "latitude": 34.0333, "longitude": -5.0000},
    {"city": "Tangier", "latitude": 35.7676, "longitude": -5.7998},
]

europe_locations = [
    {"city": "Paris", "latitude": 48.8566, "longitude": 2.3522},
    {"city": "Berlin", "latitude": 52.5200, "longitude": 13.4050},
    {"city": "London", "latitude": 51.5074, "longitude": -0.1278},
    {"city": "Madrid", "latitude": 40.4168, "longitude": -3.7038},
    {"city": "Rome", "latitude": 41.9028, "longitude": 12.4964},
]

# Combine both regions
all_locations = morocco_locations + europe_locations


# Function to generate random event data with an incremental timestamp
def generate_event_data(current_time):
    event_id = str(uuid.uuid4())
    event_type = random.choice(["sleep", "drowsy", "active", "inactive"])
    confidence = random.uniform(0.5, 1.0)  # Random confidence between 0.5 and 1.0
    json_body = [
        {
            "measurement": "events",
            "tags": {
                "user_id": user_id,
                "event_id": event_id,
                "event_type": event_type,
            },
            "fields": {"confidence": confidence},
            "time": int(current_time.timestamp() * 1e9),  # Time in nanoseconds
        }
    ]
    return json_body


# Function to generate random SOS data with an incremental timestamp
def generate_sos_data(event_id, current_time):
    sos_id = str(uuid.uuid4())
    message = random.choice(["help", "emergency", "assistance needed", "urgent"])

    # Randomly select a location from the list
    location = random.choice(all_locations)

    # Add random small deviation (between -0.01 and 0.01) to simulate variation from the city center
    lat_deviation = random.uniform(-0.1, 0.1)
    lon_deviation = random.uniform(-0.1, 0.1)

    # Apply deviations to the city's latitude and longitude
    latitude = location["latitude"] + lat_deviation
    longitude = location["longitude"] + lon_deviation

    json_body = [
        {
            "measurement": "sos",
            "tags": {"user_id": user_id, "event_id": event_id, "sos_id": sos_id},
            "fields": {
                "message": message,
                "latitude": latitude,
                "longitude": longitude,
            },
            "time": int(current_time.timestamp() * 1e9),  # Time in nanoseconds
        }
    ]
    return json_body


# Insert a large number of events and SOS messages for the user
def insert_data(num_events=1000, interval_seconds=60):
    global start_time
    for i in range(num_events):
        current_time = start_time + timedelta(seconds=i * interval_seconds)

        # Insert random event data
        event_data = generate_event_data(current_time)
        client.write_points(event_data)

        # Insert SOS data associated with the event
        event_id = event_data[0]["tags"]["event_id"]
        # sos_data = generate_sos_data(event_id, current_time)
        # client.write_points(sos_data)

        print(f"Inserted event and SOS for event ID {event_id} at {current_time}")


# Insert 1000 events and corresponding SOS data with 1-minute intervals
insert_data(num_events=300, interval_seconds=600)
