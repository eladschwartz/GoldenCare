from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base



class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    
    # Relationships
    users = relationship("User", back_populates="department")
    patients = relationship("Patient", back_populates="department")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    role = Column(String, default="USER")

    # Relationships
    department = relationship("Department", back_populates="users")
    treatments_given = relationship("Treatment", back_populates="therapist", cascade="all, delete-orphan")

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    release_date = Column(DateTime(timezone=True), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)

    # Relationships
    department = relationship("Department", back_populates="patients")
    treatments = relationship("Treatment", back_populates="patient", cascade="all, delete-orphan")

class Treatment(Base):
    __tablename__ = "treatments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    therapist_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True),server_default=(func.now()), nullable=False)

    # Relationships
    patient = relationship("Patient", back_populates="treatments")
    therapist = relationship("User", back_populates="treatments_given")