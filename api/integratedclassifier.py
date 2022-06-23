from .observation import Observation
from .imageclassifier import ImageClassifier
from .tab_model import TabModel
import pandas as pd


class IntegratedClassifier:
    def __init__(self, image_classifier: ImageClassifier, tab_model: TabModel):
        self.image_classifier = image_classifier
        self.tab_model = tab_model

    def get_all_predictions(self, obs: Observation) -> pd.DataFrame:
        image_probs = self.image_classifier.get_predictions(obs.image)
        tab_probs = self.tab_model.get_predictions(obs)
        return image_probs.join(tab_probs)

    def get_combined_predictions(self, obs: Observation) -> pd.DataFrame:
        return self.get_all_predictions(obs).apply(lambda x: x.max(), axis=1)
