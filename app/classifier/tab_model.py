import pandas as pd
import sqlite3

from classifier.observation import Observation


class TabModel():
    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def get_predictions(self, observation: Observation) -> pd.Series:
        with sqlite3.connect(self.connection_string) as con:
            params = (
                str(observation.kg),
                observation.elu_class1,
                observation.elu_class2,
                observation.elu_class3,
                str(observation.normalized_month()),
                observation.season()
            )

            stats = pd.read_sql_query(
                """SELECT species, SUM(likelihood) AS tab_score
                FROM classifier_speciesstats s
                WHERE (
                    stat = 'kg' AND value = ?
                    OR stat = 'elu_class1' AND value = ?
                    OR stat = 'elu_class2' AND value = ?
                    OR stat = 'elu_class3' AND value = ?
                    OR stat = 'normalizedmonth' AND value = ?
                    OR stat = 'season' AND value = ?
                )
                GROUP BY species""", con,
                params=params  # type: ignore
            ).set_index('species')

            max_val = stats.tab_score.max()
            return (((stats.tab_score / max_val) + 1) / 2).sort_values(ascending=False)

    def get_seasonal(self, normalized_month: int) -> pd.Series:
        with sqlite3.connect(self.connection_string) as con:

            stats = pd.read_sql_query(
                """SELECT species, SUM(likelihood) AS tab_score
                FROM classifier_speciesstats s
                WHERE stat = 'normalizedmonth' AND value = ?
                GROUP BY species""", con,
                params=(normalized_month,)  # type: ignore
            ).set_index('species')

            max_val = stats.tab_score.max()
            return (stats.tab_score / max_val)
