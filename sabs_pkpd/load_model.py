"""This file contains functions for loading a model from file.

Functionality for parsing CellML models including conversion of stimulus
protocol) is included.
"""

import myokit
import myokit.formats.cellml
import myokit.formats
import sabs_pkpd


def convert_protocol(model):
    """Convert the cellml stimulus protocol the the correct format for myokit.

    CellML models may contain a stimulus current. Myokit's CellML import does
    not automatically convert the stimulus current into the Myokit pacing
    protocol. This function detects the stimulus protocol model component after
    import from CellML and parses the contents for rewriting in Myokit pacing
    format.

    Parameters
    ----------
    model : myokit.Model
        The model as imported from cellml

    Returns
    -------
    myokit.Model
        The model with corrected stimulus protocol
    myokit.Protocol
        stimulus protocol using Myokit's pacing system
    """
    # Get the original protocol from cellml
    original_protocol_component = model.get('stimulus_protocol',
                                            class_filter=myokit.Component)

    # Read the parameters from the original protocol
    equations = original_protocol_component.equations()
    pacing_parameters = {}
    for equation in equations:

        if equation.lhs.pystr() in ['stimulus_protocol_IstimStart',
                                    'stimulus_protocol_IstimPeriod',
                                    'stimulus_protocol_IstimPulseDuration']:
            pacing_parameters[equation.lhs.pystr()] = equation.rhs
        if equation.lhs.pystr() == 'IstimAmplitude':
            amplitude = equation.rhs

    # Add the level variable which is bound to pace
    level = original_protocol_component.add_variable('level')
    level.set_rhs(0)
    level.set_binding('pace')

    # Delete those variables which are no longer needed in the stimulus model
    # component
    variables_to_delete = []
    for variable in original_protocol_component.variables():

        if variable.name() == 'IstimAmplitude':
            variable.set_rhs(0.5)
        elif variable.name() == 'Istim':
            variable.set_rhs('level * IstimAmplitude')
        elif variable.name() == 'level':
            pass
        else:
            variables_to_delete.append(variable)

    for variable in variables_to_delete:
        original_protocol_component.remove_variable(variable)

    # Write the protocol in Myokit format
    new_protocol = myokit.Protocol()
    new_protocol.schedule(
        1.0,
        pacing_parameters['stimulus_protocol_IstimStart'],
        pacing_parameters['stimulus_protocol_IstimPulseDuration'],
        period=pacing_parameters['stimulus_protocol_IstimPeriod'],
        multiplier=0)

    return model, new_protocol


def load_model_from_cellml(cellml_filename, mmt_filename):
    """Load a model into Myokit from cellml file format.

    Parameters
    ----------
    cellml_filename : str
        Path to the CellML model
    mmt_filename : str
        Path to location to save the MMT model

    Returns
    -------
    None

    """
    if 'cellml' not in myokit.formats.importers():
        raise Exception('cellml support not detected in your Myokit')

    importer = myokit.formats.importer('cellml')
    model = importer.model(cellml_filename)

    # Try to parse the stimulus protocol from the CellML model
    try:
        model, prot = convert_protocol(model)
        myokit.save_model(mmt_filename, model)

    # If the names of variables do not match, just load the model as is
    except KeyError:
        myokit.save_model(mmt_filename, model)

    sim = load_simulation_from_mmt(mmt_filename)
    return sim


def load_simulation_from_mmt(filename):
    """Load a model into Myokit from MMT file format.

    Saves the default state to sabs_pkpd.constants.default_state.

    Parameters
    ----------
    filename : str
        Path to the MMT file

    Returns
    -------
    myokit.Simulation
        Myokit Simulation object from the MMT file
    """
    model, prot, script = myokit.load(filename)
    s = myokit.Simulation(model, prot)
    sabs_pkpd.constants.default_state = s.state()

    return s
