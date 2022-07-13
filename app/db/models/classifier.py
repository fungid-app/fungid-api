from sqlalchemy import BigInteger, Column, Float, Integer, PrimaryKeyConstraint, String, Index
from torch import autocast_increment_nesting

from ..database import Base


class ClassifierObservations(Base):
    __tablename__ = 'classifier_observations'
    gbifid = Column(BigInteger, unique=True)
    specieskey = Column(Integer)
    decimallatitude = Column(Float)
    decimallongitude = Column(Float)

    __table_args__ = (
        PrimaryKeyConstraint(
            specieskey,
            decimallatitude,
            decimallongitude,
            gbifid
        ),
        {})


Index('observations_specieskey_latitude_longitutde', ClassifierObservations.specieskey,
      ClassifierObservations.decimallatitude, ClassifierObservations.decimallongitude)


class ClassifierEluValues(Base):
    __tablename__ = 'classifier_elu_values'
    eluid = Column(Integer, primary_key=True, autoincrement=False)
    class1 = Column(String, nullable=True)
    class2 = Column(String, nullable=True)
    class3 = Column(String, nullable=True)


class ClassifierSpeciesStats(Base):
    __tablename__ = 'classifier_speciesstats'
    species = Column(Integer, nullable=True)
    stat = Column(String, nullable=True)
    value = Column(String, nullable=True)
    likelihood = Column(Float, nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint(
            species,
            stat,
            value,
        ),
        {})


class ClassifierSpecies(Base):
    __tablename__ = 'classifier_species'

    _family = Column(String, nullable=True)
    genus = Column(String, nullable=True)
    species = Column(String, nullable=True)
    familykey = Column(Integer, nullable=True)
    genuskey = Column(Integer, nullable=True)
    specieskey = Column(Integer, nullable=True)
    total = Column(Integer, nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint(
            species,
            specieskey,
            total,
        ),
        {})


class DbPediaData(Base):
    __tablename__ = "dbpedia"
    id = Column(Integer, primary_key=True)
    prop = Column(String)
    species = Column(String)
    value = Column(String)


Index('dbpedia_species_prop_value_idx', DbPediaData.species,
      DbPediaData.prop, DbPediaData.value, unique=True)
