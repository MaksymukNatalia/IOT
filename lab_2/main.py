# SQLAlchemy setup
import json
from typing import List, Set
from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect, Body
import asyncio
from typing import Set, Dict, List, Any, Optional
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Float,
    DateTime,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select, insert, update, delete
from datetime import datetime
from pydantic import BaseModel, field_validator
from config import (
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
)

app = FastAPI()
# WebSocket subscriptions
subscriptions: Set[WebSocket] = set()

DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(DATABASE_URL)
metadata = MetaData()
# Define the ProcessedAgentData table
processed_agent_data = Table(
    "processed_agent_data",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("road_state", String),
    Column("x", Float),
    Column("y", Float),
    Column("z", Float),
    Column("latitude", Float),
    Column("longitude", Float),
    Column("timestamp", DateTime),
    )

class AccelerometerData(BaseModel):
    x: float
    y: float
    z: float

class GpsData(BaseModel):
    latitude: float
    longitude: float

class AgentData(BaseModel):
    accelerometer: AccelerometerData
    gps: GpsData
    timestamp: datetime
    @classmethod
    @field_validator('timestamp', mode='before')
    def check_timestamp(cls, value):
        if isinstance(value, datetime):
         return value
        try:
            return datetime.fromisoformat(value)
        except (TypeError, ValueError):
            raise ValueError(
                 "Invalid timestamp format. Expected ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).")

class ProcessedAgentData(BaseModel):
    road_state: str
    agent_data: AgentData
# Database model
class ProcessedAgentDataInDB(BaseModel):
    id: int
    road_state: str
    x: float
    y: float
    z: float
    latitude: float
    longitude: float
    timestamp: datetime




# FastAPI WebSocket endpoint
@app.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    subscriptions.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        subscriptions.remove(websocket)
# Function to send data to subscribed users
async def send_data_to_subscribers(data):
    for websocket in subscriptions:
        await websocket.send_json(json.dumps(data))

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@app.post("/processed_agent_data/")
async def create_processed_agent_data(data:List[ProcessedAgentData]):
    list_data = []

    for item in data:
        try:
            post_data = {
                "road_state": item.road_state,
                "x": item.agent_data.accelerometer.x,
                "y": item.agent_data.accelerometer.y,
                "z": item.agent_data.accelerometer.z,
                "latitude": item.agent_data.gps.latitude,
                "longitude": item.agent_data.gps.longitude,
                "timestamp": item.agent_data.timestamp
            }

            list_data.append(post_data)
            db = SessionLocal()

            insert_to_db = insert(processed_agent_data).values(list_data)

            try:
                db.execute(insert_to_db)
                db.commit()
            except Exception as e:
                db.rollback()
                print(f"An error occurred: {e}")
            finally:
                db.close()

        except Exception as e:
            print(f"Error processing data: {e}")

    return {"message": "Data processed and inserted into the database successfully"}


# Send data to subscribers
@app.get("/processed_agent_data/{processed_agent_data_id}",response_model=ProcessedAgentDataInDB)
def read_processed_agent_data(processed_agent_data_id: int):
    db = SessionLocal()
    try:
        select_data = select(processed_agent_data).where(processed_agent_data.c.id == processed_agent_data_id)
        single_value = db.execute(select_data).fetchone()
        return single_value
    except Exception as e:
        db.rollback()
        print(f"An error occurred: {e}")
    finally:
        db.close()
# Get data by id

@app.get("/processed_agent_data/", response_model=list[ProcessedAgentDataInDB])
def list_processed_agent_data():
    db = SessionLocal()
    try:
        all_records = db.query(processed_agent_data).all()
        return all_records
    except Exception as e:
        db.rollback()
        print(f"An error occurred: {e}")
    finally:
        db.close()


# Get list of data

@app.put("/processed_agent_data/{processed_agent_data_id}", response_model=ProcessedAgentDataInDB)
def update_processed_agent_data(processed_agent_data_id: int, data: ProcessedAgentData ):
# Update data
    pass
@app.delete("/processed_agent_data/{processed_agent_data_id}", response_model=ProcessedAgentDataInDB)
def delete_processed_agent_data(processed_agent_data_id: int):
# Delete by id
    pass
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)