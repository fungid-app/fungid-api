from fastapi import APIRouter
from decouple import config
import sys
from datetime import date, datetime
from typing import Dict
from io import BytesIO
from fastai.vision.core import PILImage
from fastapi import UploadFile
from classifier.observation import normalized_month
from classifier.predictions import BasicPrediction, ClassifierVersion, FullPredictions
from classifier.integratedclassifier import IntegratedClassifier
from classifier.location_model import LocationModel
from classifier.imageclassifier import ImageClassifier
from classifier.tab_model import TabModel
from classifier.georaster import KGRaster, EluRaster
from classifier.observation_factory import ObservationFactory
import pandas as pd

from typing import TypeVar, Generic
from fastapi import Query
from fastapi_pagination import paginate
from fastapi_pagination.default import Page as BasePage, Params as BaseParams

T = TypeVar("T")


class Params(BaseParams):
    size: int = Query(500, ge=1, le=10_000, description="Page size")


class Page(BasePage[T], Generic[T]):
    __params_type__ = Params


router = APIRouter(
    tags=["classifier"],
    prefix="/classifier"
)

model_version = str(config('MODEL_VERSION'))
model_image_size = int(config('MODEL_IMAGE_SIZE'))
model_path = str(config('MODEL_PATH'))
kg_file_name = str(config('KG_FILE_PATH'))
elu_file_name = str(config('ELU_FILE_PATH'))
db_file_name = str(config('DB_FILE_PATH'))


if model_version is None or model_path is None or model_image_size is None or kg_file_name is None or elu_file_name is None or db_file_name is None:
    print("Missing environment variables")
    sys.exit(1)

full_classifier = IntegratedClassifier(
    model_path,
    model_version,
    db_file_name,
    cpu=True
)

location_classifier = LocationModel(db_file_name)
tab_classifier = TabModel(db_file_name)
image_classifier = ImageClassifier(model_path, cpu=True)

obs_factory = ObservationFactory(
    KGRaster(kg_file_name),
    EluRaster(elu_file_name, db_file_name)
)


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


@ router.put('/full', response_model=FullPredictions)
async def evaluate_full_classifier(date: datetime, lat: float, lon: float, images: list[UploadFile]):
    parsed_images = await parse_images_from_request(images)
    print(f"Received {len(parsed_images)} images")
    obs = obs_factory.create(parsed_images, lat, lon, date)
    return full_classifier.get_combined_predictions(obs)


@ router.get('/location', response_model=Dict[str, float])
async def evaluate_location_classifier(lat: float, lon: float):
    return location_classifier.get_predictions(lat, lon).to_dict()


@ router.get('/tabular', response_model=Dict[str, float])
async def evaluate_tabular_classifier(date: datetime, lat: float, lon: float):
    obs = obs_factory.create([], lat, lon, date)
    return tab_classifier.get_predictions(obs).to_dict()


@ router.put('/image', response_model=Dict[str, float])
async def evaluate_image_classifier(images: list[UploadFile]):
    parsed_images = await parse_images_from_request(images)
    preds, _ = image_classifier.get_predictions(parsed_images)
    return preds.to_dict()


@router.get("/version", response_model=ClassifierVersion)
async def get_version():
    return ClassifierVersion(version=model_version, image_size=model_image_size)


@router.get("/local", response_model=list[str])
async def get_local(lat: float, lon: float):
    preds = location_classifier.get_predictions(lat, lon)
    return preds.index.to_list()


@router.get("/seasonal", response_model=Page[BasicPrediction])
async def get_seasonal(lat: float, lon: float, date: date = datetime.now().date()):

    df = pd.DataFrame(location_classifier.get_predictions(lat, lon, 75))
    m = normalized_month(lat, date.month)
    df = df.join(tab_classifier.get_seasonal(m))
    df['score'] = df.prod(axis=1)
    df['score'] = df['score'] / df['score'].max()

    predictions = [
        BasicPrediction(
            species=getattr(row, 'Index'),
            probability=getattr(row, 'score'),
        )
        for row in df.sort_values(by='score', ascending=False).itertuples()
        if getattr(row, 'score') > .001]

    return paginate(predictions)
