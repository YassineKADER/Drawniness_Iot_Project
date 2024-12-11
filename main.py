import cv2
import time
import requests
import os
from dotenv import load_dotenv
from ultralytics import YOLO
from PIL import Image
import serial
import time

# Load environment variables
load_dotenv()
arduino = serial.Serial(port="/dev/ttyACM1", baudrate=9600, timeout=0.1)
time.sleep(2)


class BackendAuthenticator:
    def __init__(self, api_url):
        self.api_url = api_url
        self.access_token = None

    def login(self, email, password):
        try:
            payload = {"email": email, "password": password}
            response = requests.post(f"{self.api_url}/token", json=payload)
            response.raise_for_status()
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            return self.access_token
        except Exception as e:
            print(f"Login failed: {e}")
            return None


class BackendEventStreamer:
    def __init__(self, api_url, access_token):
        self.api_url = api_url
        self.access_token = access_token
        self.last_event_time = 0
        self.event_interval = 1  # seconds
        self.sos_sent = False
        self.last_event_id = None

    def send_event(self, event_type, confidence=0.6):
        current_time = time.time()

        # Only send events every 20 seconds
        if True and (current_time - self.last_event_time >= self.event_interval):
            try:
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                }
                payload = {"event_type": event_type, "confidence": confidence}
                response = requests.post(
                    f"{self.api_url}/event/", json=payload, headers=headers
                )
                response.raise_for_status()
                response_data = response.json()

                # Store the event ID for potential SOS
                self.last_event_id = response_data.get("published_event").get(
                    "event_id"
                )
                self.last_event_time = current_time

                print(f"Event sent: {event_type}, Event ID: {self.last_event_id}")
                return response_data.get("published_event").get("event_id")

            except Exception as e:
                print(f"Failed to send event: {e}")
                return None

    def reset_sos(self):
        self.sos_sent = False

    def send_sos(self, message, latitude=0, longitude=0):
        # Only send SOS once and ensure we have an event ID
        if not self.sos_sent and self.last_event_id:
            try:
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "event_id": self.last_event_id,
                    "message": message,
                    "latitude": latitude,
                    "longitude": longitude,
                }
                response = requests.post(
                    f"{self.api_url}/sos/", json=payload, headers=headers
                )
                response.raise_for_status()
                self.sos_sent = True
                print(f"SOS sent with Event ID: {self.last_event_id}")
            except Exception as e:
                print(f"Failed to send SOS: {e}")


class RTMPStream:
    def __init__(self, stream_url):
        self.stream_url = stream_url
        self.cap = cv2.VideoCapture(self.stream_url)
        if not self.cap.isOpened():
            raise Exception(f"Error: Could not open RTMP stream at {stream_url}")

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            raise Exception("Error: Failed to capture frame.")
        return frame

    def release(self):
        self.cap.release()


class DrowsinessDetector:
    def __init__(self, model_path, event_streamer):
        self.model = YOLO(model_path)
        self.event_streamer = event_streamer
        self.is_currently_drowsy = False

    def process_frame(self, frame):
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        results = self.model.predict(source=image, conf=0.5)

        drowsy_detected = False
        events_sent = []

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])  # Bounding box coordinates
                class_name = self.model.names[int(box.cls[0])]
                confidence = box.conf[0]

                # Draw bounding boxes and labels
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green box
                label = f"{class_name} {confidence:.2f}"
                cv2.putText(
                    frame,
                    label,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2,
                )

                # Send events for each detected class
                if class_name:
                    events_sent.append(
                        self.event_streamer.send_event(class_name, confidence.item())
                    )

                # Check for drowsiness
                if class_name == "drowsy":
                    drowsy_detected = True

        # Handle drowsiness state
        if drowsy_detected:
            if not self.is_currently_drowsy:
                # First time drowsiness is detected
                self.is_currently_drowsy = True
                event_id = self.event_streamer.send_event("drowsy", 0.8)
                arduino.write(b"drowsy")
                print(event_id)
                raise Exception()
                if event_id:
                    print("sos trigger")
                    self.event_streamer.send_sos("Severe Drowsiness Detected!")
                return frame, "SOS: Drowsiness Detected!"
        else:
            # Reset SOS if driver is no longer drowsy
            if self.is_currently_drowsy:
                self.is_currently_drowsy = False
                self.event_streamer.reset_sos()

        return frame, None


def main():
    # Get configuration from environment variables
    api_url = os.getenv("API_URL", "http://localhost:8000")
    stream_url = os.getenv("RTMP_STREAM_URL", "rtmp://localhost:1935/live/1")
    model_path = os.getenv("MODEL_PATH", "best_with_100_epochs.pt")

    # Authentication from environment variables
    email = os.getenv("LOGIN_EMAIL", "yassine.kader@transportation.com")
    password = os.getenv("LOGIN_PASSWORD", "Driver2024!")

    # Authenticate and get token
    authenticator = BackendAuthenticator(api_url)
    access_token = authenticator.login(email, password)

    if not access_token:
        print("Authentication failed. Exiting.")
        return

    # Initialize components
    event_streamer = BackendEventStreamer(api_url, access_token)
    stream = RTMPStream(stream_url)
    detector = DrowsinessDetector(model_path, event_streamer)

    frame_interval = 0.5  # Delay between frames
    last_frame_time = time.time()

    try:
        while True:
            frame = stream.get_frame()
            current_time = time.time()

            # Process frame every 0.5 seconds
            if current_time - last_frame_time < frame_interval:
                continue

            last_frame_time = current_time

            # Detect drowsiness and draw results
            frame, message = detector.process_frame(frame)

            # Display the frame with bounding boxes
            cv2.imshow("RTMP Stream with YOLO Detection", frame)

            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        stream.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
