from datetime import datetime
from operator import index
import pandas as pd
import sqlite3

from torch import Tensor, tensor
from observation import Observation


class TabModel():
    def __init__(self, vocab: pd.DataFrame):
        self.species_stats = get_species_stats()
        self.vocab = vocab

    def get_stats(self, observation: Observation) -> pd.DataFrame:
        stats = pd.concat([
            self.species_stats.loc[('kg', str(observation.kg))],
            self.species_stats.loc[('elu_class1', observation.elu_class1)],
            self.species_stats.loc[('elu_class2', observation.elu_class2)],
            self.species_stats.loc[('elu_class3', observation.elu_class3)],
            self.species_stats.loc[('normalizedmonth',
                                    str(observation.normalized_month()))],
            self.species_stats.loc[('season', observation.season())]
        ]).groupby('species').sum()
        return self.vocab.join(stats)

    def get_tensor(self, observation) -> Tensor:
        stats = self.get_stats(observation)
        return tensor(stats['likelihood'].values)


def get_species_stats() -> pd.DataFrame:
    species_stats = None

    with sqlite3.connect('dbs/fungid.sqlite') as con:
        species_stats = pd.read_sql_query(
            "SELECT s.species, s.stat, s.value, s.likelihood FROM speciesstats s;", con)

    if species_stats is None:
        raise Exception("Error getting species stats")

    species_stats = species_stats.set_index(
        ['stat', 'value', 'species'])
    species_stats = species_stats.sort_index(
        level=species_stats.index.names)

    return species_stats


if __name__ == "__main__":
    vocab = pd.read_csv('dbs/training/vocab-v0-3.csv', index_col='species')
    tab_model = TabModel(vocab=vocab)
    observation = Observation(52.905696, -1.225849, datetime.now(), kg=1,
                              elu_class1="Artificial or Urban Area", elu_class2=None, elu_class3=None)

    print(tab_model.get_stats(observation))

    # print(tab_model.get_tensor(observation))
