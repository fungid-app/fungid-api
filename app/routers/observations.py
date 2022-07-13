from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import crud, schemas
from dependencies import get_db
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

router = APIRouter(
    tags=["observations"],
    prefix="/observations"
)


@router.get("/", response_model=Page[schemas.GbifObservation])
def get_all_observations(db: Session = Depends(get_db)):
    return paginate(crud.get_all_observations(db))


@router.get("/{id}", response_model=schemas.GbifObservation)
def get_observations_by_id(id: int, db: Session = Depends(get_db)):
    return crud.get_observation_by_id(db, id)


@router.get("/{observation_id}/images", response_model=Page[schemas.GbifObservationImage])
def get_observation_images_by_observation_id(observation_id: int, db: Session = Depends(get_db)):
    return paginate(crud.get_observation_images_by_observation_id(db, observation_id))


@router.get("/images", response_model=Page[schemas.GbifObservationImage])
def get_observation_images(db: Session = Depends(get_db)):
    return paginate(crud.get_all_images(db))


@router.get("/images/{image_id}", response_model=schemas.GbifObservationImage)
def get_image_by_id(image_id: int, db: Session = Depends(get_db)):
    return crud.get_observation_images_by_id(db, image_id)
