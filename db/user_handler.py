from typing import Dict, Optional
import influxdb
import uuid
from auth.jwt_handler import AuthHandler


class UserHandler:
    def __init__(self, db_handler):
        self.db_handler = db_handler
        self.client = db_handler.client

    def create_user(self, user_data: Dict):
        # Validate required fields
        user_data["user_id"] = "driver_" + str(uuid.uuid4())
        if not all(
            key in user_data
            for key in ["user_id", "name", "email", "phone", "password"]
        ):
            raise ValueError("Missing required user fields")

        # Hash the password
        hashed_password = AuthHandler.get_password_hash(user_data["password"])

        # Prepare user data for InfluxDB
        json_body = [
            {
                "measurement": "users",
                "tags": {"user_id": user_data["user_id"], "email": user_data["email"]},
                "fields": {
                    "name": user_data["name"],
                    "phone": user_data["phone"],
                    "hashed_password": hashed_password,
                },
            }
        ]

        # Write to database
        self.client.write_points(json_body)
        return user_data["user_id"]

    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        # Correct InfluxDB query syntax
        query = f"SELECT * FROM \"users\" WHERE \"email\" = '{email}'"
        print(query)

        try:
            # Use .get_points(measurement='users') to specify the measurement
            result = list(self.client.query(query).get_points(measurement="users"))

            if not result:
                return None

            user = result[0]
            if AuthHandler.verify_password(password, user.get("hashed_password", "")):
                return {
                    "user_id": user.get("user_id", ""),
                    "email": user.get("email", ""),
                    "name": user.get("name", ""),
                }
            return None
        except Exception as e:
            print(f"Authentication error: {e}")
            return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        query = f"SELECT * FROM users WHERE user_id = '{user_id}'"
        result = list(self.client.query(query).get_points())

        return result[0] if result else None
