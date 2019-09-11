import matplotlib.pyplot as plt
import seaborn as sns
from numpy.random import beta

class BaseAB:
    '''This is the base class for all future AB Experiments.
    Note: AB experiments may require just ticketing data, just subscription data,
    just donor data, or some combination of them. For that reason, we will keep
    them separate and prepare subclasses for each unique AB test.

    Args:
    simulations         number of monte carlo simulations for distribution
                        default = 1,000,000
    prior_a             bias from prior knowledge or expecation of experiment A
                        default = 1.0 (no bias)
    prior_b             bias from prior knowledge or expecation of experiment B
                        default = 1.0 (no bias)
    kwargs              available for additional experiments, options include:
                        prior_c: 1.0,
                        prior_d: 1.0,
                        etc.
    '''


    def __init__(self, simulations=1000000, prior_a=1.0, prior_b=1.0, **kwargs):
        self._simulations = 1000000
        self._experiment_info = {
            'experiment_a': {
                'prior': prior_a
            },
            'experiment_b': {
                'prior': prior_b
            }
        }

        if kwargs:
            check1 = 'prior_' # ensure the keywords are prior_
            check2 = [chr(ascii_dec) for ascii_dec in range(99, 99+24)] # lowercase alphabet
            for key, val in kwargs.items():
                if (key[:6] == check1) & (key[-1] in check2):
                    self._experiment_info[f"experiment_{key[-1]}"] = {
                        'prior': val
                    }
                else:
                    raise Exception(f'Unknown key included as an argument: {key}')


    def generate_posteriors(self):
        '''Generates posteriors
        '''
        posteriors = {}

        for key, val in self._experiment_info.items():
            posterior_name = f"experiment {key[-1].capitalize()}"
            posterior = beta(val['summary']['successes'] + 1,
                             val['summary']['failures'] + 1,
                             self._simulations)
            posteriors[posterior_name] = posterior

        self._posteriors = posteriors

        return print("Posteriors ready for plots")


    def plot_posteriors(self, plot_title, xlabel='conversion rate',
                        ylabel='samples', figsize=[15, 5]):
        '''Plots the generated posteriors (posteriors generated in sub classes)

        Args:
        posteriors          dictionary of posteriors generated from Monte Carlo sim
                            key: experiment (ex. 'experiment A')
                            val: posterior (ex. array([0.0414523, 0.0772763, ...]))
        plot_title          Title for generated plot
        xlabel              Label for x axis
                            default: 'conversion rate'
        ylabel              Label for y axis
                            default: 'samples'
        figsize             size of plot to be generated
                            default: [15, 5]

        '''
        colors = ['blue', 'red', 'green', 'gold', 'gray', 'orange', 'orchid', 'teal', 'snow']

        plt.figure(figsize=figsize)

        for key, val in self._posteriors.items():
            try:
                color = colors.pop(0)
            except:
                color = 'SteelBlue'     # set color if run out of colors in list provided

            sns.distplot(val, hist=False, kde=True, color=color,
                         kde_kws={'shade': True, 'linewidth': 1},
                         label=key)

        plt.legend(prop={'size': 15}, title='Experiments')
        plt.title(plot_title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        return plt.show()


    def plot_relative_difference(self, xlabel='percentage lift', figsize=[15, 5]):
        '''Plots the relative difference between posteriors
        (posteriors generated in sub classes)
        Only works with two posteriors (A, B) only.

        Args:
        posteriors          dictionary of posteriors generated from Monte Carlo sim
                            key: experiment (ex. 'experiment A')
                            val: posterior (ex. array([0.0414523, 0.0772763, ...]))
        xlabel              Label for x axis
                            default: 'percentage lift'
        figsize             size of plot to be generated
                            default: [15, 5]
        '''
        if len(self._posteriors) > 2:
            msg = 'This method can only handle two posteriors. Filter down to just two and try again.'
            raise Exception(msg)

        posterior_keys = list(self._posteriors.keys())
        posterior_vals = list(self._posteriors.values())
        posterior_a = posterior_vals[0]
        posterior_b = posterior_vals[1]

        relative_difference = (posterior_b - posterior_a) / posterior_a

        plt.figure(figsize=figsize)

        sns.distplot(relative_difference, hist=True, kde=True,
                     color='green', kde_kws={'linewidth': 1})

        plt.title(f"Relative Difference")
        plt.xlabel(xlabel)

        return plt.show()


    def __repr__(self):
        rep_str = f"{self.__class__.__name__}(simulations='{self._simulations}'"
        for key, val in self._experiment_info.items():
            rep_str += f", prior_{key[-1]}={val['prior']}"
        return rep_str + ')'

    def __str__(self):
        ret_str = ''

        for key, val in self._experiment_info.items():
            ret_str += f"{key}: {val['summary']} \n"

        return ret_str
