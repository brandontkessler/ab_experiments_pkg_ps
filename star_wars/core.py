import pandas as pd
import numpy as np

from ..ab_base import BaseAB


class StarWars(BaseAB):
    '''StarWars test inherited from base

    Args:
    ticketing_df        a dataframe consisting of PS ticketing data
                        df must drop na orders and order date must be converted to datetime
    participant_path    path & filename to the participant file
                        default: '../../../data/ab_experiments/star_wars/experiments_lists.csv'
    concert_date        date of concert in question
                        default: '8/17/2019 20:00:00'
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

    _DEFAULT_PARTICIPANT_PATH = '../../data/ab_experiments/star_wars/experiments_lists.csv'
    _DEFAULT_DATE_OF_CONCERT = pd.to_datetime('8/17/2019 20:00:00')

    def __init__(self, ticketing_df,
                 participant_path=_DEFAULT_PARTICIPANT_PATH,
                 concert_date=_DEFAULT_DATE_OF_CONCERT,
                 simulations=1000000, prior_a=1.0, prior_b=1.0, **kwargs):
        super().__init__(simulations, prior_a, prior_b, **kwargs)


        self._concert_date = concert_date
        self._ticket_df = ticketing_df.loc[ticketing_df.order_dt > concert_date] # filter
        self._unique_ticket_buyers = set(self._ticket_df.customer_no)

        self._participants_df = pd.read_csv(participant_path)
        for key, val in self._experiment_info.items():
            experiment = key[-1].capitalize()
            participant_mask = self._participants_df['experiment'] == experiment
            participants = set(self._participants_df.loc[participant_mask]['customer_no'])
            converts = participants & self._unique_ticket_buyers
            convert_mask = self._ticket_df.customer_no.isin(converts)
            paid_mask = self._ticket_df.paid_amt > 0
            filtered = self._ticket_df.loc[convert_mask & paid_mask]

            self._experiment_info[key]['summary'] = {
                'participants': len(participants),
                'customers': len(filtered.customer_no.unique()),
                'tickets': len(filtered.paid_amt),
                'revenue': np.sum(filtered.paid_amt),
                'successes': len(filtered.customer_no.unique()),
                'failures': len(participants) - len(filtered.customer_no.unique())
            }
