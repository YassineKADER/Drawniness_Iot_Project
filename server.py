from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.security import OAuth2PasswordRequestForm
from db.Handler import InfluxDBHandler
from db.user_handler import UserHandler
from auth.jwt_handler import AuthHandler
from dotenv import load_dotenv
import logging
import os

load_dotenv()
app = FastAPI()

# Database Configuration
INFLUXDB_HOST = os.getenv("INFLUXDB_HOST")
INFLUXDB_PORT = int(os.getenv("INFLUXDB_PORT", 8086))
INFLUXDB_USERNAME = os.getenv("INFLUXDB_USERNAME")
INFLUXDB_PASSWORD = os.getenv("INFLUXDB_PASSWORD")
INFLUXDB_DATABASE = os.getenv("INFLUXDB_DATABASE")

# Initialize Handlers
db_handler = InfluxDBHandler()
user_handler = UserHandler(db_handler)

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.post("/register")
async def register_user(user_data: dict):
    try:
        user_id = user_handler.create_user(user_data)
        return {"status": "success", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/token")
async def login_for_access_token(form_data: dict):
    user = user_handler.authenticate_user(
        form_data.get("email"), form_data.get("password")
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = AuthHandler.create_access_token(data={"sub": user["user_id"]})
    return {"access_token": access_token, "token_type": "bearer"}


# Event Handling Route
@app.post("/event/")
async def handle_event(
    request: dict, current_user: dict = Depends(AuthHandler.get_current_user)
):
    try:
        data = request
        user_id = current_user.get("sub")
        event_type = data.get("event_type")
        confidence = data.get("confidence", 0.0)

        if not user_id or not event_type:
            raise HTTPException(
                status_code=400, detail="Missing 'user_id' or 'event_type'"
            )

        # Write the event to InfluxDB
        event_id = db_handler.write_event(user_id, event_type, confidence)

        # Publish event to external HTTP API
        payload = {
            "user_id": user_id,
            "event_type": event_type,
            "confidence": confidence,
            "event_id": event_id,
        }
        # try:
        #            response = requests.post(HTTP_EVENT_API, json=payload)
        # response.raise_for_status()
        # logger.info(f"Event published to HTTP API: {response.json()}")
        # except requests.RequestException as e:
        #    logger.error(f"Failed to publish event: {e}")
        #    raise HTTPException(status_code=502, detail="Failed to notify HTTP API")

        return {"status": "success", "published_event": payload}
    except Exception as e:
        # raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
        raise e


# SOS Route
@app.post("/sos/")
async def handle_sos(
    request: dict, current_user: dict = Depends(AuthHandler.get_current_user)
):
    try:
        data = request
        user_id = current_user.get("sub")
        event_id = data.get("event_id")
        message = data.get("message")
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        if not all([user_id, message, latitude, longitude]):
            raise HTTPException(status_code=400, detail="Missing required fields")

        # Write SOS to InfluxDB
        db_handler.write_sos(user_id, event_id, message, latitude, longitude)

        # Notify external HTTP API
        payload = {
            "user_id": user_id,
            "event_id": event_id,
            "message": message,
            "latitude": latitude,
            "longitude": longitude,
        }
        # try:
        #            response = requests.post(HTTP_SOS_API, json=payload)
        #            response.raise_for_status()
        # logger.info(f"SOS notification sent to HTTP API: {response.json()}")
        # except requests.RequestException as e:
        #    logger.error(f"Failed to send SOS notification: {e}")
        #    raise HTTPException(status_code=502, detail="Failed to notify HTTP API")

        return {"status": "SOS sent", "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# Main entry point for running the server
def main():
    import uvicorn

    uvicorn.run(
        "server:app",  # Assumes the file is named server.py
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
