#!/usr/bin/env python3

"""Process the prototype data from the AFLOW library.

Steps:

1) Manually get the tabular data from the index page
   http://aflowlib.org/prototype-encyclopedia/prototype_index.html

   I did this by opening in Safari, using the Developer module to show the sources,
   open the scripts in th left panel, and downloading table_sort.min.js

   In an editor, I copied the array u from the text 'u=[...],v=[]' by search from the
   bracket in 'u=[' to 'v=[]' and then backup up to closing bracket of the u-array.

   I used black to format it so that I could see the data more nicely. This file is
   'index.json'

   I also had to enclose `Prototype` and `Notes` to make correct JSON. And there are
   a couple places where quoted strings have ", so are quoted with '. I flipped the
   quotes to make "good" json.

   I manually patched the 4 special case in the index.json file::

       "A_hR1_166_a Hg": "A_hR1_166_a.alpha-Hg",
       "A_hR1_166_a Po": "A_hR1_166_a.beta-Po",
       "AB_mP32_14_4e_4e AsS": "AB_mP32_14_4e_4e.realgar",
       "AB_mP32_14_4e_4e AsS": "AB_mP32_14_4e_4e.pararealgar",
       "AB_cP2_221_a_b H4NNO3": "AB_cP2_221_a_b.NH4.NO3",

2) The `download` function then downloads any CIF files to the CIF/ subdirectory. It
   only downloads missing files. The url is like this

   http://aflowlib.org/prototype-encyclopedia/CIF/<AFLOW prototype>.cif
"""

import json
from pathlib import Path
import re
import requests

import CifFile

GreekLetters = {
    r"\\alpha": "\N{Greek Small Letter Alpha}",
    r"\\beta": "\N{Greek Small Letter Beta}",
    r"\\gamma": "\N{Greek Small Letter Gamma}",
    r"\\delta": "\N{Greek Small Letter Delta}",
    r"\\epsilon": "\N{Greek Small Letter Epsilon}",
    r"\\zeta": "\N{Greek Small Letter Zeta}",
    r"\\eta": "\N{Greek Small Letter Eta}",
    r"\\theta": "\N{Greek Small Letter Theta}",
    r"\\iota": "\N{Greek Small Letter Iota}",
    r"\\kappa": "\N{Greek Small Letter Kappa}",
    r"\\lamda": "\N{Greek Small Letter Lamda}",
    r"\\mu": "\N{Greek Small Letter Mu}",
    r"\\nu": "\N{Greek Small Letter Nu}",
    r"\\xi": "\N{Greek Small Letter Xi}",
    r"\\omicron": "\N{Greek Small Letter Omicron}",
    r"\\pi": "\N{Greek Small Letter Pi}",
    r"\\rho": "\N{Greek Small Letter Rho}",
    r"\\sigma": "\N{Greek Small Letter Sigma}",
    r"\\tau": "\N{Greek Small Letter Tau}",
    r"\\upsilon": "\N{Greek Small Letter Upsilon}",
    r"\\phi": "\N{Greek Small Letter Phi}",
    r"\\chi": "\N{Greek Small Letter Chi}",
    r"\\psi": "\N{Greek Small Letter Psi}",
    r"\\omega": "\N{Greek Small Letter Omega}",
    r"\\Alpha": "\N{Greek Capital Letter Alpha}",
    r"\\Beta": "\N{Greek Capital Letter Beta}",
    r"\\Gamma": "\N{Greek Capital Letter Gamma}",
    r"\\Delta": "\N{Greek Capital Letter Delta}",
    r"\\Epsilon": "\N{Greek Capital Letter Epsilon}",
    r"\\Zeta": "\N{Greek Capital Letter Zeta}",
    r"\\Eta": "\N{Greek Capital Letter Eta}",
    r"\\Theta": "\N{Greek Capital Letter Theta}",
    r"\\Iota": "\N{Greek Capital Letter Iota}",
    r"\\Kappa": "\N{Greek Capital Letter Kappa}",
    r"\\Lamda": "\N{Greek Capital Letter Lamda}",
    r"\\Mu": "\N{Greek Capital Letter Mu}",
    r"\\Nu": "\N{Greek Capital Letter Nu}",
    r"\\Xi": "\N{Greek Capital Letter Xi}",
    r"\\Omicron": "\N{Greek Capital Letter Omicron}",
    r"\\Pi": "\N{Greek Capital Letter Pi}",
    r"\\Rho": "\N{Greek Capital Letter Rho}",
    r"\\Sigma": "\N{Greek Capital Letter Sigma}",
    r"\\Tau": "\N{Greek Capital Letter Tau}",
    r"\\Upsilon": "\N{Greek Capital Letter Upsilon}",
    r"\\Phi": "\N{Greek Capital Letter Phi}",
    r"\\Chi": "\N{Greek Capital Letter Chi}",
    r"\\Psi": "\N{Greek Capital Letter Psi}",
    r"\\Omega": "\N{Greek Capital Letter Omega}",
}

