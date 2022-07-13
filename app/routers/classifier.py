from fastapi import APIRouter
from decouple import config
import sys
from datetime import datetime
from typing import Dict
from io import BytesIO
from fastai.vision.core import PILImage
from fastapi import UploadFile

from classifier.integratedclassifier import IntegratedClassifier
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


classifier = IntegratedClassifier(
    disk + model_file_name, disk + db_file_name, cpu=True)
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


@router.put('/full', response_model=Dict[str, float])
async def classify(date: datetime, lat: float, lon: float, images: list[UploadFile]):
    parsed_images = await parse_images_from_request(images)
    obs = obs_factory.create(parsed_images, lat, lon, date)
    results: Dict[str, float] = classifier.get_combined_predictions(
        obs).to_dict()
    return results
