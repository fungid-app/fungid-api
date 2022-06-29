import aiohttp
import asyncio
import uvicorn
import sys
from datetime import datetime
from pathlib import Path
from fastai import *
from fastai.vision.core import *
from fastai.vision.utils import *
from io import BytesIO
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from core.integratedclassifier import IntegratedClassifier
from core.georaster import KGRaster, EluRaster
from core.observation_factory import ObservationFactory
from core.helpers import *

disk = '/var/data/'
download_url = "https://nyc3.digitaloceanspaces.com/inciteful/fungid/v0.4/"
model_file_name = 'image-model.pkl'
kg_file_name = 'kg.tif'
elu_file_name = 'elu.tif'
db_file_name = 'db.sqlite'

to_download_files = [
    model_file_name,
    kg_file_name,
    elu_file_name,
    db_file_name,
]

to_download_files = [(download_url + f, disk + f) for f in to_download_files]

classes = ['black', 'grizzly', 'teddys']

app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=[
                   '*'], allow_headers=['X-Requested-With', 'Content-Type'])


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


loop = asyncio.get_event_loop()

for file in to_download_files:
    loop.run_until_complete(download_file(file[0], file[1]))

loop.close()

classifier = IntegratedClassifier(
    disk + model_file_name, disk + db_file_name, cpu=True)
obs_factory = ObservationFactory(
    KGRaster(disk + kg_file_name), EluRaster(disk + elu_file_name, disk + db_file_name))


async def parse_images_from_request(form_data):
    images = []
    for i in range(0, 100):
        form_name = 'image' + str(i)
        try:
            img_bytes = await (form_data[form_name].read())
            img = PILImage.create(BytesIO(img_bytes))
            images.append(img)
        except:
            break

    return images


@ app.route('/analyze', methods=['POST'])
async def analyze(request):
    form_data = await request.form()
    images = await parse_images_from_request(form_data)
    date = form_data['date']
    lat = float(form_data['lat'])
    lon = float(form_data['lon'])
    date = datetime.strptime(date, '%Y-%m-%d')
    obs = obs_factory.create(images, lat, lon, date)
    results = classifier.get_all_predictions(obs).to_json()

    return JSONResponse(results)


if __name__ == '__main__':
    if 'serve' in sys.argv:
        uvicorn.run(app=app, host='0.0.0.0', port=5000, log_level="info")