subscripts = {
    "0": "\N{Subscript Zero}",
    "1": "\N{Subscript One}",
    "2": "\N{Subscript Two}",
    "3": "\N{Subscript Three}",
    "4": "\N{Subscript Four}",
    "5": "\N{Subscript Five}",
    "6": "\N{Subscript Six}",
    "7": "\N{Subscript Seven}",
    "8": "\N{Subscript Eight}",
    "9": "\N{Subscript Nine}",
    "+": "\N{Subscript Plus Sign}",
    "-": "\N{Subscript Minus}",
    "=": "\N{Subscript Equals Sign}",
    "(": "\N{Subscript Left Parenthesis}",
    ")": "\N{Subscript Right Parenthesis}",
    "a": "\N{Latin Subscript Small Letter A}",
    "e": "\N{Latin Subscript Small Letter E}",
    "o": "\N{Latin Subscript Small Letter O}",
    "x": "\N{Latin Subscript Small Letter X}",
    "h": "\N{Latin Subscript Small Letter H}",
    "k": "\N{Latin Subscript Small Letter K}",
    "l": "\N{Latin Subscript Small Letter L}",
    "m": "\N{Latin Subscript Small Letter M}",
    "n": "\N{Latin Subscript Small Letter N}",
    "p": "\N{Latin Subscript Small Letter P}",
    "s": "\N{Latin Subscript Small Letter S}",
    "t": "\N{Latin Subscript Small Letter T}",
    ".": ".",
}

references = """
@Misc{ crystal_builder_step,
        author = {Paul Saxe},
        title = {Crystal Builder plug-in for SEAMM},
        month = {$month},
        year = {$year},
        organization = {The Molecular Sciences Software Institute (MolSSI)},
        url = {https://github.com/molssi-seamm/crystal_builder_step},
        address = {Virginia Tech, Blacksburg, VA, USA},
        version = {$version}
}

@article{MEHL2017S1,
    title = "The AFLOW Library of Crystallographic Prototypes: Part 1",
    journal = "Computational Materials Science",
    volume = "136",
    pages = "S1 - S828",
    year = "2017",
    issn = "0927-0256",
    doi = "https://doi.org/10.1016/j.commatsci.2017.01.017",
    url = "http://www.sciencedirect.com/science/article/pii/S0927025617300241",
    author = "Michael J. Mehl and David Hicks and Cormac Toher and Ohad Levy and Robert M. Hanson and Gus Hart and Stefano Curtarolo",
    keywords = "Crystal Structure, Space Groups, Wyckoff Positions, Lattice Vectors, Basis Vectors, Database",
}

@article{HICKS2019S1,
    title = "The AFLOW Library of Crystallographic Prototypes: Part 2",
    journal = "Computational Materials Science",
    volume = "161",
    pages = "S1 - S1011",
    year = "2019",
    issn = "0927-0256",
    doi = "https://doi.org/10.1016/j.commatsci.2018.10.043",
    url = "http://www.sciencedirect.com/science/article/pii/S0927025618307146",
    author = "David Hicks and Michael J. Mehl and Eric Gossett and Cormac Toher and Ohad Levy and Robert M. Hanson and Gus Hart and Stefano Curtarolo",
    keywords = "Crystal Structure, Space Groups, Wyckoff Positions, Lattice Vectors, Basis Vectors, Database",
}

@article{HICKS2021110450,
    title = {The AFLOW Library of Crystallographic Prototypes: Part 3},
    journal = {Computational Materials Science},
    volume = {199},
    pages = {110450},
    year = {2021},
    issn = {0927-0256},
    doi = {https://doi.org/10.1016/j.commatsci.2021.110450},
    url = {https://www.sciencedirect.com/science/article/pii/S0927025621001750},
    author = {David Hicks and Michael J. Mehl and Marco Esters and Corey Oses and Ohad Levy and Gus L.W. Hart and Cormac Toher and Stefano Curtarolo},
    keywords = {Crystal Structure, Space Groups, Wyckoff Positions, Lattice Vectors, Basis Vectors, Database},
    abstract = {The AFLOW Library of Crystallographic Prototypes has been extended to include a total of 1,100 common crystal structural prototypes (510 new ones with Part 3), comprising all of the inorganic crystal structures defined in the seven-volume Strukturbericht series published in Germany from 1937 through 1943. We cover a history of the Strukturbericht designation system, the evolution of the system over time, and the first comprehensive index of inorganic Strukturbericht designations ever published.}
}"""  # noqa: E501


