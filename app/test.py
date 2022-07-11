import os
import sqlite3
from typing import Optional
from core.integratedclassifier import IntegratedClassifier
from core.observation_factory import ObservationFactory
from core.tab_model import TabModel
from core.imageclassifier import ImageClassifier
from core.observation import Observation
from core.georaster import KGRaster, EluRaster
from core.helpers import *
import fastai.vision.core as vs
from datetime import datetime


def get_env_var(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise Exception(f"{name} must be set")

    return value


def get_image() -> vs.PILImage:
    image = vs.PILImage.create("dbs/images/224/2593822195-1.png")
    if image is None:
        raise Exception("Image not found")
    return image


def get_observation() -> Observation:
    return Observation([get_image()], 52.905696, -1.225849, datetime.now(), kg=1,
                       elu_class1="Artificial or Urban Area", elu_class2=None, elu_class3=None)


def get_image_classifier() -> ImageClassifier:
    path = get_env_var("MODEL_FILE_NAME")
    return ImageClassifier(path)


def get_tab_model() -> TabModel:
    sqlite = get_env_var("SQLITE_PATH")
    return TabModel(sqlite)


def get_integrated_classifier():
    ic = IntegratedClassifier(get_env_var(
        "MODEL_FILE_NAME"), get_env_var("SQLITE_PATH"))
    return ic


def observation_factory():
    kgpath = get_env_var("KG_FILE_NAME")
    elupath = get_env_var("ELU_FILE_NAME")
    sqlite = get_env_var("DB_FILE_NAME")

    return ObservationFactory(
        KGRaster(kgpath), EluRaster(elupath, sqlite))


def test_observation_factory():
    obs_factory = observation_factory()
    observation = obs_factory.create([get_image()], 52.905696, -1.225849, date=datetime(
        year=2020, month=1, day=1))

    print(observation.full_observation())


def test_integrated_classifier():
    observation = get_observation()
    ic = get_integrated_classifier()
    preds = ic.get_combined_predictions(observation, False)
    print(preds)


if __name__ == "__main__":
    test_integrated_classifier()
