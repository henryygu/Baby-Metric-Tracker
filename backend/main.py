from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import yaml
from datetime import datetime

from . import crud, models, schemas, database
from .database import engine, get_session

models.Log.metadata.create_all(bind=engine)

app = FastAPI(title="Baby Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/config")
def get_config():
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    return config["user"]

@app.get("/dashboard", response_model=schemas.DashboardData)
def get_dashboard(db: Session = Depends(get_session)):
    return crud.get_stats(db)

@app.get("/logs", response_model=List[schemas.LogRead])
def read_logs(skip: int = 0, limit: int = 100, event: Optional[str] = None, db: Session = Depends(get_session)):
    return crud.get_logs(db, skip=skip, limit=limit, event=event)

@app.post("/logs", response_model=schemas.LogRead)
def create_log(log: schemas.LogCreate, db: Session = Depends(get_session)):
    return crud.log_event(db, log)

@app.post("/logs/{event_type}/stop", response_model=schemas.LogRead)
def stop_session(event_type: str, db: Session = Depends(get_session)):
    stopped = crud.stop_ongoing_session(db, event_type)
    if not stopped:
        raise HTTPException(status_code=404, detail=f"No ongoing {event_type} session found")
    return stopped

@app.delete("/logs/{log_id}")
def delete_log(log_id: int, db: Session = Depends(get_session)):
    success = crud.delete_log(db, log_id)
    if not success:
        raise HTTPException(status_code=404, detail="Log not found")
    return {"status": "success"}

@app.put("/logs/{log_id}", response_model=schemas.LogRead)
def update_log(log_id: int, log_data: schemas.LogCreate, db: Session = Depends(get_session)):
    db_log = db.query(models.Log).filter(models.Log.id == log_id).first()
    if not db_log:
        raise HTTPException(status_code=404, detail="Log not found")
    
    for key, value in log_data.dict(exclude_unset=True).items():
        setattr(db_log, key, value)
    
    db.commit()
    db.refresh(db_log)
    return db_log

@app.get("/latest-feed-id")
def get_latest_feed_id(db: Session = Depends(get_session)):
    return {"feed_id": crud.get_latest_feed_id(db)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