def clean_text(text):
    """Replace subscripts and other special characters."""
    text = re.sub(r"&ndash;", "\N{En Dash}", text)
    text = re.sub(r"&frasl;", "\N{Fraction Slash}", text)
    text = re.sub(r"&middot;", "\N{Middle Dot}", text)
    text = re.sub(r"&cacute;", "\N{Latin Small Letter C with Acute}", text)
    text = re.sub(r"&auml;", "\N{Latin Small Letter A with Diaeresis}", text)
    text = re.sub(r"&uuml;", "\N{Latin Small Letter U with Diaeresis}", text)
    text = re.sub(r"&approx;", "\N{Almost Equal To}", text)
    text = re.sub(r"<em>([^<]+)</em>", r"*\1*", text)
    text = re.sub(r"<sub>([^<]+)</sub>", subscript_helper, text)
    text = re.sub(r"<q>([^<]+)</q>", r'"\1"', text)
    text = re.sub(
        r"<sup>II</sup>",
        "\N{Modifier Letter Capital I}\N{Modifier Letter Capital I}",
        text,
    )
    text = text.replace("\u00a0", " ")
    text = math_mode(text)

    return text.strip()


def subscript_helper(match):
    result = ""
    for char in match.group(1):
        if char in subscripts:
            result += subscripts[char]
        else:
            # print(f"There is no unicode subscript for '{char}'")
            result += char
    return result


def entry_to_string(cif, key):
    """Convert a cif entry to a string."""
    if key not in cif:
        return None
    if isinstance(cif[key], str):
        return cif[key].strip()
    lines = []
    for line in cif[key]:
        line = line.strip()
        if line != "":
            lines.append(line)
    return " ".join(lines)


def simple_spacegroup(text):
    """Translate LATeX math mode to Unicode."""
    text = text.strip("$")
    text = re.sub(r"_\{([^}]+)}", r"\1", text)
    text = re.sub(r"\\bar{(.)}", r"-\1", text)
    return text


def math_mode(text):
    """Translate LATeX math mode to Unicode."""
    text = re.sub(r"_\{([^}]+)}", subscript_helper, text)
    text = re.sub(r"\$([^$]+)\$", math_mode_helper, text)
    text = re.sub(r"\\le", "\N{Less-Than or Equal To}", text)
    return text


def math_mode_helper(match):
    text = match.group(1)
    text = re.sub(r"\\bar{(.)}", "\\1\N{Combining Overline}", text)
    for pattern, replacement in GreekLetters.items():
        text = re.sub(pattern, replacement, text)
    return text


