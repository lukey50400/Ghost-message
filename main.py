from fastapi import FastAPI, Depends
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, delete
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import uvicorn
import uuid
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI()

#the Database File
DATABASE_URL = "sqlite:///./messages.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Message Table
class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(String)
    text = Column(String)
    created_at = Column(DateTime, default=datetime.now)


Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/send")
async def send_message(text: str, sender_id: str, db: Session = Depends(get_db)):
    new_msg = Message(text=text, sender_id=sender_id)
    
    db.add(new_msg)
    db.commit()
    return {"status": "Message posted", "sender": sender_id}

@app.get("/messages")
async def get_messages(db: Session = Depends(get_db)):
    return db.query(Message).all()

@app.get("/cleanup")
async def cleanup_messages(db: Session = Depends(get_db)):
    
    cutoff = datetime.now() - timedelta(days=7)
    deleted_count = db.query(Message).filter(Message.created_at < cutoff).delete()
    
    db.commit()
    return {"status": "Success", "messages_removed": deleted_count}
    
def automatic_cleanup():
    db = SessionLocal()
    try:
        cutoff = datetime.now() - timedelta(days=7)
        deleted = db.query(Message).filter(Message.created_at < cutoff).delete()
        db.commit()
        print(f"🕒 Auto-Cleanup: Removed {deleted} old messages.")
    finally:
        db.close()


scheduler = BackgroundScheduler()
scheduler.add_job(automatic_cleanup, 'interval', days=1)
scheduler.start()
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)