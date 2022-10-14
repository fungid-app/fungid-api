from fastapi_pagination import add_pagination
import uvicorn
from fastapi import FastAPI
from routers import classifier, taxonomy, observations
from fastapi.staticfiles import StaticFiles
from decouple import config

build_env = str(config('BUILD_ENV'))

servers = []

if(build_env != "development"):
    servers.append(
        {
            "url": "https://api.fungid.app",
            "description": "Production server"
        }
    )

app = FastAPI(
    debug=True,
    docs_url='/', title="FungID API",
    contact={
        "name": "FungID",
        "url": "https://fungid.app",
        "email": "michael@fungid.app"
    },
    version="0.0.1",
    servers=servers,
)


static_folder = str(config('STATIC_FILES'))
app.mount("/static", StaticFiles(directory=static_folder), name="static")

obs_imgs_folder = str(config('OBSERVATION_IMAGES'))
app.mount("/images/observations",
          StaticFiles(directory=obs_imgs_folder), name="obs_images")

app.include_router(classifier.router)
app.include_router(taxonomy.router)
app.include_router(observations.router)


@app.get('/healthcheck')
async def healthcheck():
    return {'status': 'ok'}

add_pagination(app)

if __name__ == '__main__':
    # debug = os.environ.get('BUILD_ENV') == 'DEBUG'
    # print("debug: " + str(debug))
    uvicorn.run("__main__:app", host='0.0.0.0', port=8080)
