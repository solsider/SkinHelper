from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    full_name: str = Field(min_length=2)
    email: EmailStr
    password: str = Field(min_length=6)
    role: str = "student"


class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class NewsBase(BaseModel):
    title: str
    summary: str
    content: str


class NewsOut(NewsBase):
    id: int
    published_at: datetime

    class Config:
        from_attributes = True


class SpecialtyBase(BaseModel):
    title: str
    code: str
    duration: str
    description: str


class SpecialtyOut(SpecialtyBase):
    id: int

    class Config:
        from_attributes = True


class TeacherBase(BaseModel):
    full_name: str
    position: str
    bio: str
    email: EmailStr


class TeacherOut(TeacherBase):
    id: int

    class Config:
        from_attributes = True


class ScheduleBase(BaseModel):
    group_name: str
    day_of_week: str
    lesson_time: str
    subject: str
    teacher: str
    room: str


class ScheduleOut(ScheduleBase):
    id: int

    class Config:
        from_attributes = True


class ApplicationCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    specialty_id: int
    message: str = ""


class ContactOut(BaseModel):
    id: int
    address: str
    phone: str
    email: EmailStr
    map_embed: str

    class Config:
        from_attributes = True
