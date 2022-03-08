# -*- coding: utf-8 -*-

"""
crystal_builder_step
A step for building crystals in SEAMM
"""

# Bring up the classes so that they appear to be directly in
# the crystal_builder_step package.

from crystal_builder_step.crystal_builder import CrystalBuilder  # noqa: F401
from crystal_builder_step.crystal_builder_parameters import (  # noqa: F401
    lattice_systems,
)
from crystal_builder_step.crystal_builder_parameters import (  # noqa: F401
    CrystalBuilderParameters,
)
from crystal_builder_step.crystal_builder_step import (  # noqa: F401
    CrystalBuilderStep,
)
from crystal_builder_step.tk_crystal_builder import TkCrystalBuilder  # noqa: F401, E501

from crystal_builder_step.crystal_metadata import common_prototypes  # noqa: F401, E501
from crystal_builder_step.crystal_metadata import prototype_data  # noqa: F401
from crystal_builder_step.crystal_metadata import spacegroups  # noqa: F401

# Handle versioneer
from ._version import get_versions

__author__ = """Paul Saxe"""
__email__ = "psaxe@molssi.org"
versions = get_versions()
__version__ = versions["version"]
__git_revision__ = versions["full-revisionid"]
del get_versions, versions
