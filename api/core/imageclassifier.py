from numpy import integer
from pandas import DataFrame
from .helpers import *
import fastbook
import fastai.vision.core as vs
from typing import Tuple, Union


class ImageClassifier:
    def __init__(self, filename: str, cpu=True):
        self.resize = Resize(224, ResizeMethod.Pad, pad_mode='zeros')
        self.learner = fastbook.load_learner(filename, cpu=cpu)
        self.vocab = pd.DataFrame(self.learner.dls.vocab, columns=[
                                  "species"]).set_index("species")

    def get_predictions(self, images: list[vs.PILImage]) -> Tuple[pd.Series, pd.DataFrame]:
        df = pd.DataFrame(
            pd.concat([self._get_prediction(image, str(i))
                      for i, image in enumerate(images)], axis=1)
        )
        return df.mean(axis=1), df  # type: ignore

    def _get_prediction(self, image: vs.PILImage, idx: str) -> pd.Series:
        resized = self.resize(image)
        _, _, probs = self.learner.predict(resized)
        val = self.vocab.copy()
        val[idx] = probs
        return val[idx]


if __name__ == "__main__":
    import os
    path = os.getenv("IMAGE_CLASSIFIER_PATH")
    if(path is not None):
        image_classifier = ImageClassifier(path)
        image = vs.PILImage.create("dbs/images/224/2593822195-1.png")

        if image is None:
            raise Exception("Image not found")

        preds = image_classifier.get_predictions([image])
        print(preds)
