from .classifier.observation import Observation
from .classifier.imageclassifier import ImageClassifier
from .classifier.tab_model import TabModel
from .classifier.location_model import LocationModel
import pandas as pd


class IntegratedClassifier:
    def __init__(self,
                 img_classifier_path: str,
                 db_str: str,
                 cpu=True):
        self.image_classifier = ImageClassifier(img_classifier_path, cpu=cpu)
        self.tab_model = TabModel(db_str)
        self.location_model = LocationModel(db_str)

    def get_all_predictions(self, obs: Observation, only_local=True) -> pd.DataFrame:
        image_probs, _ = self.image_classifier.get_predictions(obs.images)
        df = pd.DataFrame(image_probs, columns=['image'])
        tab_probs = self.tab_model.get_predictions(obs)
        location_probs = self.location_model.get_predictions(obs.lat, obs.long)
        df = pd.concat([df, tab_probs, location_probs], axis=1)

        if only_local:
            df = df.loc[location_probs.index]

        return df

    def get_combined_predictions(self, obs: Observation, only_local=True) -> pd.Series:
        df = self.get_all_predictions(obs, only_local=only_local)
        df = df.fillna(.5).prod(axis=1)
        df = df/df.sum()
        return df.sort_values(ascending=False)