def to_bibtex(prototype):
    """Extract the reference information and transform to BibTeX."""

    path = Path("CIF") / (prototype + ".cif")
    with open(path) as fd:
        data = CifFile.ReadCif(fd)

    lines = []
    for _, cif in data.items():
        # pprint.pprint({**cif})

        if "_publ_author_name" not in cif:
            continue

        lines.append("@article{" + prototype)

        tmp = cif["_publ_author_name"]
        if isinstance(tmp, str):
            lines.append("   author = {" + tmp + "}")
        else:
            lines.append("   author = {" + " and ".join(tmp) + "}")

        title = entry_to_string(cif, "_publ_Section_title")
        if title is not None:
            lines.append("   title = {" + title + "}")

        journal = entry_to_string(cif, "_journal_name_full_name")
        if journal is not None:
            lines.append("   journal = {" + journal + "}")

        volume = entry_to_string(cif, "_journal_volume")
        if volume is not None:
            lines.append("   volume = {" + volume + "}")

        page_first = entry_to_string(cif, "_journal_page_first")
        page_last = entry_to_string(cif, "_journal_page_last")

        if page_first is not None:
            if page_last is None:
                lines.append("   pages = {" + page_first + "}")
            else:
                lines.append("   pages = {" + page_first + "--" + page_last + "}")

        year = entry_to_string(cif, "_journal_year")
        if year is not None:
            lines.append("   year = " + year)

        lines.append("}")

    return ",\n".join(lines)


