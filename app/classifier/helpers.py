from fastai.vision.all import *
from fastai.data.external import *


def get_tab_model_data(data):
    tab_columns = ['kg', 'elu_class1', 'elu_class2', 'elu_class3',
                   'decimallatitude', 'decimallongitude', 'species', 'normalized_month', 'season']
    return data[tab_columns].copy()


def get_img_model_data(data):
    img_data = data.copy()
    img_data['img'] = 'dbs/images/224/' + \
        data.gbifid.astype(str) + '-' + \
        data.imgid.astype(int).astype(str) + '.png'
    return img_data[['img', 'species']]


def get_results(learner, data):
    row, clas, probs = learner.predict(data)
    # print(clas)
    return probs


def get_bounding_box(lat, lon, dist):
    latdiff = (180 / math.pi) * (dist / 6378137)
    londiff = (180 / math.pi) * (dist / 6378137) / math.cos(lat)
    return (lat - latdiff, lon - londiff), (lat + latdiff, lon + londiff)


# def obs_from_series(series: pd.Series, image_locs: list[str]) -> Observation:
#     images = [PILImage.create(img) for img in image_locs]
#     if images is None:
#         raise Exception("Could not load image: ", series.img)

#     date = datetime.strptime(series.eventdate, '%Y-%m-%d %H:%M:%S')
#     return Observation(images, series.decimallatitude, series.decimallongitude,
#                        date, series.kg, series.elu_class1, series.elu_class2, series.elu_class3)
