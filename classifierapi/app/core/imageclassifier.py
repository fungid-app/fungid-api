from fastai.vision.all import load_learner, PILImage
from typing import Tuple
import pandas as pd


class ImageClassifier:
    def __init__(self, filename: str, cpu=True):
        self.learner = load_learner(filename, cpu=cpu)
        self.vocab = pd.DataFrame(self.learner.dls.vocab, columns=[
                                  "species"]).set_index("species")

    def get_predictions(self, images: list[PILImage]) -> Tuple[pd.Series, pd.DataFrame]:
        df = pd.DataFrame(
            pd.concat([self._get_prediction(image, str(i))
                      for i, image in enumerate(images)], axis=1)
        )
        return df.mean(axis=1), df  # type: ignore

    def _get_prediction(self, image: PILImage, idx: str) -> pd.Series:
        _, _, probs = self.learner.predict(image)
        val = self.vocab.copy()
        val[idx] = probs
        return val[idx]
