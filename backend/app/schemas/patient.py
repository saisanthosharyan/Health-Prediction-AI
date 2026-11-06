import math
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class PatientBase(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    date_of_birth: date
    email: EmailStr

    glucose: float = Field(gt=0)
    haemoglobin: float = Field(gt=0)
    cholesterol: float = Field(gt=0)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        value = " ".join(value.split())

        if not value:
            raise ValueError("Full name cannot be empty.")

        return value

    @field_validator("date_of_birth", mode="before")
    @classmethod
    def parse_date_of_birth(cls, value):
        if isinstance(value, date):
            return value

        if isinstance(value, str):
            for date_format in ("%d/%m/%Y", "%d.%m.%Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(
                        value.strip(),
                        date_format,
                    ).date()
                except ValueError:
                    continue

        raise ValueError(
            "Date of birth must be a valid date in DD/MM/YYYY format."
        )

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("Date of birth cannot be in the future.")

        return value

    @field_validator("glucose", "haemoglobin", "cholesterol")
    @classmethod
    def validate_blood_values(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("Blood test values must be finite numbers.")

        return value


class PatientCreate(PatientBase):
    pass


class PatientUpdate(PatientBase):
    pass


class PatientResponse(PatientBase):
    id: int
    remarks: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)