# -*- coding: utf-8 -*-

"""Non-graphical part of the Crystal Builder step in a SEAMM flowchart
"""

try:
    import importlib.metadata as implib
except Exception:
    import importlib_metadata as implib
import json

prototype_data = {}
spacegroups = []

common_prototypes = {
    "simple cubic (SC)": "A_cP1_221_a",
    "body-centered cubic (BCC)": "A_cI2_229_a",
    "face-centered cubic (FCC)": "A_cF4_225_a",
    "diamond": "A_cF8_227_a",
    "zincblende (ZnS)": "AB_cF8_216_c_a",
    "wurtzite (ZnS)": "AB_hP4_186_b_b",
}


def read_prototypes():
    """Read data for the AFLOW prototypes"""
    global prototype_data
    global spacegroups

    # Read in the prototype metadata
    package = "crystal-builder-step"
    files = [p for p in implib.files(package) if "prototypes.json" in str(p)]
    if len(files) > 0:
        path = files[0]
        data = path.read_text()
        prototype_data = json.loads(data)
    else:
        raise IOError("Prototypes JSON file not found!")

    # get a list of the spacegroups, in order
    tmp = {}
    for _, data in prototype_data.items():
        spno = int(data["spacegroup_number"])
        spgrp = data["simple_spacegroup"]
        if spno in tmp:
            if spgrp != tmp[spno]:
                raise RuntimeError(
                    f"Duplicate spacegroups for {spno}: {spgrp}, {tmp[spno]}"
                )
        else:
            tmp[spno] = spgrp
    for spno in sorted(tmp.keys()):
        spacegroups.append(tmp[spno])


read_prototypes()
