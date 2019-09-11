import pandas as pd
import numpy as np

from ..ab_base import BaseAB


class Flex3v4(BaseAB):
    '''Flex3v4 test inherited from base
    Experiment A: Flex 3 for $120
    Experiment B: Flex 4 for $160

    Args:
    sub_df              a dataframe consisting of PS subscriber data
    participant_path    path & filename to the participant file
                        default: '../../../data/ab_experiments/star_wars/experiments_lists.csv'
    simulations         number of monte carlo simulations for distribution
                        default: 1,000,000
    prior_a             bias from prior knowledge or expecation of experiment A
                        default: 1.0 (no bias)
    prior_b             bias from prior knowledge or expecation of experiment B
                        default: 1.0 (no bias)
    kwargs              available for additional experiments, options include:
                        prior_c: 1.0,
                        prior_d: 1.0,
                        etc.
    '''

    _DEFAULT_PARTICIPANT_PATH = '../../data/ab_experiments/flex3v4/'
    _DEF_FILE_FLEX3 = 'flex3.csv'
    _DEF_FILE_FLEX4 = 'flex4.csv'

    def __init__(self, sub_df,
                 participant_path=_DEFAULT_PARTICIPANT_PATH,
                 flex3_file = _DEF_FILE_FLEX3,
                 flex4_file = _DEF_FILE_FLEX4,
                 simulations=1000000, prior_a=1.0, prior_b=1.0, **kwargs):
        super().__init__(simulations, prior_a, prior_b, **kwargs)

        self._path = participant_path
        self._flex3 = pd.read_csv(self._path + flex3_file, header=None, names=['ids'])
        self._flex4 = pd.read_csv(self._path + flex4_file, header=None, names=['ids'])
        self._data = sub_df
        self._unique_subs = set(self._data.customer_no)

        self.assign_experiment(self._flex3, 'a')
        self.assign_experiment(self._flex4, 'b')

        self._participants_df = self.combine_ab(self._flex3, self._flex4)

        for key, val in self._experiment_info.items():

            participant_mask = self._participants_df['experiment'] == key
            participants = set(self._participants_df.loc[participant_mask]['ids'])

            converts = participants & self._unique_subs
            convert_mask = self._data.customer_no.isin(converts)

            filtered = self._data.loc[convert_mask]

            self._experiment_info[key]['summary'] = {
                'participants': len(participants),
                'customers': len(filtered.customer_no.unique()),
                'packages': np.sum(filtered.num_seats),
                'revenue': np.sum(filtered.tot_due_amt),
                'successes': len(filtered.customer_no.unique()),
                'failures': len(participants) - len(filtered.customer_no.unique())
            }

    def assign_experiment(self, df, experiment):
        options = ['a', 'b']
        if experiment.lower() not in options:
            raise Exception('Must only assign experiment as "a" or "b".')

        df['experiment'] = f'experiment_{experiment.lower()}'

    def combine_ab(self, a_df, b_df):
        df = a_df.append(b_df).reset_index(drop=True)
        return df
