import os
import sqlite3
from typing import Optional
from integratedclassifier import IntegratedClassifier
from observation_factory import ObservationFactory
from tab_model import TabModel
from imageclassifier import ImageClassifier
from observation import Observation
import fastai.vision.core as vs
import georaster as gr
from helpers import *
from datetime import datetime


def get_image() -> vs.PILImage:
    image = vs.PILImage.create("dbs/images/224/2593822195-1.png")
    if image is None:
        raise Exception("Image not found")
    return image


def get_observation() -> Observation:
    return Observation(get_image(), 52.905696, -1.225849, datetime.now(), kg=1,
                       elu_class1="Artificial or Urban Area", elu_class2=None, elu_class3=None)


def get_image_classifier() -> ImageClassifier:
    path = os.getenv("IMAGE_CLASSIFIER_PATH")
    if(path is None):
        raise Exception("IMAGE_CLASSIFIER_PATH must be set")

    return ImageClassifier(path)


def get_tab_model() -> TabModel:
    sqlite = os.getenv("SQLITE_PATH")

    if sqlite is None:
        raise Exception("SQLITE_PATH must be set")

    return TabModel(sqlite)


def get_integrated_classifier():
    image_classifier = get_image_classifier()
    tab_model = get_tab_model()
    ic = IntegratedClassifier(image_classifier, tab_model)
    return ic


def test_observation_factory():
    kgpath = os.getenv("KG_RASTER_PATH")
    elupath = os.getenv("ELU_RASTER_PATH")
    if kgpath is None or elupath is None:
        raise Exception("KG_RASTER_PATH and ELU_RASTER_PATH must be set")

    observation_factory = ObservationFactory(
        gr.KGRaster(kgpath), gr.EluRaster(elupath))
    observation = observation_factory.make_observation(get_image(), 52.905696, -1.225849, date=datetime(
        year=2020, month=1, day=1))
    print(observation.full_observation())


def test_integrated_classifier():
    observation = get_observation()
    ic = get_integrated_classifier()
    preds = ic.get_all_predictions(observation)
    print(preds)


if __name__ == "__main__":
    test_integrated_classifier()
