====================
Crystal Builder Step
====================

.. image:: https://img.shields.io/github/issues-pr-raw/molssi-seamm/crystal_builder_step
   :target: https://github.com/molssi-seamm/crystal_builder_step/pulls
   :alt: GitHub pull requests

.. image:: https://github.com/molssi-seamm/crystal_builder_step/workflows/CI/badge.svg
   :target: https://github.com/molssi-seamm/crystal_builder_step/actions
   :alt: Build Status

.. image:: https://codecov.io/gh/molssi-seamm/crystal_builder_step/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/molssi-seamm/crystal_builder_step
   :alt: Code Coverage

.. image:: https://img.shields.io/lgtm/grade/python/g/molssi-seamm/crystal_builder_step.svg?logo=lgtm&logoWidth=18
   :target: https://lgtm.com/projects/g/molssi-seamm/crystal_builder_step/context:python
   :alt: Code Quality

.. image:: https://github.com/molssi-seamm/crystal_builder_step/workflows/Documentation/badge.svg
   :target: https://molssi-seamm.github.io/crystal_builder_step/index.html
   :alt: Documentation Status

.. image:: https://pyup.io/repos/github/molssi-seamm/crystal_builder_step/shield.svg
   :target: https://pyup.io/repos/github/molssi-seamm/crystal_builder_step/
   :alt: Updates for Dependencies

.. image:: https://img.shields.io/pypi/v/crystal_builder_step.svg
   :target: https://pypi.python.org/pypi/crystal_builder_step
   :alt: PyPi VERSION

Description
-----------

A SEAMM plug-in for building crystals from prototypes. This plug-in
provides an interface to the `AFLOW Encyclopedia of Crystallographic
Prototypes`_. Users can specify the prototype, elements to place in
the positions, as well as the lattice parameter, creating a crystal
for subsequent editing and building steps and for simulations using
the range of codes supported by SEAMM.

* Free software: BSD-3-Clause
* Documentation: https://molssi-seamm.github.io/crystal_builder_step/index.html

.. _AFLOW Encyclopedia of Crystallographic Prototypes: http://www.aflowlib.org/prototype-encyclopedia/

Features
--------

* 590 crystal prototypes.
* Selection by common prototypes, such as FCC, BCC, and Diamond
* Selection by Strukturbericht designation.
* Searching by number of atomice sites in the prototype.
* Specification of elements for each site in a prototype.
* Specification of cell parameters to override the defaults.

Credits
---------

This package was created with Cookiecutter_ and the `molssi-seamm/cookiecutter-seamm-plugin`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`molssi-seamm/cookiecutter-seamm-plugin`: https://github.com/molssi-seamm/cookiecutter-seamm-plugin

Developed by the Molecular Sciences Software Institute (MolSSI_),
which receives funding from the `National Science Foundation`_ under
award ACI-1547580

.. _MolSSI: https://www.molssi.org
.. _`National Science Foundation`: https://www.nsf.gov

