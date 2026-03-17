from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(30), default="student", nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    student_profile = relationship("Student", back_populates="user", uselist=False)


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    group_name = Column(String(50), default="П-101")
    year = Column(Integer, default=1)

    user = relationship("User", back_populates="student_profile")


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(120), nullable=False)
    position = Column(String(120), nullable=False)
    bio = Column(Text, nullable=False)
    email = Column(String(120), nullable=False)


class Specialty(Base):
    __tablename__ = "specialties"

    id = Column(Integer, primary_key=True)
    title = Column(String(120), nullable=False)
    code = Column(String(30), nullable=False)
    duration = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(120), nullable=False)
    phone = Column(String(30), nullable=False)
    specialty_id = Column(Integer, ForeignKey("specialties.id"), nullable=False)
    message = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True)
    title = Column(String(160), nullable=False)
    summary = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    published_at = Column(DateTime, default=datetime.utcnow)


class Schedule(Base):
    __tablename__ = "schedule"

    id = Column(Integer, primary_key=True)
    group_name = Column(String(50), nullable=False)
    day_of_week = Column(String(20), nullable=False)
    lesson_time = Column(String(30), nullable=False)
    subject = Column(String(120), nullable=False)
    teacher = Column(String(120), nullable=False)
    room = Column(String(20), nullable=False)


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True)
    address = Column(String(255), nullable=False)
    phone = Column(String(30), nullable=False)
    email = Column(String(120), nullable=False)
    map_embed = Column(Text, nullable=False)
