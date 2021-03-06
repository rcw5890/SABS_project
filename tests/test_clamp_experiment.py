# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 15:06:09 2019

@author: yanral
"""
import sabs_pkpd
import numpy as np
import myokit
import unittest


class Test(unittest.TestCase):
    def test_get_steady_state(self):

        # model_filename1 = 'C:/Users/yanral/Documents/Software Development/
        # mmt_models/tentusscher_2006.mmt'

        # model_filename2 = 'C:/Users/yanral/Documents/Software Development/
        # mmt_models/ohara_rudy_cipa_v1_2017.mmt'
        model_filename1 = './mmt_models/tentusscher_2006.mmt'
        model_filename2 = './mmt_models/ohara_rudy_cipa_v1_2017.mmt'

        sabs_pkpd.constants.s = \
            sabs_pkpd.load_model.load_simulation_from_mmt(model_filename1)
        time_ss = 6000
        res = \
            sabs_pkpd.clamp_experiment.get_steady_state(sabs_pkpd.constants.s,
                                                        time_ss)
        expected1 = np.array([-85.38, 0.0001062, 3.65, 0.000224, 0.986, 10.11,
                              135.38, 0.0002083, 0.4727, 0.003254, 0.001663,
                              0.749, 0.748, 3.312e-05, 0.9709, 0.999, 0.99996,
                              0.999998, 2.363e-08])
        res = np.array(res[0][0])
        rel_diff = abs((expected1 - res) / res)
        print(np.nanmax(rel_diff) < 0.05)

        sabs_pkpd.constants.s = [sabs_pkpd.constants.s]
        sabs_pkpd.constants.s.append(sabs_pkpd.load_model.
                                     load_simulation_from_mmt(model_filename2))
        res2 = \
            sabs_pkpd.clamp_experiment.get_steady_state(sabs_pkpd.constants.s,
                                                        time_ss)
        expected2 = np.array([-87.93, 0.01287, 7.279, 7.279, 144.64, 144.64,
                              8.720e-05, 8.622e-05, 1.620, 1.562, 0.0074,
                              0.6956, 0.6956, 0.6955, 0.452, 0.6955, 0.0001909,
                              0.4968, 0.2661, 0.001006, 0.9995, 0.5637,
                              0.0005126, 0.9995, 0.6161, 2.381e-09, 0.9999,
                              0.9018, 0.9999, 0.9996, 0.9999, 0.9999, 0.9999,
                              0.002916, 0.9996, 6.9304e-05, 1.827e-08,
                              8.385e-05, 0.0001583, 5.791e-05, 0.0, 0.0, 0.0,
                              0.0, 0.2847, 0.0001944, 0.9968, 2.496e-07,
                              3.118e-07])
        test1 = np.array(res2[0][0])
        rel_diff = abs((expected1 - test1) / test1)
        assert np.nanmax(rel_diff) < 0.05
        test2 = np.array(res2[1][0])
        rel_diff2 = abs((expected2 - test2) / test2)
        assert np.nanmax(rel_diff2) < 0.05

        # Test the exceptions
        with self.assertRaises(ValueError) as context:
            res = sabs_pkpd.clamp_experiment.get_steady_state('not_sim',
                                                              time_ss)
        assert 's should be provided as' in str(context.exception)

        with self.assertRaises(ValueError) as context:
            res = sabs_pkpd.clamp_experiment.get_steady_state(['not_sim'],
                                                              time_ss)
        assert 's should be provided as' in str(context.exception)

        with self.assertRaises(ValueError) as context:
            res = sabs_pkpd.clamp_experiment.get_steady_state(
                sabs_pkpd.constants.s, time_ss, data_exp='not_data_exp')
        assert 'data_exp should contain' in str(context.exception)

        # Test providing data exp
        sabs_pkpd.constants.n = 2
        sabs_pkpd.constants.s = \
            sabs_pkpd.load_model.load_simulation_from_mmt(
                './tests/test resources/pints_problem_def_test.mmt')

        fit_param_annot = ['constants.unknown_cst', 'constants.unknown_cst2']
        exp_cond_annot = 'constants.T'
        model_output_annot = 'comp1.y'
        sabs_pkpd.constants.data_exp = \
            sabs_pkpd.load_data.load_data_file(
                './tests/test resources/load_data_test.csv')
        sabs_pkpd.constants.data_exp.Add_fitting_instructions(
            fit_param_annot, exp_cond_annot, model_output_annot)
        res = sabs_pkpd.clamp_experiment.get_steady_state(
            sabs_pkpd.constants.s,
            time_ss,
            data_exp=sabs_pkpd.constants.data_exp)

        res = sabs_pkpd.clamp_experiment.get_steady_state(
            [sabs_pkpd.constants.s],
            time_ss,
            data_exp=sabs_pkpd.constants.data_exp)

        # Test providing save location
        model_filename1 = './mmt_models/tentusscher_2006.mmt'
        model_filename2 = './mmt_models/ohara_rudy_cipa_v1_2017.mmt'
        save_location = './mmt_models/test_save_get_steady_state'
        list_of_models_names = ['TT06', 'Ohara 2017']
        time_ss = 6000
        sabs_pkpd.constants.s = \
            [sabs_pkpd.load_model.load_simulation_from_mmt(model_filename1)]
        sabs_pkpd.constants.s.append(
            sabs_pkpd.load_model.load_simulation_from_mmt(model_filename2))
        res = sabs_pkpd.clamp_experiment.get_steady_state(
            sabs_pkpd.constants.s,
            time_ss,
            save_location=save_location,
            list_of_models_names=list_of_models_names)

        # Test wrong number of model names
        list_of_models_names = ['TT06', 'Ohara 2017', 'wrong model']
        with self.assertRaises(ValueError) as context:
            res = sabs_pkpd.clamp_experiment.get_steady_state(
                sabs_pkpd.constants.s,
                time_ss,
                save_location=save_location,
                list_of_models_names=list_of_models_names)

    def test_save_steady_state_to_mmt(self):
        # model_filename1 = 'C:/Users/yanral/Documents/Software Development/
        # mmt_models/tentusscher_2006.mmt'

        # model_filename2 = 'C:/Users/yanral/Documents/Software Development/
        # mmt_models/ohara_rudy_cipa_v1_2017.mmt'
        model_filename1 = './mmt_models/tentusscher_2006.mmt'
        model_filename2 = './mmt_models/ohara_rudy_cipa_v1_2017.mmt'

        time_ss = 6000
        sabs_pkpd.constants.s = \
            [sabs_pkpd.load_model.load_simulation_from_mmt(model_filename1)]
        sabs_pkpd.constants.s.append(sabs_pkpd.load_model.
                                     load_simulation_from_mmt(model_filename2))
        res = sabs_pkpd.clamp_experiment.get_steady_state(
            sabs_pkpd.constants.s, time_ss)

        list_of_models_names = ['TT06', 'Ohara 2017']
        save_location = './mmt_models/test_save_steady_state'
        sabs_pkpd.clamp_experiment.save_steady_state_to_mmt(
            sabs_pkpd.constants.s, res, list_of_models_names, save_location)

        assert True

    def test_clamp_experiment_model(self):
        modelname = './tests/test resources/pints_problem_def_test.mmt'

        # Design the clamp protocol
        time_max = 30
        n_timepoints = 10
        time_samples = np.linspace(2, time_max, n_timepoints)
        read_out = 'comp1.x'
        exp_clamped_parameter_annot = 'comp1.y'
        exp_clamped_parameter_values = 1 + np.sin(time_samples)

        p = myokit.Protocol()
        for i in range(len(time_samples) - 1):
            p.schedule(exp_clamped_parameter_values[i],
                       time_samples[i],
                       time_samples[i + 1] - time_samples[i])

        # Save the new model and protocol if the user provided the argument
        # save_new_mmt_filename
        newmodelname = './tests/test resources/model_clamped.mmt'

        m = sabs_pkpd.clamp_experiment.clamp_experiment_model(
            modelname,
            exp_clamped_parameter_annot,
            'engine.pace',
            p,
            newmodelname)

        s = sabs_pkpd.load_model.load_simulation_from_mmt(newmodelname)

        s.reset()
        # reset timer
        s.set_time(0)

        a = s.run(time_max, log_times=time_samples)
        output = a[read_out]

        expected_output = np.array([0.00901, 0.02621, 0.00976, 0.02642,
                                    0.00952, 0.02661, 0.00935, 0.02676,
                                    0.00922])
        diff = np.linalg.norm(output - expected_output)

        assert diff < 0.001
