from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_admin
from ..models import News, Schedule, Specialty, Teacher
from ..schemas import NewsBase, NewsOut, ScheduleBase, ScheduleOut, SpecialtyBase, SpecialtyOut, TeacherBase, TeacherOut

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


def update_model(instance, payload):
    for key, value in payload.model_dump().items():
        setattr(instance, key, value)


@router.post("/news", response_model=NewsOut)
def create_news(payload: NewsBase, db: Session = Depends(get_db)):
    item = News(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/news/{item_id}", response_model=NewsOut)
def update_news(item_id: int, payload: NewsBase, db: Session = Depends(get_db)):
    item = db.get(News, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="News not found")
    update_model(item, payload)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/news/{item_id}")
def delete_news(item_id: int, db: Session = Depends(get_db)):
    item = db.get(News, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="News not found")
    db.delete(item)
    db.commit()
    return {"message": "Deleted"}


@router.post("/specialties", response_model=SpecialtyOut)
def create_specialty(payload: SpecialtyBase, db: Session = Depends(get_db)):
    item = Specialty(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/specialties/{item_id}", response_model=SpecialtyOut)
def update_specialty(item_id: int, payload: SpecialtyBase, db: Session = Depends(get_db)):
    item = db.get(Specialty, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Specialty not found")
    update_model(item, payload)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/specialties/{item_id}")
def delete_specialty(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Specialty, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Specialty not found")
    db.delete(item)
    db.commit()
    return {"message": "Deleted"}


@router.post("/teachers", response_model=TeacherOut)
def create_teacher(payload: TeacherBase, db: Session = Depends(get_db)):
    item = Teacher(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/teachers/{item_id}", response_model=TeacherOut)
def update_teacher(item_id: int, payload: TeacherBase, db: Session = Depends(get_db)):
    item = db.get(Teacher, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Teacher not found")
    update_model(item, payload)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/teachers/{item_id}")
def delete_teacher(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Teacher, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Teacher not found")
    db.delete(item)
    db.commit()
    return {"message": "Deleted"}


@router.post("/schedule", response_model=ScheduleOut)
def create_schedule(payload: ScheduleBase, db: Session = Depends(get_db)):
    item = Schedule(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/schedule/{item_id}", response_model=ScheduleOut)
def update_schedule(item_id: int, payload: ScheduleBase, db: Session = Depends(get_db)):
    item = db.get(Schedule, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Schedule record not found")
    update_model(item, payload)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/schedule/{item_id}")
def delete_schedule(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Schedule, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Schedule record not found")
    db.delete(item)
    db.commit()
    return {"message": "Deleted"}
