from .observation import Observation
from .imageclassifier import ImageClassifier
from .tab_model import TabModel
from .location_model import LocationModel
import pandas as pd


class IntegratedClassifier:
    def __init__(self,
                 img_classifier_path: str,
                 db_str: str,
                 cpu=True):
        self.image_classifier = ImageClassifier(img_classifier_path, cpu=cpu)
        self.tab_model = TabModel(db_str)
        self.location_model = LocationModel(db_str)

    def get_all_predictions(self, obs: Observation) -> pd.DataFrame:
        image_probs, _ = self.image_classifier.get_predictions(obs.images)
        df = pd.DataFrame(image_probs, columns=['image'])
        tab_probs = self.tab_model.get_predictions(obs)
        location_probs = self.location_model.get_predictions(obs.lat, obs.long)
        return pd.concat([df, tab_probs, location_probs], axis=1)

    def get_combined_predictions(self, obs: Observation) -> pd.DataFrame:
        return self.get_all_predictions(obs).apply(lambda x: x.max(), axis=1)
