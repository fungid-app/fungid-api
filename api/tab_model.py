import pandas as pd
import sqlite3

from torch import Tensor, tensor
from .observation import Observation


class TabModel():
    def __init__(self, connection_string: str):
        self.species_stats = get_species_stats(connection_string)

    def get_predictions(self, observation: Observation) -> pd.Series:
        stats = pd.concat([
            self.species_stats.loc[('kg', str(observation.kg))],
            self.species_stats.loc[('elu_class1', observation.elu_class1)],
            self.species_stats.loc[('elu_class2', observation.elu_class2)],
            self.species_stats.loc[('elu_class3', observation.elu_class3)],
            self.species_stats.loc[('normalizedmonth',
                                    str(observation.normalized_month()))],
            self.species_stats.loc[('season', observation.season())]
        ]).groupby('species').sum()

        max_val = stats.likelihood.max()
        return (stats.likelihood + max_val) / (max_val * 2)
        # return stats.likelihood / max_val


def get_species_stats(connection_string: str) -> pd.DataFrame:
    species_stats = None

    with sqlite3.connect(connection_string) as con:
        species_stats = pd.read_sql_query(
            "SELECT s.species, s.stat, s.value, s.likelihood FROM speciesstats s;", con)

        species_stats = species_stats.set_index(
            ['stat', 'value', 'species'])

        species_stats = species_stats.sort_index(
            level=species_stats.index.names)

    if species_stats is None:
        raise Exception("Error getting species stats")

    return species_stats