if __name__ == "__main__":  # pragma: no cover

    # Read the array of prototypes.
    with open("index.json", "r") as fd:
        prototypes = json.load(fd)
    print(f"There are {len(prototypes)} prototypes.")
    print("Downloading any CIF files that are missing.")

    # Download the CIF files
    cifdir = Path("CIF")
    cifdir.mkdir(exist_ok=True)

    i = 0
    pset = set()
    for data in prototypes:
        name = data["Prototype"]
        # Ufff. Name may have html <sub> </sub>
        name = name.replace("<sub>", "").replace("</sub>", "")
        prototype = data["AFLOW Prototype"]

        if prototype in pset:
            # print(f"{prototype} is a duplicate")
            pass
        else:
            pset.add(prototype)

        ciffile = cifdir / (prototype + ".cif")
        i += 1
        if not ciffile.exists():
            print(f"   {i:4} Downloading CIF for {prototype} {name}")
            url = f"http://aflowlib.org/prototype-encyclopedia/CIF/{prototype}.cif"
            r = requests.get(url)
            if r.status_code == requests.codes.ok:
                ciffile.write_text(r.text)
            else:
                # It appears that when there are multiple entries, the protoype is
                # appended
                url = (
                    f"http://aflowlib.org/prototype-encyclopedia/CIF/{prototype}.{name}"
                    ".cif"
                )
                r = requests.get(url)
                if r.status_code == requests.codes.ok:
                    ciffile.write_text(r.text)
                else:
                    print(f"      status = {r.status_code}")
            r.close()

    # Process the citations
    path = cifdir / "references.bib"
    print(f"Writing references to {path}.")
    with open(path, "w") as fd:
        fd.write(references)

        pset = set()
        for data in prototypes:
            prototype = data["AFLOW Prototype"]

            if prototype not in pset:
                pset.add(prototype)
                try:
                    text = to_bibtex(prototype)
                except Exception as e:
                    print(f"Error in {prototype}: {str(e)}")
                    continue
                if text is None:
                    print(f"No reference information for {prototype}.")
                else:
                    fd.write(text)
                    fd.write("\n\n")

    # Now create the metadata for the plug-in.
    path = Path("prototypes.json")
    print(f"Writing the metadata to {path}.")

    jdata = {}
    max_sites = 0

    data = {}
    tmp = []
    data["prototype"] = [clean_text(d["Prototype"]) for d in prototypes]
    data["nSpecies"] = [d["# Species"] for d in prototypes]
    data["nAtoms"] = [d["# Atoms"] for d in prototypes]
    data["Pearson symbol"] = [d["Pearson Symbol"] for d in prototypes]
    data["Strukturbericht designation"] = [
        None if d["Struk. Design."] == "None" else clean_text(d["Struk. Design."])
        for d in prototypes
    ]
    data["AFLOW prototype"] = [d["AFLOW Prototype"] for d in prototypes]
    data["space group symbol"] = [
        clean_text(d["Space Group Symbol"]) for d in prototypes
    ]
    data["space group number"] = [d["Space Group Number"] for d in prototypes]
    data["notes"] = [clean_text(d["Notes"]) for d in prototypes]
    data["hyperlink"] = [
        f"http://www.aflowlib.org/CrystalDatabase/{d['AFLOW Prototype']}.html"
        for d in prototypes
    ]

    # Add cell and site info.
    cp = data["cell parameters"] = []
    sites = data["sites"] = []
    pset = set()
    for pdata in prototypes:
        prototype = pdata["AFLOW Prototype"]
        if prototype not in pset:
            pset.add(prototype)

            cif_path = Path("CIF") / (prototype + ".cif")
            with open(cif_path, "r") as fd:
                try:
                    tmp = CifFile.ReadCif(fd)
                except Exception as e:
                    print(f"Problem with {cif_path}, {e}")
                    continue
            if tmp is None:
                print(f"Problem with {cif_path}")
                continue

            for _, cif in tmp.items():
                if "_aflow_params" not in cif:
                    print(f"No aflow parameters in {prototype}.")
                else:
                    params = cif["_aflow_params"].split(",")
                    values = cif["_aflow_params_values"].split(",")

                cell_parameters = []
                adjustable = {
                    "x": {},
                    "y": {},
                    "z": {},
                }
                if "_aflow_params" in cif:
                    for param, value in zip(params, values):
                        if param[0] in ("x", "y", "z"):
                            if param[1:3] == "_{":
                                site_no = int(param[3:-1])
                                adjustable[param[0]][site_no] = value
                            else:
                                site_no = int(param[1:])
                                adjustable[param[0]][site_no] = value
                        elif param[0] == "\\":
                            cell_parameters.append((param[1:], value))
                        elif param == "b/a":
                            cell_parameters.append(("b", cif["_cell_length_b"]))
                        elif param == "c/a":
                            cell_parameters.append(("c", cif["_cell_length_c"]))
                        else:
                            cell_parameters.append((param, value))
                cp.append(cell_parameters)

                site_data = []
                site_no = 0
                for symbol, site, mult, x, y, z in zip(
                    cif["_atom_site_type_symbol"],
                    cif["_atom_site_Wyckoff_label"],
                    cif["_atom_site_symmetry_multiplicity"],
                    cif["_atom_site_fract_x"],
                    cif["_atom_site_fract_y"],
                    cif["_atom_site_fract_z"],
                ):
                    site_no += 1
                    if site_no in adjustable["x"]:
                        x = adjustable["x"][site_no]
                        xvar = True
                    else:
                        xvar = False
                    if site_no in adjustable["y"]:
                        y = adjustable["y"][site_no]
                        yvar = True
                    else:
                        yvar = False
                    if site_no in adjustable["z"]:
                        z = adjustable["z"][site_no]
                        zvar = True
                    else:
                        zvar = False
                    site_data.append(
                        (site, int(mult), symbol, x, xvar, y, yvar, z, zvar)
                    )
                sites.append(site_data)

            n_sites = len(site_data)
            max_sites = max_sites if n_sites < max_sites else n_sites
            description = clean_text(pdata["Notes"])
            if description[-10:] == " Structure":
                description = description[0:-10]
            jdata[prototype] = {
                "prototype": clean_text(pdata["Prototype"]),
                "n_elements": pdata["# Species"],
                "n_atoms": pdata["# Atoms"],
                "pearson_symbol": pdata["Pearson Symbol"],
                "strukturbericht": (
                    None
                    if pdata["Struk. Design."] == "None"
                    else clean_text(pdata["Struk. Design."])
                ),
                "aflow": prototype,
                "simple_spacegroup": simple_spacegroup(pdata["Space Group Symbol"]),
                "spacegroup": clean_text(pdata["Space Group Symbol"]),
                "spacegroup_number": pdata["Space Group Number"],
                "description": description,
                "hyperlink": (
                    f"http://www.aflowlib.org/CrystalDatabase/{prototype}.html"
                ),
                "cell": cell_parameters,
                "sites": site_data,
                "n_sites": n_sites,
            }

    with open(path, "w") as fd:
        json.dump(jdata, fd, indent=4)
