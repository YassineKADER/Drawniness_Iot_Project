# Real-Time Drowsiness Detection & Driver Safety System

<p align="center">
  <img src="https://avatars.githubusercontent.com/u/80207770" alt="Project Banner" width="199">
</p>

## Overview

This project is a comprehensive IoT solution designed to enhance driver safety by detecting drowsiness in real-time. Leveraging computer vision, machine learning, and cloud services, this system not only detects drowsiness but also triggers alerts and notifications to prevent potential accidents. This system includes a drowsiness detection model, backend API, database integration, and Arduino-based hardware.

## Features

-   **Real-Time Drowsiness Detection:** Utilizes a trained YOLOv8 model to analyze video streams and detect drowsiness.
-   **Backend API:** A FastAPI-based backend server handles user authentication, event tracking, and SOS alerts, integrated with InfluxDB for data storage.
-   **Data Visualization:** Uses Grafana to visualize and analyze driver behavior data.
-   **Cloud Integration:** Data is stored in an InfluxDB database with the capability to integrate with external APIs for event notifications.
-   **Arduino Integration:** Controls physical alerts through an Arduino board, triggering LED blinking.
-   **Comprehensive System:** It covers the whole pipeline, from computer vision to hardware alerts, ensuring a complete safety solution.

## Architecture

The project follows this architecture:

1.  **Video Capture:** An RTMP stream provides real-time video input.(you can use just your webcame if you want to work with rtmp like me you should setup a rtmp server like nginx with nginx-rtmp-module or MonaServer if your using windows)
2.  **YOLOv8 Model:** A pre-trained YOLOv8 model detects drowsy and other states.
3.  **Backend API:** A FastAPI server handles:
    -   User authentication (via JWT).
    -   Event recording into InfluxDB (drowsiness, active, inactive, sleep).
    -   SOS alerts and location information.
    -   External API integration (for future HTTP event handling).
4.  **InfluxDB:** Time-series database for storing event and SOS data.
5.  **Grafana:** Visualizes data from InfluxDB for analysis.
6.  **Arduino:** Receives commands via serial communication to trigger physical alerts (LED blinking).

## Getting Started

Follow these steps to set up and run the project:

### Prerequisites

-   Python 3.10+
-   InfluxDB
-   RTMP server (e.g., nginx-rtmp-module)
-   Arduino IDE
-   Nodejs (for Grafana)
-   Basic knowledge of Linux command-line

### Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/realtime_detection.git
    cd realtime_detection
    ```

2.  **Create and Activate the Virtual Environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate  # On Windows
    ```

3.  **Install Dependencies:**

    ```bash
    pip install -r req.txt
    ```

4.  **Configure Environment Variables:**

    -   Create a `.env` file in the root directory.
    -   Add the necessary environment variables:

        ```env
        INFLUXDB_HOST=your_influxdb_host
        INFLUXDB_PORT=8086
        INFLUXDB_USERNAME=your_influxdb_username
        INFLUXDB_PASSWORD=your_influxdb_password
        INFLUXDB_DATABASE=your_influxdb_database
        API_URL=http://localhost:8000
        RTMP_STREAM_URL=rtmp://localhost:1935/live/1
        MODEL_PATH=./yolo/best_with_100_epochs.pt
        SECRET_KEY=your_secret_jwt_key
        LOGIN_EMAIL=your_email
        LOGIN_PASSWORD=your_password
        ```
        
        Replace placeholder values with your actual values.
        Make sure to replace `your_secret_jwt_key` with a strong and randomly generated secret key.

5.  **Run InfluxDB and Grafana:**

    -   Ensure InfluxDB is running and configured with the provided credentials.
    -   Import the Grafana dashboard (`grafana/dashboard.json`) for easy visualization of the data.
    -   For Grafana setup, use the following command to install all the required packages:
        ```bash
        sudo npm install -g @grafana/toolkit
        ```
        Then run
        ```bash
        grafana-cli plugins install grafana-influxdb-datasource
        ```
        and
        ```bash
        grafana-server
        ```

6.  **Start the RTMP server**

    -   Configure and start your RTMP server. Make sure that you have `ffmpeg` installed.
    -   To simulate an rtmp stream run this command:

        ```bash
        ffmpeg -re -stream_loop -1 -i video.mp4 -c copy -f flv rtmp://localhost:1935/live/1
        ```

        Note: replace video.mp4 with your video.
7.  **Run the Backend API:**

    ```bash
    python server.py # or  python server_run.py if you want the server to run on a different port
    ```

8.  **Run the Main Application:**

    ```bash
    python main.py
    ```

9.  **Upload Arduino code to the board:**

    - Open `arduino_code/main.ino` in Arduino IDE
    - Select the correct port
    - Upload the code

### Using the System

1.  **Log in with provided credentials.**
2.  **Start the video stream using RTMP.**
3.  The system will detect drowsiness and send events/SOS alerts to the backend server.
4.  If drowsiness is detected, the Arduino will trigger an LED to blink.

## Development

-   The drowsiness detection model was trained using YOLOv8, please check the notebook to reproduce the training.
-   Feel free to contribute to this project by opening issues, requesting features, or submitting pull requests.

## Test

-   `test.py` contains simple requests to the API to test the functionality.
-   You can simulate data using `faker.py`.

## Additional Resources

-   YOLOv8: [https://github.com/ultralytics/ultralytics](https://github.com/ultralytics/ultralytics)
-   FastAPI: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
-   InfluxDB: [https://www.influxdata.com/](https://www.influxdata.com/)
-   Grafana: [https://grafana.com/](https://grafana.com/)

## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

## Arduino Code

The Arduino code `arduino_code/main.ino` controls the physical alerts using an LED. It communicates via serial with the main application. Here is a basic overview:

-   **Motor Control**: Defines pins for motor control, but they are not used in this version.
-   **LED**: Defines a pin for the LED (pin 13) for visual alert.
-   **Serial Communication**: Listens for commands via serial (baud rate 9600).
-   **Commands**:
    -  `"STOP"`:
       - On the first "STOP" command, it slows down motors (not used in this version).
       - On the second "STOP" command, it stops the motors (not used in this version) and start blinking the LED.
    -   `"START"`: Resets the system, stop blinking the LED (if blinking), and resumes motors (not used in this version)
-   **Blinking LED**: Blinks the LED until a `"START"` command is received.

<p align="center">
  Made with ❤️ by Yassine Kader (EROS)

</p>
