from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db.models import core
from dependencies import get_db
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate

router = APIRouter(
    tags=["observations"],
    prefix="/observations"
)


@router.get("/", response_model=Page[core.GbifObservation])
def get_all_observations(db: Session = Depends(get_db)):
    return paginate(db, select(core.GbifObservation))


@router.get("/{id}", response_model=core.GbifObservation)
def get_observations_by_id(id: int, db: Session = Depends(get_db)):
    return db.exec(select(core.GbifObservation).filter(
        core.GbifObservation.gbifid == id)).first()


@router.get("/by_species/{species}", response_model=Page[core.GbifObservation])
def get_observations_by_species(species: str, db: Session = Depends(get_db)):
    return paginate(
        db,
        select(core.GbifObservation).join(core.Species).where(
            core.Species.species == species)
    )


@router.get("/{observation_id}/images", response_model=Page[core.GbifObservationImage])
def get_observation_images_by_observation_id(observation_id: int, db: Session = Depends(get_db)):
    return paginate(db,
                    select(core.GbifObservationImage).where(
                        core.GbifObservationImage.observation_id == observation_id)
                    )


@router.get("/images", response_model=Page[core.GbifObservationImage])
def get_observation_images(db: Session = Depends(get_db)):
    return paginate(db, select(core.GbifObservationImage))


@ router.get("/images/{image_id}", response_model=core.GbifObservationImage)
def get_image_by_id(image_id: int, db: Session = Depends(get_db)):
    return db.exec(
        select(core.GbifObservationImage).where(
            core.GbifObservationImage.id == image_id)
    ).first()
