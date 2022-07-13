from sqlmodel import Session
from .models import core


def get_species(db: Session, name: str):
    return db.query(core.Species).filter(core.Species.species == name)


def get_all_species(db: Session):
    return db.query(core.Species)


def get_species_by_id(db: Session, id: int):
    return db.query(core.Species).filter(core.Species.id == id)


def observations_by_species(db: Session, species: str):
    return db.query(core.GbifObservation).filter(core.GbifObservation.species.species == species)


def get_all_observations(db: Session):
    return db.query(core.GbifObservation)


def get_observation_by_id(db: Session, gbifid: int):
    return db.query(core.GbifObservation).filter(core.GbifObservation.gbifid == gbifid)


def get_all_images(db: Session):
    return db.query(core.GbifObservationImage)


def get_observation_images_by_observation_id(db: Session, observation_id: int):
    return db.query(core.GbifObservationImage).filter(core.GbifObservationImage.observation_id == observation_id)


def get_observation_images_by_id(db: Session, id: int):
    return db.query(core.GbifObservationImage).filter(core.GbifObservationImage.id == id)
