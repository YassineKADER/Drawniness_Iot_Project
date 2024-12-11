import uvicorn


def main():
    uvicorn.run(
        "server:app",  # Assumes your main FastAPI script is named main.py
        host="0.0.0.0",  # Listen on all available network interfaces
        port=8000,  # Standard FastAPI development port
        reload=True,  # Enable auto-reload for development
    )


if __name__ == "__main__":
    main()
