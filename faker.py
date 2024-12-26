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
    {"city": "Agadir", "latitude": 30.4278, "longitude": -9.5981},
    {"city": "Oujda", "latitude": 34.6814, "longitude": -1.9076},
    {"city": "Kenitra", "latitude": 34.2610, "longitude": -6.5802},
    {"city": "Tetouan", "latitude": 35.5720, "longitude": -5.3729},
    {"city": "Safi", "latitude": 32.2994, "longitude": -9.2372},
]

europe_locations = [
    {"city": "Amsterdam", "latitude": 52.3676, "longitude": 4.9041},
    {"city": "Vienna", "latitude": 48.2082, "longitude": 16.3738},
    {"city": "Lisbon", "latitude": 38.7223, "longitude": -9.1393},
    {"city": "Athens", "latitude": 37.9838, "longitude": 23.7275},
    {"city": "Stockholm", "latitude": 59.3293, "longitude": 18.0686},
]  # Combine both regions


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
insert_data(num_events=50, interval_seconds=60)
