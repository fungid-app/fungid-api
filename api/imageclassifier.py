from helpers import *
import fastbook
import fastai.vision.core as vs


class ImageClassifier:
    def __init__(self, filename: str, cpu=True):
        self.resize = Resize(224, ResizeMethod.Pad, pad_mode='zeros')
        self.learner = fastbook.load_learner(filename, cpu=cpu)
        self.vocab = pd.DataFrame(self.learner.dls.vocab, columns=[
                                  "species"]).set_index("species")

    def get_predictions(self, image: vs.PILImage) -> pd.DataFrame:
        resized = self.resize(image)
        _, _, probs = self.learner.predict(resized)
        val = self.vocab.copy()
        val["img_prob"] = probs
        return val


if __name__ == "__main__":
    import os
    path = os.getenv("IMAGE_CLASSIFIER_PATH")
    if(path is not None):
        image_classifier = ImageClassifier(path)
        image = vs.PILImage.create("dbs/images/224/2593822195-1.png")

        if image is None:
            raise Exception("Image not found")

        preds = image_classifier.get_predictions(image)
        print(preds)
