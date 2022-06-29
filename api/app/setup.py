from core.integratedclassifier import IntegratedClassifier
from core.georaster import KGRaster, EluRaster
from core.observation_factory import ObservationFactory
from pathlib import Path
from fastai import *
from fastai.vision.core import *
from fastai.vision.utils import *
import aiohttp
import asyncio
from core.helpers import *


async def download_file(url, dest):
    dest = Path(dest)

    if dest.exists():
        print("found: ", dest)
        return

    print("downloading: ", dest)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
            with open(dest, 'wb') as f:
                f.write(data)


def download_files(files_to_download):
    loop = asyncio.get_event_loop()

    for file in files_to_download:
        loop.run_until_complete(download_file(*file))

    loop.close()


def setup():
    disk = '/var/data/'

    download_url = "https://nyc3.digitaloceanspaces.com/inciteful/fungid/v0.4/"
    model_file_name = 'image-model.pkl'
    kg_file_name = 'kg.tif'
    elu_file_name = 'elu.tif'
    db_file_name = 'db.sqlite'

    files_to_download = [
        model_file_name,
        kg_file_name,
        elu_file_name,
        db_file_name,
    ]

    files_to_download = [(download_url + f, disk + f)
                         for f in files_to_download]

    download_files(files_to_download)
    classifier = IntegratedClassifier(
        disk + model_file_name, disk + db_file_name, cpu=True)
    obs_factory = ObservationFactory(
        KGRaster(disk + kg_file_name), EluRaster(disk + elu_file_name, disk + db_file_name))

    return (classifier, obs_factory)
