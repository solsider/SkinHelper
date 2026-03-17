from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Application, Contact, News, Schedule, Specialty, Teacher
from ..schemas import (
    ApplicationCreate,
    ContactOut,
    NewsOut,
    ScheduleOut,
    SpecialtyOut,
    TeacherOut,
)

router = APIRouter(tags=["public"])


@router.get("/news", response_model=list[NewsOut])
def list_news(db: Session = Depends(get_db)):
    return db.query(News).order_by(News.published_at.desc()).all()


@router.get("/specialties", response_model=list[SpecialtyOut])
def list_specialties(db: Session = Depends(get_db)):
    return db.query(Specialty).all()


@router.get("/teachers", response_model=list[TeacherOut])
def list_teachers(db: Session = Depends(get_db)):
    return db.query(Teacher).all()


@router.get("/schedule", response_model=list[ScheduleOut])
def list_schedule(db: Session = Depends(get_db)):
    return db.query(Schedule).all()


@router.get("/contacts", response_model=ContactOut)
def get_contacts(db: Session = Depends(get_db)):
    return db.query(Contact).first()


@router.post("/applications")
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db)):
    application = Application(**payload.model_dump())
    db.add(application)
    db.commit()
    return {"message": "Заявка отправлена"}
