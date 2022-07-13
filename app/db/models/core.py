from datetime import datetime
from tkinter.tix import Tree
from typing import List, Optional
from sqlalchemy import BigInteger, Column, ForeignKey, Index
from sqlmodel import Relationship, SQLModel, Field, UniqueConstraint

# DROP TABLE IF EXISTS gbif_observations;
# DROP TABLE IF EXISTS gbif_observation_images;
# DROP TABLE IF EXISTS gbif_observers;
# DROP TABLE IF EXISTS species;
# DROP TABLE IF EXISTS common_names;
# DROP TABLE IF EXISTS dbpedia;


class CommonName(SQLModel, table=True):
    __tablename__: str = "common_names"

    id: int = Field(primary_key=True)
    name: Optional[str]
    language: Optional[str]
    species_id: Optional[int] = Field(foreign_key="species.id",
                                      index=True)
    species: "Species" = Relationship(back_populates="common_names")

    __table_args__ = (
        Index('cn_species_name_language', "species_id", "name",
              "language", unique=True),
    )


class Species(SQLModel, table=True):
    __tablename__: str = "species"

    id: int = Field(primary_key=True)
    phylum: Optional[str] = Field(index=True)
    classname: Optional[str] = Field(index=True)
    order: Optional[str] = Field(index=True)
    family: Optional[str] = Field(index=True)
    genus: Optional[str] = Field(index=True)
    species: Optional[str]
    description: Optional[str]
    included_in_classifier: bool = Field(default=False)
    number_of_observations: Optional[int]

    __table_args__ = (
        Index("ix_species_species", "species", unique=True),
        Index("species_included_in_classifier_index",
              "included_in_classifier", "id", unique=True),
    )

    common_names: List[CommonName] = Relationship(back_populates="species")


class GbifObserver(SQLModel, table=True):
    __tablename__: str = "gbif_observers"

    id: int = Field(primary_key=True)
    name: Optional[str]

    observations: List["GbifObservation"] = Relationship(
        back_populates="observer")
    __table_args__ = (
        UniqueConstraint("name"),
    )


class GbifObservationImage(SQLModel, table=True):
    __tablename__: str = "gbif_observation_images"
    id: int = Field(primary_key=True)
    imgid: Optional[int]
    external_url: Optional[str]
    rights_holder: Optional[str]
    creator: Optional[str]
    license: Optional[str]
    is_thumbnail: bool = Field(default=False)
    observation_id: Optional[int] = Field(
        foreign_key="gbif_observations.gbifid", index=True)

    observation: "GbifObservation" = Relationship(back_populates="images")


class GbifObservation(SQLModel, table=True):
    __tablename__: str = "gbif_observations"
    gbifid: int = Field(sa_column=Column(
        BigInteger(), autoincrement=False, primary_key=True))

    datecreated: Optional[datetime]
    latitude: Optional[float]
    longitude: Optional[float]
    public: Optional[bool]
    acces_rights: Optional[str]
    rights_holder: Optional[str]
    recorded_by: Optional[str]
    license: Optional[str]
    countrycode: Optional[str]
    state_province: Optional[str]
    county: Optional[str]
    municipality: Optional[str]
    locality: Optional[str]

    species_id: Optional[int] = Field(foreign_key="species.id",
                                      index=True)

    species: Species = Relationship(back_populates="observations")

    observer_id: Optional[int] = Field(
        foreign_key="gbif_observers.id")

    observer: GbifObserver = Relationship(back_populates="observations")

    images: List[GbifObservationImage] = Relationship(
        back_populates="observation")

    __table_args__ = (
        Index('obs_gbifobs_sp_lat_lon_pub_idx', "species_id",
              "latitude", "longitude", "public"),
        Index('obs_gbifobs_observer_idx', "observer_id")
    )
