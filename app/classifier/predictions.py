from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class InferredData(BaseModel):
    normalized_month: int
    season: str
    kg: int
    elu_class1: Optional[str]
    elu_class2: Optional[str]
    elu_class3: Optional[str]


class FullPrediction(BaseModel):
    species: str
    probability: float
    local_probability: float
    image_score: float
    tab_score: float
    local_score: float
    is_local: bool


class FullPredictions(BaseModel):
    predictions: list[FullPrediction]
    date: datetime
    inferred: InferredData
    version: str


class ClassifierVersion(BaseModel):
    version: str
    image_size: int
