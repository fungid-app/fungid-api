from typing import Optional
import datetime
import pandas as pd
import fastai.vision.core as vs


class Observation:
    def __init__(self, images: list[vs.PILImage], lat: float, long: float, date: datetime.datetime, kg: int, elu_class1: Optional[str], elu_class2: Optional[str], elu_class3: Optional[str]):
        self.images = images
        self.lat = lat
        self.long = long
        self.date = date
        self.kg = kg
        self.elu_class1 = elu_class1
        self.elu_class2 = elu_class2
        self.elu_class3 = elu_class3

    def normalized_month(self) -> int:
        if(self.lat < 0):
            return ((self.date.month + 6) % 12) + 1
        else:
            return self.date.month

    def season(self) -> str:
        normalizedmonth = self.normalized_month()
        if normalizedmonth in [12, 1, 2]:
            return "winter"
        elif normalizedmonth in [3, 4, 5]:
            return "spring"
        elif normalizedmonth in [6, 7, 8]:
            return "summer"
        else:
            return "autumn"

    def full_observation(self) -> pd.Series:
        return pd.Series({
            "image": self.images[0],
            "decimallatitude": self.lat,
            "decimallongitude": self.long,
            "season": self.season(),
            "normalized_month": self.normalized_month(),
            "kg": self.kg,
            "elu_class1": self.elu_class1,
            "elu_class2": self.elu_class2,
            "elu_class3": self.elu_class3
        })
