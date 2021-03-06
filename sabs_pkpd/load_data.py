import numpy as np
from operator import itemgetter


class FittingInstructions():
    """
    This class stores the fitting instructions for parameter inference.

    Attributes
    ----------
    fitted_params_annot : list of strings
        mmt model annotations of the fitted parameters. Ex
        ['constants.unknown_cst']
    exp_cond_param_annot : str
        mmt model annotation of the variable specifying the experimental
        conditions. It should correspond to the annotation of the experimental
        condition varying when generating the data.
    sim_output_param_annot : str
        mmt model annotation of the simulation output of interest.
    """
    def __init__(self,
                 fitted_params_annot,
                 exp_cond_param_annot,
                 sim_output_param_annot):
        self.fitted_params_annot = fitted_params_annot
        self.exp_cond_param_annot = exp_cond_param_annot
        self.sim_output_param_annot = sim_output_param_annot


class Data_exp():
    def __init__(self, times, values, exp_nums, exp_conds):
        self.times = times
        self.values = values
        self.exp_nums = exp_nums
        self.exp_conds = exp_conds
        self.fitting_instructions = None

    def Add_fitting_instructions(self,
                                 fitted_params_annot,
                                 exp_cond_param_annot,
                                 sim_output_param_annot):
        self.fitting_instructions = \
            FittingInstructions(fitted_params_annot,
                                exp_cond_param_annot,
                                sim_output_param_annot)


def load_data_file(filename, headers: bool = True):
    # Data should be provided in 4 columns:
    # time, data, experiment number, experiment condition
    data = np.loadtxt(filename, delimiter=',', skiprows=int(headers))

    if len(data[:, 0]) != len(data[:, 1]):
        raise ValueError('The times and values must have the same length')
    if type(data[0][0]) == str:
        raise ValueError('The CSV file is not in the standard format. '
                         'Please refer to the documentation. (More than one '
                         'line of headers)')

    if len(data[0]) > 4:
        raise ValueError('The CSV file is not in the standard format. Please '
                         'refer to the documentation. (Too many columns)')

    # Sorting the list in increasing times and experimental condition

    data = sorted(data, key=itemgetter(3, 0))
    data = np.concatenate([i for i in data])
    data = data.reshape(len(data) // 4, 4)
    exp_nums_list = list(set(data[:, 2]))
    exp_conds_list = list(set(data[:, 3]))
    times = []
    values = []

    for i in range(len(exp_nums_list)):
        temp = data[data[:, 2] == exp_nums_list[i]]
        times.append(temp[:, 0])
        values.append(temp[:, 1])

    return Data_exp(times, values, exp_nums_list, exp_conds_list)
