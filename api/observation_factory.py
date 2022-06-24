from .observation import Observation
from .georaster import KGRaster, EluRaster
import datetime
import fastai.vision.core as vs


class ObservationFactory:
    def __init__(self, kgraster: KGRaster, eluraster: EluRaster):
        self.kgraster = kgraster
        self.eluraster = eluraster

    def make_observation(self, images: list[vs.PILImage], lat: float, long: float, date: datetime.datetime) -> Observation:
        kg = self.kgraster.get_value(lat, long)
        elu_class1, elu_class2, elu_class3 = self.eluraster.get_classes(
            lat, long)
        return Observation(images, lat=lat, long=long, date=date, kg=kg, elu_class1=elu_class1, elu_class2=elu_class2, elu_class3=elu_class3)
