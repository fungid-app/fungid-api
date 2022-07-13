from sqlalchemy.orm import Session

from . import models, schemas


def get_species(db: Session, name: str):
    return db.query(models.Species).filter(models.Species.species == name)


def get_all_species(db: Session):
    return db.query(models.Species)


def get_species_by_id(db: Session, id: int):
    return db.query(models.Species).filter(models.Species.id == id)


def observations_by_species(db: Session, species: str):
    return db.query(models.GbifObservation).filter(models.GbifObservation.species.species == species)


def get_all_observations(db: Session):
    return db.query(models.GbifObservation)


def get_observation_by_id(db: Session, gbifid: int):
    return db.query(models.GbifObservation).filter(models.GbifObservation.gbifid == gbifid)


def get_all_images(db: Session):
    return db.query(models.GbifObservationImage)


def get_observation_images_by_observation_id(db: Session, observation_id: int):
    return db.query(models.GbifObservationImage).filter(models.GbifObservationImage.observation_id == observation_id)


def get_observation_images_by_id(db: Session, id: int):
    return db.query(models.GbifObservationImage).filter(models.GbifObservationImage.id == id)
