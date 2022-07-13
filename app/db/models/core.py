from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Index
from sqlalchemy.orm import relationship

from ..database import Base

# DROP TABLE IF EXISTS gbif_observations;
# DROP TABLE IF EXISTS gbif_observation_images;
# DROP TABLE IF EXISTS gbif_observers;
# DROP TABLE IF EXISTS species;
# DROP TABLE IF EXISTS common_names;
# DROP TABLE IF EXISTS dbpedia;


class Species(Base):
    __tablename__ = "species"
    id = Column(Integer, primary_key=True)
    phylum = Column(String, nullable=True, index=True)
    classname = Column(String, nullable=True, index=True)
    order = Column(String, nullable=True, index=True)
    family = Column(String, nullable=True, index=True)
    genus = Column(String, nullable=True, index=True)
    species = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    included_in_classifier = Column(Boolean, default=False)
    number_of_observations = Column(Integer)

    common_names = relationship("CommonName", back_populates="species")
    observations = relationship("GbifObservation", back_populates="species")


Index("species_included_in_classifier_index",
      Species.included_in_classifier, Species.id, unique=True)


class CommonName(Base):
    __tablename__ = "common_names"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    language = Column(String, nullable=True)
    species_id = Column(Integer, ForeignKey("species.id"), index=True)
    species = relationship("Species", back_populates="common_names")


Index('cn_species_name_language', CommonName.species_id, CommonName.name,
      CommonName.language, unique=True)


class GbifObserver(Base):
    __tablename__ = "gbif_observers"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    observations = relationship("GbifObservation", back_populates="observer")


class GbifObservation(Base):
    __tablename__ = "gbif_observations"
    gbifid = Column(BigInteger, primary_key=True, autoincrement=False)
    datecreated = Column(DateTime)
    latitude = Column(Float)
    longitude = Column(Float)
    public = Column(Boolean, default=True)
    acces_rights = Column(String, nullable=True)
    rights_holder = Column(String, nullable=True)
    recorded_by = Column(String, nullable=True)
    license = Column(String, nullable=True)
    countrycode = Column(String, nullable=True)
    state_province = Column(String, nullable=True)
    county = Column(String, nullable=True)
    municipality = Column(String, nullable=True)
    locality = Column(String, nullable=True)

    species_id = Column(Integer, ForeignKey(
        "species.id"), nullable=True, index=True)
    species = relationship("Species", back_populates="observations")

    observer_id = Column(Integer, ForeignKey(
        "gbif_observers.id"), nullable=True)
    observer = relationship("GbifObserver", back_populates="observations")

    images = relationship("GbifObservationImage", back_populates="observation")


Index('obs_gbifobs_sp_lat_lon_pub_idx', GbifObservation.species_id,
      GbifObservation.latitude, GbifObservation.longitude, GbifObservation.public)

Index('obs_gbifobs_observer_idx', GbifObservation.observer_id)


class GbifObservationImage(Base):
    __tablename__ = "gbif_observation_images"
    id = Column(Integer, primary_key=True)
    imgid = Column(Integer)
    external_url = Column(String)
    rights_holder = Column(String)
    creator = Column(String)
    license = Column(String)
    is_thumbnail = Column(Boolean, default=False)
    observation_id = Column(Integer, ForeignKey(
        "gbif_observations.gbifid"), index=True)
    observation = relationship("GbifObservation", back_populates="images")
