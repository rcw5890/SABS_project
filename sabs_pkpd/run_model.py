import myokit
import sabs_pkpd
import numpy as np
import matplotlib.pyplot as plt


def simulate_data(fitted_params_values, s, data_exp, pre_run=0):
    """
    This function runs the model in the same conditions (and with the same time
    sampling) as the experimental data loaded in data_exp.

    :param fitted_params_values: list
        List of the values for the fitted parameters. It has to match the
        length of fitting parameters annotations.
    :param s: Myokit.Simulation
        Myokit simulation defined by the chosen model and protocol.
    :param data_exp: Data_exp
        Contains the data that the model is fitted too. See documentation for
        sabs_pkpd.load_data for further info
    :param pre_run: int
        Defines the time for which the model is run without returning output.
        Useful for reaching (quasi-) steady-state
    :return: output : list
        List of the same shape as data_exp.times. It contains the model output
        in the given conditions at the time points used to generate the
        experimental data.
    """

    # Allocate memory for the output
    output = []

    # Verify that the parameters for fitting and their values have the same
    # length
    if len(fitted_params_values) != \
            len(data_exp.fitting_instructions.fitted_params_annot):
        raise ValueError('Fitted parameters annotations and values should '
                         'have the same length')

    # Run the model solving for all experiment conditions
    for k in range(0, len(set(data_exp.exp_conds))):
        s.reset()
        # reset timer
        s.set_time(0)

        # Set initial value of state variable parameters
        if sabs_pkpd.constants.default_state is not None:
            state_to_set = sabs_pkpd.constants.default_state
        else:
            state_to_set = s.state()

        for i in range(0,
                       len(data_exp.fitting_instructions.fitted_params_annot)):
            if sabs_pkpd.pints_problem_def.parameter_is_state(
                    data_exp.fitting_instructions.fitted_params_annot[i],
                    s):
                index = sabs_pkpd.pints_problem_def.find_index_of_state(
                    data_exp.fitting_instructions.fitted_params_annot[i],
                    s)
                state_to_set[index] = fitted_params_values[i]

        # Set the value of the initial state to what it should be
        s.set_state(state_to_set)

        # Set constant parameters values.
        for i in range(0,
                       len(data_exp.fitting_instructions.fitted_params_annot)):
            if not sabs_pkpd.pints_problem_def.parameter_is_state(
                    data_exp.fitting_instructions.fitted_params_annot[i],
                    s):
                s.set_constant(
                    data_exp.fitting_instructions.fitted_params_annot[i],
                    fitted_params_values[i])

        # set the right experimental conditions
        s.set_constant(data_exp.fitting_instructions.exp_cond_param_annot,
                       list(data_exp.exp_conds)[k])

        # Eventually run a pre-run to reach steady-state
        s.pre(pre_run)

        # Run the simulation with starting parameters
        a = s.run(data_exp.times[k][-1] * 1.00001, log_times=data_exp.times[k])

        # Convert output in concentration
        output.append(
            list(a[data_exp.fitting_instructions.sim_output_param_annot]))

    return output


