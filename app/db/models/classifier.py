from typing import Optional
from sqlalchemy import BigInteger, Column, Index, Integer
from torch import autocast_increment_nesting
from sqlmodel import SQLModel, Field


class ClassifierObservations(SQLModel, table=True):
    __tablename__: str = 'classifier_observations'

    specieskey: int = Field(primary_key=True)
    decimallatitude: float = Field(primary_key=True)
    decimallongitude: float = Field(primary_key=True)

    gbifid: int = Field(sa_column=Column(
        BigInteger(), primary_key=True, unique=True))
    __table_args__ = (
        Index('observations_specieskey_latitude_longitutde', "specieskey",
              "decimallatitude", "decimallongitude"),
    )


class ClassifierEluValues(SQLModel, table=True):
    __tablename__: str = 'classifier_elu_values'
    eluid: int = Field(sa_column=Column(
        Integer, autoincrement=False, primary_key=True))
    class1: Optional[str]
    class2: Optional[str]
    class3: Optional[str]


class ClassifierSpeciesStats(SQLModel, table=True):
    __tablename__: str = "classifier_speciesstats"
    species: Optional[int] = Field(primary_key=True)
    stat: Optional[str] = Field(primary_key=True)
    value: Optional[str] = Field(primary_key=True)
    likelihood: Optional[float]


class ClassifierSpecies(SQLModel, table=True):
    __tablename__: str = 'classifier_species'

    family: Optional[str]
    genus: Optional[str]
    species: Optional[str] = Field(primary_key=True)
    familykey: Optional[int]
    genuskey: Optional[int]
    specieskey: Optional[int] = Field(primary_key=True)
    total: Optional[int] = Field(primary_key=True)


class DbPediaData(SQLModel, table=True):
    __tablename__: str = "dbpedia"
    id: int = Field(primary_key=True)
    prop: Optional[str]
    species: Optional[str]
    value: Optional[str]
    __table_args__ = (
        Index('dbpedia_species_prop_value_idx', "species",
              "prop", "value", unique=True),
    )
