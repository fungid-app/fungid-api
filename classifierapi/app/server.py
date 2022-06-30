from core.integratedclassifier import IntegratedClassifier
from core.georaster import KGRaster, EluRaster
from core.observation_factory import ObservationFactory

import uvicorn
import sys
from datetime import datetime
from io import BytesIO
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from fastai.vision.core import PILImage
from core.helpers import *
import os

disk = os.environ.get('DISK')
model_file_name = os.environ.get('MODEL_FILE_NAME')
kg_file_name = os.environ.get('KG_FILE_NAME')
elu_file_name = os.environ.get('ELU_FILE_NAME')
db_file_name = os.environ.get('DB_FILE_NAME')

if disk is None or model_file_name is None or kg_file_name is None or elu_file_name is None or db_file_name is None:
    print("Missing environment variables")
    sys.exit(1)

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

app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=[
                   '*'], allow_headers=['X-Requested-With', 'Content-Type'])


@ app.route('/', methods=['POST'])
async def analyze(request):
    form_data = await request.form()
    images = await parse_images_from_request(form_data)
    date = form_data['date']
    lat = float(form_data['lat'])
    lon = float(form_data['lon'])
    date = datetime.strptime(date, '%Y-%m-%d')
    obs = obs_factory.create(images, lat, lon, date)
    results = classifier.get_combined_predictions(obs).to_json()

    return JSONResponse(results)


@ app.route('/healthcheck', methods=['GET'])
async def healthcheck(request):
    return JSONResponse({'status': 'ok'})

if __name__ == '__main__':
    uvicorn.run(app=app, host='0.0.0.0', port=8080, log_level="info")
