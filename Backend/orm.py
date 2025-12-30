from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, BigInteger, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Create base class for ORM models
Base = declarative_base()

# Define ORM Models
class Employee(Base):
    __tablename__ = 'employees'
    
    employee_id = Column(String, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    dept = Column(String)
    role = Column(String)
    location = Column(String)
    hire_date = Column(DateTime)
    
    # Relationships
    attendance_records = relationship("Attendance", back_populates="employee")
    events = relationship("Event", back_populates="employee")
    payroll_records = relationship("Payroll", back_populates="employee")
    reviews = relationship("Review", back_populates="employee")
    
    def __repr__(self):
        return f"<Employee(id={self.employee_id}, name={self.first_name} {self.last_name}, dept={self.dept})>"


class Attendance(Base):
    __tablename__ = 'attendance'
    
    employee_id = Column(String, ForeignKey('employees.employee_id'), primary_key=True)
    date = Column(DateTime, primary_key=True)
    absent = Column(BigInteger)
    
    # Relationship
    employee = relationship("Employee", back_populates="attendance_records")
    
    def __repr__(self):
        return f"<Attendance(employee_id={self.employee_id}, date={self.date}, absent={self.absent})>"


class Event(Base):
    __tablename__ = 'events'
    
    employee_id = Column(String, ForeignKey('employees.employee_id'), primary_key=True)
    event_type = Column(String, primary_key=True)
    event_date = Column(DateTime, primary_key=True)
    details = Column(String)
    
    # Relationship
    employee = relationship("Employee", back_populates="events")
    
    def __repr__(self):
        return f"<Event(employee_id={self.employee_id}, type={self.event_type}, date={self.event_date})>"


class KPIOverview(Base):
    __tablename__ = 'kpi_overview'
    
    headcount = Column(BigInteger, primary_key=True)
    terminations = Column(BigInteger)
    turnover_rate = Column(Float)
    
    def __repr__(self):
        return f"<KPIOverview(headcount={self.headcount}, terminations={self.terminations}, turnover_rate={self.turnover_rate})>"


class MappingsLog(Base):
    __tablename__ = 'mappings_log'
    
    ts_utc = Column(String, primary_key=True)
    provider = Column(String, primary_key=True)
    source_field = Column(String)
    approved = Column(String)
    suggested = Column(String)
    
    def __repr__(self):
        return f"<MappingsLog(ts={self.ts_utc}, provider={self.provider})>"


class Payroll(Base):
    __tablename__ = 'payroll'
    
    employee_id = Column(String, ForeignKey('employees.employee_id'), primary_key=True)
    email = Column(String)
    base_salary = Column(Float)
    currency = Column(String)
    pay_period = Column(String, primary_key=True)
    
    # Relationship
    employee = relationship("Employee", back_populates="payroll_records")
    
    def __repr__(self):
        return f"<Payroll(employee_id={self.employee_id}, salary={self.base_salary}, period={self.pay_period})>"


class Review(Base):
    __tablename__ = 'reviews'
    
    employee_id = Column(String, ForeignKey('employees.employee_id'), primary_key=True)
    review_date = Column(DateTime, primary_key=True)
    score = Column(BigInteger)
    
    # Relationship
    employee = relationship("Employee", back_populates="reviews")
    
    def __repr__(self):
        return f"<Review(employee_id={self.employee_id}, date={self.review_date}, score={self.score})>"


class SyncLog(Base):
    __tablename__ = 'sync_log'
    
    ts_utc = Column(String, primary_key=True)
    provider = Column(String, primary_key=True)
    rows_in = Column(BigInteger)
    rows_valid = Column(BigInteger)
    rows_invalid = Column(BigInteger)
    
    def __repr__(self):
        return f"<SyncLog(ts={self.ts_utc}, provider={self.provider}, rows_in={self.rows_in})>"


class Admin(Base):
    __tablename__ = 'admin'
    
    employee_id = Column(String, ForeignKey('employees.employee_id'), primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String)
    google_authenticator_secret = Column(String)
    
    # Relationship
    employee = relationship("Employee")
    
    def __repr__(self):
        return f"<Admin(employee_id={self.employee_id}, username={self.username}, role={self.role})>"


# Database connection and session setup
engine = create_engine('sqlite:///hr.sqlite', echo=False)
Session = sessionmaker(bind=engine)
session = Session()
