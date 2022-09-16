from datetime import datetime
from classifier.observation import Observation
from classifier.imageclassifier import ImageClassifier
from classifier.predictions import FullPrediction, FullPredictions, InferredData
from classifier.tab_model import TabModel
from classifier.location_model import LocationModel
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

        tab_probs = self.tab_model.get_predictions(obs)

        # Get Local Predcitions
        location_probs = self.location_model.get_predictions(obs.lat, obs.long)
        is_local = (location_probs > 0).rename('is_local')

        # Combine all predictions
        df = pd.DataFrame(image_probs, columns=['image_score'])
        df = pd.concat([df, tab_probs, location_probs, is_local], axis=1)

        # Fill empty local predictions
        df.is_local = df.is_local.fillna(False)
        df = df.fillna(.25)

        return df

    def get_combined_predictions_df(self, obs: Observation) -> pd.DataFrame:
        df = self.get_all_predictions(obs)

        df['score'] = df.prod(axis=1)
        df['probability'] = df.score/df.score.sum()
        df.loc[df.is_local, 'local_probability'] = (
            df.loc[df.is_local, 'score'] / df.loc[df.is_local, 'score'].sum())  # type: ignore

        return df.drop(columns=['score']).sort_values(by='probability', ascending=False)

    def get_combined_predictions(self, obs: Observation, min_score: float = .001) -> FullPredictions:
        df: pd.DataFrame = self.get_combined_predictions_df(obs)
        predictions = [
            FullPrediction(
                species=getattr(row, 'Index'),
                probability=getattr(row, 'probability'),
                local_probability=getattr(row, 'local_probability'),
                image_score=getattr(row, 'image_score'),
                tab_score=getattr(row, 'tab_score'),
                local_score=getattr(row, 'local_score'),
                is_local=getattr(row, 'is_local')
            )
            for row in df.itertuples()
            if getattr(row, 'probability') > min_score]

        return FullPredictions(
            predictions=predictions,
            date=datetime.now(),
            inferred=InferredData(
                normalized_month=obs.normalized_month(),
                season=obs.season(),
                kg=obs.kg,
                elu_class1=obs.elu_class1,
                elu_class2=obs.elu_class2,
                elu_class3=obs.elu_class3
            )
        )
