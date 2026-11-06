from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.patient import Patient
from app.schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
)
from app.services.health_ai import generate_health_remarks

router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
)


class PatientEmailUpdate(BaseModel):
    email: EmailStr


def calculate_age(date_of_birth: date) -> int:
    today = date.today()

    return (
        today.year
        - date_of_birth.year
        - (
            (today.month, today.day)
            < (date_of_birth.month, date_of_birth.day)
        )
    )


async def create_remarks(patient_data) -> str:
    age = calculate_age(patient_data.date_of_birth)

    return await generate_health_remarks(
        age=age,
        glucose=patient_data.glucose,
        haemoglobin=patient_data.haemoglobin,
        cholesterol=patient_data.cholesterol,
    )


@router.post(
    "/",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_patient(
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
):
    remarks = await create_remarks(patient_data)

    patient = Patient(
        **patient_data.model_dump(),
        remarks=remarks,
    )

    db.add(patient)
    db.commit()
    db.refresh(patient)

    return patient


@router.get(
    "/",
    response_model=list[PatientResponse],
)
def get_patients(db: Session = Depends(get_db)):
    return (
        db.query(Patient)
        .order_by(Patient.id.asc())
        .all()
    )


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient record not found.",
        )

    return patient


@router.put(
    "/{patient_id}",
    response_model=PatientResponse,
)
async def update_patient(
    patient_id: int,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient record not found.",
        )

    for field, value in patient_data.model_dump().items():
        setattr(patient, field, value)

    patient.remarks = await create_remarks(patient_data)

    db.commit()
    db.refresh(patient)

    return patient


@router.patch(
    "/{patient_id}/email",
    response_model=PatientResponse,
)
def update_patient_email(
    patient_id: int,
    email_data: PatientEmailUpdate,
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient record not found.",
        )

    patient.email = str(email_data.email)

    db.commit()
    db.refresh(patient)

    return patient


@router.delete(
    "/{patient_id}",
    status_code=status.HTTP_200_OK,
)
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient record not found.",
        )

    db.delete(patient)
    db.commit()

    return {
        "message": "Patient record deleted successfully.",
        "patient_id": patient_id,
    }