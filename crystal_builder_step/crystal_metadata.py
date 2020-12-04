# -*- coding: utf-8 -*-

"""Non-graphical part of the Crystal Builder step in a SEAMM flowchart
"""

try:
    import importlib.metadata as implib
except Exception:
    import importlib_metadata as implib
import json

prototypes = {}
prototype_data = {}

common_prototypes = {
    'simple cubic (SC)': 'A_cP1_221_a',
    'body-centered cubic (BCC)': 'A_cI2_229_a',
    'face-centered cubic (FCC)': 'A_cF4_225_a',
    'diamond': 'A_cF8_227_a',
    'zincblende (ZnS)': 'AB_cF8_216_c_a',
    'wurtzite (ZnS)': 'AB_hP4_186_b_b'
}


def read_prototypes():
    """Read data for the AFLOW prototypes"""
    global prototypes
    global prototype_data

    # Read in the prototype metadata
    package = 'crystal-builder-step'
    files = [p for p in implib.files(package) if 'prototypes.json' in str(p)]
    if len(files) > 0:
        path = files[0]
        data = path.read_text()
        prototypes = json.loads(data)
    else:
        raise IOError('Prototypes JSON file not found!')

    prototypes['n_sites'] = []
    max_sites = 0
    # yapf: disable
    for (
        prototype,
        n_elements,
        n_atoms,
        pearson_symbol,
        strukturbericht,
        aflow,
        spacegroup,
        spacegroup_number,
        description,
        cell,
        sites
    ) in zip(
        prototypes['prototype'],
        prototypes['nSpecies'],
        prototypes['nAtoms'],
        prototypes['Pearson symbol'],
        prototypes['Strukturbericht designation'],
        prototypes['AFLOW prototype'],
        prototypes['space group symbol'],
        prototypes['space group number'],
        prototypes['notes'],
        prototypes['cell parameters'],
        prototypes['sites']
    ):
        prototypes['n_sites'].append(len(sites))
        if len(sites) > max_sites:
            max_sites = len(sites)
        prototype_data[aflow] = {
            'prototype': prototype,
            'n_elements': n_elements,
            'n_atoms': n_atoms,
            'pearson_symbol': pearson_symbol,
            'strukturbericht': strukturbericht,
            'aflow': aflow,
            'spacegroup': spacegroup,
            'spacegroup_number': spacegroup_number,
            'description': description,
            'cell': cell,
            'sites': sites
        }
    # yapf: enable
    prototypes['max_sites'] = max_sites


read_prototypes()
