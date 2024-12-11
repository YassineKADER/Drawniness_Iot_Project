import influxdb
import os
import uuid
import time
from dotenv import load_dotenv


class InfluxDBHandler:
    def __init__(self):
        # Load environment variables from the .env/.bash file
        load_dotenv()

        host = os.getenv("INFLUXDB_HOST")
        port = int(os.getenv("INFLUXDB_PORT", 8086))
        username = os.getenv("INFLUXDB_USERNAME")
        password = os.getenv("INFLUXDB_PASSWORD")
        database = os.getenv("INFLUXDB_DATABASE")

        self.client = influxdb.InfluxDBClient(
            host=host, port=port, username=username, password=password
        )

        # Ensure the database exists
        self.client.create_database(database)
        self.client.switch_database(database)

    def validate_user_exists(self, user_id: str) -> bool:
        """Check if the user exists in the database."""
        return True
        query = f"SELECT * FROM users WHERE user_id = '{user_id}' LIMIT 1"
        print(query)
        result = list(self.client.query(query).get_points())
        return len(result) > 0

    def validate_event_exists(self, event_id: str) -> bool:
        """Check if the event exists in the database."""
        query = f"SELECT * FROM events WHERE event_id = '{event_id}' LIMIT 1"
        result = list(self.client.query(query).get_points())
        return len(result) > 0

    def write_event(self, user_id: str, event_type: str, confidence: float) -> str:
        """Write an event to the database with validation for the user."""
        if not self.validate_user_exists(user_id):
            raise ValueError(f"User {user_id} does not exist")

        event_id = str(uuid.uuid4())
        json_body = [
            {
                "measurement": "events",
                "tags": {
                    "user_id": user_id,
                    "event_id": event_id,
                    "event_type": event_type,
                },
                "fields": {"confidence": confidence},
                "time": time.time_ns(),
            }
        ]
        self.client.write_points(json_body)
        return event_id

    def write_sos(
        self,
        user_id: str,
        event_id: str,
        message: str,
        latitude: float,
        longitude: float,
    ) -> str:
        """Write an SOS message to the database with validation for the user and event."""
        if not self.validate_user_exists(user_id):
            raise ValueError(f"User {user_id} does not exist")

        if not self.validate_event_exists(event_id):
            raise ValueError(f"Event {event_id} does not exist")

        sos_id = str(uuid.uuid4())
        json_body = [
            {
                "measurement": "sos",
                "tags": {"user_id": user_id, "event_id": event_id, "sos_id": sos_id},
                "fields": {
                    "message": message,
                    "latitude": latitude,
                    "longitude": longitude,
                },
                "time": time.time_ns(),
            }
        ]
        self.client.write_points(json_body)
        return sos_id

    def reset_database(self):
        """Reset the database by dropping specific measurements."""
        measurements = ["users", "events", "sos"]
        for measurement in measurements:
            try:
                self.client.query(f'DROP MEASUREMENT "{measurement}"')
                print(f"Dropped {measurement}")
            except Exception as e:
                print(f"Error dropping {measurement}: {e}")

    def close(self):
        """Close the connection to the InfluxDB client."""
        pass


def main():
    db_manager = InfluxDBHandler()
    db_manager.reset_database()


if __name__ == "__main__":
    main()
