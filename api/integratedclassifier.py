from observation import Observation
import imageclassifier as ic
import tab_model as tm
import pandas as pd


class IntegratedClassifier:
    def __init__(self, image_classifier: ic.ImageClassifier, tab_model: tm.TabModel):
        self.image_classifier = image_classifier
        self.tab_model = tab_model

    def get_all_predictions(self, obs: Observation) -> pd.DataFrame:
        image_probs = self.image_classifier.get_predictions(obs.image)
        tab_probs = self.tab_model.get_predictions(obs)
        return image_probs.join(tab_probs)

    def get_combined_predictions(self, obs: Observation) -> pd.DataFrame:
        return self.get_all_predictions(obs).apply(lambda x: x.max(), axis=1)
