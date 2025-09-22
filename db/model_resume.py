from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date


class DateInfo(BaseModel):
    month: str
    year: str


class Experience(BaseModel):
    id: int
    role: str
    level:str
    company: str
    startDate: DateInfo
    endDate: Optional[DateInfo] = None
    description: str
    isCurrentRole: bool


class Education(BaseModel):
    id: int
    degree: str
    institution: str
    faculty: str
    major: str
    startDate: DateInfo
    endDate: Optional[DateInfo] = None
    gpa: str
    isCurrentlyStudying: bool


class PersonalInfo(BaseModel):
    fullName: str
    phone: str
    email: EmailStr
    address: str
    birthDate: Optional[date] = None
    currentSalary: float
    expectedSalary: float


class Achievement(BaseModel):
    id: int
    title: str
    description: str
    technologies: List[str]
    link: str
    startDate: DateInfo
    endDate: Optional[DateInfo] = None


class Certificate(BaseModel):
    id: int
    name: str


class ResumeModel(BaseModel):
    personalInfo: PersonalInfo
    skills: List[str]
    experiences: List[Experience]
    education: List[Education]
    certificates: List[Certificate]
    achievement: List[Achievement]
