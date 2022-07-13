from datetime import datetime
from typing import Union

from pydantic import BaseModel


class CommonNameBase(BaseModel):
    name: str
    language: Union[str, None] = None


class CommonNameCreate(CommonNameBase):
    pass


class CommonName(CommonNameBase):
    id: int
    species_id: int

    class Config:
        orm_mode = True


class GbifObservationImageBase(BaseModel):
    imgid: int
    external_url: str
    rights_holder: Union[str, None] = None
    creator: Union[str, None] = None
    license: Union[str, None] = None


class GbifObservationImageCreate(GbifObservationImageBase):
    pass


class GbifObservationImage(GbifObservationImageBase):
    id: int
    observation_id: int
    is_thumbnail: bool

    class Config:
        orm_mode = True


class GbifObservationBase(BaseModel):
    gbifid: int
    datecreated: datetime
    latitude: float
    longitude: float
    public: bool
    acces_rights: Union[str, None] = None
    right_holder: Union[str, None] = None
    recorded_by: Union[str, None] = None
    license: Union[str, None] = None
    countrycode: Union[str, None] = None
    state_province: Union[str, None] = None
    county: Union[str, None] = None
    municipality: Union[str, None] = None
    locality: Union[str, None] = None


class GbifObservationCreate(GbifObservationBase):
    pass


class GbifObservation(GbifObservationBase):
    species_id: int
    observer_id: int
    images: list[GbifObservationImage] = []

    class Config:
        orm_mode = True


class GbifObserverBase(BaseModel):
    name: str


class GbifObserverCreate(GbifObserverBase):
    pass


class GbifObserver(GbifObserverBase):
    id: int
    # observations: list[GbifObservation] = []

    class Config:
        orm_mode = True


class SpeciesBase(BaseModel):
    phylum: Union[str, None] = None
    classname: Union[str, None] = None
    order: Union[str, None] = None
    family: Union[str, None] = None
    genus: Union[str, None] = None
    species: str
    description: Union[str, None] = None
    included_in_classifier: bool
    number_of_observations: int


class SpeciesCreate(SpeciesBase):
    pass


class Species(SpeciesBase):
    id: int
    common_names: list[CommonName] = []
    # observations: list[GbifObservation] = []

    class Config:
        orm_mode = True
