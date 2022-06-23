import pandas as pd
import sqlite3

from torch import Tensor, tensor
from observation import Observation


class TabModel():
    def __init__(self, con: sqlite3.Connection):
        self.species_stats = get_species_stats(con)

    def get_predictions(self, observation: Observation) -> pd.DataFrame:
        stats = pd.concat([
            self.species_stats.loc[('kg', str(observation.kg))],
            self.species_stats.loc[('elu_class1', observation.elu_class1)],
            self.species_stats.loc[('elu_class2', observation.elu_class2)],
            self.species_stats.loc[('elu_class3', observation.elu_class3)],
            self.species_stats.loc[('normalizedmonth',
                                    str(observation.normalized_month()))],
            self.species_stats.loc[('season', observation.season())]
        ]).groupby('species').sum()
        return stats

    def get_tensor(self, observation) -> Tensor:
        stats = self.get_predictions(observation)
        return tensor(stats['likelihood'].values)


def get_species_stats(con: sqlite3.Connection) -> pd.DataFrame:
    species_stats = pd.read_sql_query(
        "SELECT s.species, s.stat, s.value, s.likelihood FROM speciesstats s;", con)

    if species_stats is None:
        raise Exception("Error getting species stats")

    species_stats = species_stats.set_index(
        ['stat', 'value', 'species'])
    species_stats = species_stats.sort_index(
        level=species_stats.index.names)

    return species_stats
