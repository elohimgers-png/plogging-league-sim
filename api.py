from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

simulation_data = {
    "litter": 1000,
    "cleaned": 0,
    "engagement": 0.0,
    "points": 0
}

control = {"reward": 1.0}

class SimulationUpdate(BaseModel):
    litter: int
    cleaned: int
    engagement: float
    points: float

@app.get("/")
def root():
    return {"status": "API running"}

@app.post("/update")
def update_data(data: SimulationUpdate):
    global simulation_data
    simulation_data = data.dict()
    return {"status": "received"}

@app.get("/metrics")
def get_metrics():
    return simulation_data

@app.post("/control")
def set_control(data: dict):
    global control
    control.update(data)
    return {"status": "updated"}

@app.get("/control")
def get_control():
    return control
