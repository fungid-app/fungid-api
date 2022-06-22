import observation as obs
import georaster as gr
import datetime


class ObservationFactory:
    def __init__(self):
        self.kgraster = gr.KGRaster()
        self.eluraster = gr.EluRaster()

    def make_observation(self, lat: float, long: float, date: datetime.datetime) -> obs.Observation:
        kg = self.kgraster.get_value(lat, long)
        elu_class1, elu_class2, elu_class3 = self.eluraster.get_classes(
            lat, long)
        return obs.Observation(lat=lat, long=long, date=date, kg=kg, elu_class1=elu_class1, elu_class2=elu_class2, elu_class3=elu_class3)


if __name__ == "__main__":
    observation_factory = ObservationFactory()
    observation = observation_factory.make_observation(52.905696, -1.225849, date=datetime.datetime(
        year=2020, month=1, day=1))
    print(observation.full_observation())
