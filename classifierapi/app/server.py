import uvicorn
import sys
from datetime import datetime
from io import BytesIO
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from setup import setup
from fastai.vision.core import PILImage
from core.helpers import *

classifier, obs_factory = setup()


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
