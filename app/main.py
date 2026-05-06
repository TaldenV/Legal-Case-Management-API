from fastapi import FastAPI

app = FastAPI(
    title="Legal Case Management API",
    description="A REST API for managing clients, cases, claims, and partner integrations.",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    """
    Health check endpoint — confirms the app is running.
    docker-compose and load balancers can use this to verify the service is up.
    """
    return {"status": "ok"}
