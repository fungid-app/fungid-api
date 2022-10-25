from fastai.vision.all import load_learner, PILImage, Learner
from typing import Tuple
import pandas as pd
from scipy import stats
class ImageClassifier:
    def __init__(self, filename: str, cpu=True):
        self.learner: Learner = load_learner(filename, cpu=cpu)
        self.learner.no_mbar()
        self.learner.no_logging()
        self.vocab = pd.DataFrame(self.learner.dls.vocab, columns=[
                                  "species"]).set_index("species")

    def get_predictions(self, images: list[PILImage]) -> Tuple[pd.Series, pd.DataFrame]:
        df = self._get_predictions(images)
        
        df['image_score'] = stats.gmean(df, axis=1)
        return df.image_score.sort_values(ascending=False), df.drop(columns=['image_score'])

        # score = df.prod(axis=1)
        # score = score / score.sum()
        # return score.sort_values(ascending=False), df
    
        
    def _get_predictions(self, images: list[PILImage]) -> pd.DataFrame:
        test_dl = self.learner.dls.test_dl(images, num_workers=0)

        preds, _ = self.learner.get_preds(dl=test_dl, reorder=False)
        val = self.vocab.copy()
        for idx, pred in enumerate(preds):
            val[idx] = pred

        return val
 