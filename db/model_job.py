from pydantic import BaseModel
from typing import List, Optional

class Experience(BaseModel):
    job_name: str
    level:str
    min_experience_years: Optional[int] = None
    max_experience_years: Optional[int] = None
    description: str

class Education(BaseModel):
    id: int
    education: List[str]
    minimum_level: str

class JobModel(BaseModel):
    title: str
    skills: List[str]
    experiences: List[Experience]
    educations: List[Education]
    responsibilities: List[str]