def quick_simulate(s,
                   time_max,
                   read_out: str,
                   exp_cond_param_annot=None,
                   exp_cond_param_values=None,
                   fixed_params_annot=None,
                   fixed_params_values=None,
                   pre_run=0,
                   time_samples=None):

    """
    This function returns a simulation for any desired conditions.

    Note that s is not reloaded here, meaning that if you previously set a
    constant in a previous simulation, this will not be changed until you
    either reset manually the constant's value (s.set_constant()) or reload the
    mmt model.

    :param s: Myokit.Simulation
        Myokit simulation defined by the chosen model and protocol.

    :param time_max: int
        Maximal time for which the model is run

    :param read_out: str
        MMT model annotation of the variable read out as output from the model
        simulation.

    :param exp_cond_param_annot: str
        MMT model annotation of the experimental condition varying when
        generating the data.

    :param exp_cond_param_values: list
        List of values for the experimental condition in which the model should
        be run. The model solving is looped over the experimental condition
        values (1 run per value).

    :param fixed_params_annot: list of str
        List of the MMT model annotations of the constants set for the
        simulation.

    :param fixed_params_values: list
        List of values for the constants set for the simulation.

    :param pre_run: int
        Defines the time for which the model is run without returning output.
        Useful for reaching (quasi-) steady-state

    :param time_samples: list
        time points for which the model output is returned.

    :return: output : list
        List of shape (len(experimental condition values), time_samples). It
        contains the model output in the given conditions at the time points
        used to generate the experimental data.
    """
    if sabs_pkpd.constants.default_state is None:
        print('No default state was provided in '
              'sabs_pkpd.constants.default_state. Simulating with initial '
              'conditions provided with the .mmt model...')

    if time_samples is not None:
        if time_samples[-1] > time_max:
            raise ValueError('The time samples have to be within the range '
                             '(0 , time_max)')

    if fixed_params_values is not None or fixed_params_annot is not None:
        if len(fixed_params_annot) != len(fixed_params_values):
            raise ValueError('The parameters clamped for the simulation must '
                             'have the same length for names and values')

    if exp_cond_param_values is not None or exp_cond_param_annot is not None:
        if (not isinstance(exp_cond_param_values, list) and not
                isinstance(exp_cond_param_values, np.ndarray)) or \
                not isinstance(exp_cond_param_annot, str):
            raise ValueError('The experimental conditions must be provided as '
                             'a list or numpy.ndarray, and the parameter '
                             'annotation must be a string matching with the '
                             'variable name in the MMT model')
        if len(fixed_params_annot) != len(fixed_params_values):
            raise ValueError('The parameters clamped for the simulation must '
                             'have the same length for names and values')

    if time_samples is None:
        time_samples = np.linspace(0, time_max, 100)

    # Prepare variable for the output
    output = []

    # Run the model solving for all experiment conditions
    # In case the user wants some parameter to vary between simulations
    if exp_cond_param_values is not None:
        for k, exp_val in enumerate(exp_cond_param_values):
            s.reset()
            # reset timer
            s.set_time(0)

            # Set initial value of state variable parameters
            if sabs_pkpd.constants.default_state is not None:
                state_to_set = sabs_pkpd.constants.default_state
            else:
                state_to_set = s.state()
            if fixed_params_annot is not None:
                for i, annot in enumerate(fixed_params_annot):
                    if sabs_pkpd.pints_problem_def.\
                            parameter_is_state(annot, s):
                        index = sabs_pkpd.pints_problem_def.\
                            find_index_of_state(annot, s)
                        state_to_set[index] = fixed_params_values[i]
                    else:
                        s.set_constant(annot, fixed_params_values[i])

            s.set_state(state_to_set)

            # set the right experimental conditions
            s.set_constant(exp_cond_param_annot, exp_val)

            # Eventually run a pre-run to reach steady-state
            s.pre(pre_run)

            # Run the simulation with starting parameters
            a = s.run(time_max * 1.000001, log_times=time_samples)
            # Convert output in concentration
            output.append(list(a[read_out]))
    else:
        s.reset()

        # Set initial value of state variable parameters
        if sabs_pkpd.constants.default_state is not None:
            state_to_set = sabs_pkpd.constants.default_state
        else:
            state_to_set = s.state()
        # reset timer
        s.set_time(0)

        # Set parameters for simulation
        if fixed_params_annot is not None:
            for i, annot in enumerate(fixed_params_annot):
                if sabs_pkpd.pints_problem_def.parameter_is_state(annot, s):
                    index = sabs_pkpd.pints_problem_def.\
                        find_index_of_state(annot, s)
                    state_to_set[index] = fixed_params_values[i]
                else:
                    s.set_constant(annot, fixed_params_values[i])

        # Set the state to the value corresponding to the eventual clamp or exp
        # condition
        s.set_state(state_to_set)

        # Eventually run a pre-run to reach steady-state
        s.pre(pre_run)

        # Run the simulation with starting parameters
        a = s.run(time_max * 1.00001, log_times=time_samples)
        # Convert output in concentration
        output.append(list(a[read_out]))

    return output


def plot_model_vs_data(plotting_parameters_annot,
                       plotting_parameters_values,
                       data_exp,
                       s,
                       pre_run=0,
                       figsize=(20, 20)):
    """
    This function plots the experimental data and the output of the model for
    parameters rescaled as precised by the user

    :param plotting_parameters_annot:
    List of strings. Model annotations for the parameters the user wants to
    rescale for the plotting

    :param plotting_parameters_values:
    List or numpy.array. Contains the values for the parameters annotated with
    plotting_params_annot

    :param data_exp:
    Data_exp class. Contains all the experimental data. The fitting
    instructions must have been initialised previously.

    :param s:
    myokit.Simulation. myokit object used to run the model.

    :param pre_run:
    Length of pre-run to apply to the model to reach steady-state

    :param figsize:
    Tuple. Defines the size of the figure for the plots. If not specified, it
    is (20, 20)

    :return: None

    """
    # Retrieve conditions in which to reproduce data
    print('Running the model with pre_run : ' + str(pre_run))
    read_out = data_exp.fitting_instructions.sim_output_param_annot
    exp_cond_param_annot = data_exp.fitting_instructions.exp_cond_param_annot
    fixed_params_annot = list(plotting_parameters_annot)
    fixed_params_annot.append(exp_cond_param_annot)

    # Produce one plot per experimental condition used to generate the data
    number_of_plots = len(data_exp.exp_conds)

    if number_of_plots == 1:
        number_of_rows = 1
        fig1 = plt.figure()
    else:
        number_of_rows = number_of_plots // 2 \
            + number_of_plots % (number_of_plots // 2)
        fig1, axes = plt.subplots(number_of_rows, 2, figsize=figsize)

    for i in range(0, number_of_plots):
        if number_of_plots > 1:
            plt.subplot(number_of_rows, 2, i + 1)

        # Retrieve simulation parameters from the provided data in data_exp
        time_max = data_exp.times[i][-1]
        time_samples = data_exp.times[i]

        fixed_params_values = list(plotting_parameters_values)
        exp_cond_param_values = [data_exp.exp_conds[i]]
        fixed_params_values.append(data_exp.exp_conds[i])

        # Use quick_simulate to generate the model output corresponding to the
        # data
        sim_data = quick_simulate(s,
                                  time_max,
                                  read_out,
                                  exp_cond_param_annot,
                                  exp_cond_param_values,
                                  fixed_params_annot,
                                  fixed_params_values,
                                  time_samples=time_samples,
                                  pre_run=pre_run)

        # Plot the results
        plt.plot(time_samples, sim_data[0], label='Simulated values')
        plt.plot(time_samples, data_exp.values[i], label='Experimental data')
        plt.title('Experimental conditions : ' + exp_cond_param_annot + ' = '
                  + str(exp_cond_param_values))
        plt.xlabel('Time')
        plt.ylabel(data_exp.fitting_instructions.sim_output_param_annot)
        plt.legend()

    return 0
