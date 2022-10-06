from fastapi import APIRouter
from decouple import config
import sys
from datetime import datetime
from typing import Dict
from io import BytesIO
from fastai.vision.core import PILImage
from fastapi import UploadFile
from classifier.predictions import FullPredictions
from classifier.helpers import *
from classifier.integratedclassifier import IntegratedClassifier
from classifier.location_model import LocationModel
from classifier.imageclassifier import ImageClassifier
from classifier.tab_model import TabModel
from classifier.georaster import KGRaster, EluRaster
from classifier.observation_factory import ObservationFactory

router = APIRouter(
    tags=["classifier"],
    prefix="/classifier"
)

disk = str(config('DISK'))
model_file_name = str(config('MODEL_FILE_NAME'))
kg_file_name = str(config('KG_FILE_NAME'))
elu_file_name = str(config('ELU_FILE_NAME'))
db_file_name = str(config('DB_FILE_NAME'))


if disk is None or model_file_name is None or kg_file_name is None or elu_file_name is None or db_file_name is None:
    print("Missing environment variables")
    sys.exit(1)

db_con_str = disk + db_file_name

full_classifier = IntegratedClassifier(
    disk + model_file_name, db_con_str, cpu=True)
location_classifier = LocationModel(db_con_str)
tab_classifier = TabModel(db_con_str)
image_classifier = ImageClassifier(disk + model_file_name, cpu=True)

obs_factory = ObservationFactory(
    KGRaster(disk + kg_file_name), EluRaster(disk + elu_file_name, disk + db_file_name))


async def parse_images_from_request(images: list[UploadFile]):
    parsed_images: list[PILImage] = []
    for i in range(0, 100):
        try:
            img_bytes = await (images[i].read())
            img: PILImage = PILImage.create(BytesIO(img_bytes))  # type: ignore
            parsed_images.append(img)
        except:
            break

    return parsed_images


@router.put('/full', response_model=FullPredictions)
async def evaluate_full_classifier(date: datetime, lat: float, lon: float, images: list[UploadFile]):
    parsed_images = await parse_images_from_request(images)
    obs = obs_factory.create(parsed_images, lat, lon, date)
    return full_classifier.get_combined_predictions(obs)
    

@router.get('/location', response_model=Dict[str, float])
async def evaluate_location_classifier(lat: float, lon: float):
    return location_classifier.get_predictions(lat, lon).to_dict()
    
@router.get('/tabular', response_model=Dict[str, float])
async def evaluate_tabular_classifier(date: datetime, lat: float, lon: float):
    obs = obs_factory.create([], lat, lon, date)
    return tab_classifier.get_predictions(obs).to_dict()

@router.put('/image', response_model=Dict[str, float])
async def evaluate_image_classifier(images: list[UploadFile]):
    parsed_images = await parse_images_from_request(images)
    preds, _ = image_classifier.get_predictions(parsed_images)
    return preds.to_dict()
    