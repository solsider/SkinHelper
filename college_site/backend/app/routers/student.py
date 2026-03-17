from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import News, Schedule, Student, User

router = APIRouter(prefix="/student", tags=["student"])


@router.get("/dashboard")
def dashboard(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current.role not in {"student", "admin"}:
        raise HTTPException(status_code=403, detail="Student access required")

    student = db.query(Student).filter(Student.user_id == current.id).first()
    group_name = student.group_name if student else "П-101"
    schedule = db.query(Schedule).filter(Schedule.group_name == group_name).all()
    news = db.query(News).order_by(News.published_at.desc()).limit(5).all()

    return {
        "profile": {
            "full_name": current.full_name,
            "email": current.email,
            "role": current.role,
            "group_name": group_name,
        },
        "schedule": [
            {
                "day_of_week": s.day_of_week,
                "lesson_time": s.lesson_time,
                "subject": s.subject,
                "teacher": s.teacher,
                "room": s.room,
            }
            for s in schedule
        ],
        "news": [{"id": n.id, "title": n.title, "summary": n.summary} for n in news],
    }
