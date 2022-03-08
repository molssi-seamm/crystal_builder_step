# -*- coding: utf-8 -*-

"""The graphical part of a Crystal Builder step"""

import fnmatch
import tkinter as tk
import tkinter.ttk as ttk

import seamm
import seamm_widgets as sw
import crystal_builder_step  # noqa: F401


class TkCrystalBuilder(seamm.TkNode):
    """
    The graphical part of a Crystal Builder step in a flowchart.

    Attributes
    ----------
    namespace : str
        The namespace of the current step.
    node : Node
        The corresponding node of the non-graphical flowchart
    dialog : Dialog
        The Pmw dialog object
    sub_tk_flowchart : TkFlowchart
        A graphical Flowchart representing a subflowchart
    self[widget] : dict
        A dictionary of tk widgets built using the information
        contained in Crystal Builder_parameters.py

    See Also
    --------
    CrystalBuilder, TkCrystalBuilder,
    CrystalBuilderParameters,
    """

    def __init__(
        self, tk_flowchart=None, node=None, canvas=None, x=None, y=None, w=200, h=50
    ):
        """
        Initialize a graphical node.

        Parameters
        ----------
        tk_flowchart: Tk_Flowchart
            The graphical flowchart that we are in.
        node: Node
            The non-graphical node for this step.
        namespace: str
            The stevedore namespace for finding sub-nodes.
        canvas: Canvas
           The Tk canvas to draw on.
        x: float
            The x position of the nodes center on the canvas.
        y: float
            The y position of the nodes cetner on the canvas.
        w: float
            The nodes graphical width, in pixels.
        h: float
            The nodes graphical height, in pixels.
        """
        self.dialog = None
        self._in_reset = False
        self._last_aflow_prototype = None
        self._last_prototype_group = None
        self._last_prototype = None
        self._last_n_sites = None
        self._last_n_elements = None
        self._last_spacegroup = None
        self._last_pearson_symbol = None

        super().__init__(
            tk_flowchart=tk_flowchart, node=node, canvas=canvas, x=x, y=y, w=w, h=h
        )

    def create_dialog(self):
        """
        Create the dialog. A set of widgets will be chosen by default
        based on what is specified in the
        Crystal Builder_parameters module.

        See Also
        --------
        TkCrystalBuilder.reset_dialog
        """

        frame = super().create_dialog(title="Crystal Builder")

        # Shortcut for parameters
        P = self.node.parameters

        # Create the frames for information, cell, and atom sites
        info_frame = self["info_frame"] = ttk.LabelFrame(
            self["frame"],
            borderwidth=4,
            relief="sunken",
            text="Information",
            labelanchor="n",
            padding=10,
        )
        cell_frame = self["cell_frame"] = ttk.LabelFrame(
            self["frame"],
            borderwidth=4,
            relief="sunken",
            text="Cell",
            labelanchor="n",
            padding=10,
        )
        self["site_frame"] = ttk.LabelFrame(
            self["frame"],
            borderwidth=4,
            relief="sunken",
            text="Atom Sites",
            labelanchor="n",
            padding=10,
        )

        # The create the widgets
        for key in (
            "prototype_group",
            "prototype",
            "n_sites",
            "n_elements",
            "spacegroup",
            "pearson_symbol",
        ):
            self[key] = P[key].widget(frame)
            self[key].bind("<<ComboboxSelected>>", self.reset_dialog)
            self[key].bind("<Return>", self.reset_dialog)
            self[key].bind("<FocusOut>", self.reset_dialog)

        for key in ("a", "b", "c", "alpha", "beta", "gamma"):
            self[key] = P[key].widget(cell_frame)

        # Patch up the spacegroups in the pulldown
        spacegroups = ["any"]
        spacegroups.extend(crystal_builder_step.spacegroups)
        self["spacegroup"].configure(values=spacegroups)

        for key in (
            "AFLOW prototype",
            "Prototype",
            "# Elements",
            "# Sites",
            "# Atoms",
            "Pearson symbol",
            "Strukturbericht designation",
            "Space group",
            "Space group number",
            "Description",
        ):
            self["label " + key] = ttk.Label(info_frame, text=key + ":", anchor=tk.E)
            self["value " + key] = ttk.Label(info_frame, text="", anchor=tk.W)

        self["label AFLOW prototype"].grid(row=0, column=0, sticky=tk.E)
        self["value AFLOW prototype"].grid(row=0, column=1, sticky=tk.EW)
        self["label Space group"].grid(row=0, column=3, sticky=tk.E)
        self["value Space group"].grid(row=0, column=4, sticky=tk.EW)
        self["label # Elements"].grid(row=0, column=6, sticky=tk.E)
        self["value # Elements"].grid(row=0, column=7, sticky=tk.EW)

        self["label Prototype"].grid(row=1, column=0, sticky=tk.E)
        self["value Prototype"].grid(row=1, column=1, sticky=tk.EW)
        self["label Space group number"].grid(row=1, column=3, sticky=tk.E)
        self["value Space group number"].grid(row=1, column=4, sticky=tk.EW)
        self["label # Sites"].grid(row=1, column=6, sticky=tk.E)
        self["value # Sites"].grid(row=1, column=7, sticky=tk.EW)

        self["label Strukturbericht designation"].grid(row=2, column=0, sticky=tk.E)
        self["value Strukturbericht designation"].grid(row=2, column=1, sticky=tk.EW)
        self["label Pearson symbol"].grid(row=2, column=3, sticky=tk.E)
        self["value Pearson symbol"].grid(row=2, column=4, sticky=tk.EW)
        self["label # Atoms"].grid(row=2, column=6, sticky=tk.E)
        self["value # Atoms"].grid(row=2, column=7, sticky=tk.EW)

        self["label Description"].grid(row=5, column=0, sticky=tk.E)
        self["value Description"].grid(row=5, column=1, columnspan=7, sticky=tk.EW)

        info_frame.rowconfigure(4, minsize=10)
        info_frame.columnconfigure(2, weight=1, minsize=20)
        info_frame.columnconfigure(5, weight=1, minsize=20)

        # and lay them out
        self.reset_dialog()

    def reset_dialog(self, widget=None):
        """Layout the widgets in the dialog.

        The widgets are chosen by default from the information in
        Crystal Builder_parameter.

        This function simply lays them out row by row with
        aligned labels. You may wish a more complicated layout that
        is controlled by values of some of the control parameters.

        Parameters
        ----------
        widget

        See Also
        --------
        TkCrystalBuilder.create_dialog
        """
        # Not sure if this is needed, but prevents re-entering
        if self._in_reset:
            return

        prototype_group = self["prototype_group"].get()
        prototype = self["prototype"].get()
        n_sites = self["n_sites"].get()
        n_elements = self["n_elements"].get()
        spacegroup = self["spacegroup"].get()
        pearson_symbol = self["pearson_symbol"].get()

        # If nothing has changed, return
        if (
            prototype_group == self._last_prototype_group
            and prototype == self._last_prototype
            and n_sites == self._last_n_sites
            and n_elements == self._last_n_elements
            and spacegroup == self._last_spacegroup
            and pearson_symbol == self._last_pearson_symbol
        ):
            return

        # Filter the prototypes
        try:
            spacegroup_number = int(spacegroup)
        except Exception:
            spacegroup_number = None

        self._tmp = {}
        prototypes = []
        if prototype_group == "common":
            prototypes = [*crystal_builder_step.common_prototypes]
            self._tmp = {
                p: v for p, v in crystal_builder_step.common_prototypes.items()
            }
            self["prototype"].combobox.config(values=prototypes)
        elif prototype_group == "Strukturbericht":
            for aflow, data in crystal_builder_step.prototype_data.items():
                struk = data["strukturbericht"]
                if struk is None:
                    continue
                if n_sites != "any" and data["n_sites"] != int(n_sites):
                    continue
                if n_elements != "any" and data["n_elements"] != int(n_elements):
                    continue
                if pearson_symbol != "any" and not fnmatch.fnmatchcase(
                    data["pearson_symbol"], pearson_symbol
                ):
                    continue
                if spacegroup_number is None:
                    if spacegroup != "any" and not fnmatch.fnmatchcase(
                        data["simple_spacegroup"], spacegroup
                    ):
                        continue
                else:
                    if data["spacegroup_number"] != spacegroup_number:
                        continue
                key = f"{struk}: {data['description']}"
                prototypes.append(key)
                self._tmp[key] = aflow
        elif prototype_group == "prototype":
            for aflow, data in crystal_builder_step.prototype_data.items():
                if n_sites != "any" and data["n_sites"] != int(n_sites):
                    continue
                if n_elements != "any" and data["n_elements"] != int(n_elements):
                    continue
                if pearson_symbol != "any" and not fnmatch.fnmatchcase(
                    data["pearson_symbol"], pearson_symbol
                ):
                    continue
                if spacegroup_number is None:
                    if spacegroup != "any" and not fnmatch.fnmatchcase(
                        data["simple_spacegroup"], spacegroup
                    ):
                        continue
                else:
                    if data["spacegroup_number"] != spacegroup_number:
                        continue
                key = f"{data['prototype']}: {data['description']}"
                prototypes.append(key)
                self._tmp[key] = aflow
        elif prototype_group == "description":
            for aflow, data in crystal_builder_step.prototype_data.items():
                if n_sites != "any" and data["n_sites"] != int(n_sites):
                    continue
                if n_elements != "any" and data["n_elements"] != int(n_elements):
                    continue
                if pearson_symbol != "any" and not fnmatch.fnmatchcase(
                    data["pearson_symbol"], pearson_symbol
                ):
                    continue
                if spacegroup_number is None:
                    if spacegroup != "any" and not fnmatch.fnmatchcase(
                        data["simple_spacegroup"], spacegroup
                    ):
                        continue
                else:
                    if data["spacegroup_number"] != spacegroup_number:
                        continue
                key = f"{data['description']}"
                prototypes.append(key)
                self._tmp[key] = aflow
        else:
            for aflow, data in crystal_builder_step.prototype_data.items():
                if n_sites != "any" and data["n_sites"] != int(n_sites):
                    continue
                if n_elements != "any" and data["n_elements"] != int(n_elements):
                    continue
                if pearson_symbol != "any" and not fnmatch.fnmatchcase(
                    data["pearson_symbol"], pearson_symbol
                ):
                    continue
                if spacegroup_number is None:
                    if spacegroup != "any" and not fnmatch.fnmatchcase(
                        data["simple_spacegroup"], spacegroup
                    ):
                        continue
                else:
                    if data["spacegroup_number"] != spacegroup_number:
                        continue
                key = f"{aflow}: {data['description']}"
                prototypes.append(key)
                self._tmp[key] = aflow

        if len(prototypes) == 0:
            self["prototype_group"].set(self._last_prototype_group)
            self["prototype"].set(self._last_prototype)
            self["n_sites"].set(self._last_n_sites)
            self["n_elements"].set(self._last_n_elements)
            self["spacegroup"].set(self._last_spacegroup)
            self["pearson_symbol"].set(self._last_pearson_symbol)

            tk.messagebox.showwarning(
                title="No matching prototypes!",
                message=(
                    "The criteria you gave for filtering the prototypes were "
                    "to strict. The last change was reversed."
                ),
            )
            return

        # Save the control parameters
        self._last_prototype_group = prototype_group
        self._last_prototype = prototype
        self._last_n_sites = n_sites
        self._last_n_elements = n_elements
        self._last_spacegroup = spacegroup
        self._last_pearson_symbol = pearson_symbol

        self._in_reset = True

        # and proceed
        prototypes.sort()

        # Remove any widgets previously packed
        frame = self["frame"]
        for slave in frame.grid_slaves():
            slave.grid_forget()
        for slave in self["cell_frame"].grid_slaves():
            slave.grid_forget()
        for slave in self["site_frame"].grid_slaves():
            slave.grid_forget()
        self["prototype"].combobox.config(values=prototypes)

        width = 80
        self["prototype"].config(width=width)
        if prototype in prototypes:
            self["prototype"].set(prototype)
        else:
            self["prototype"].combobox.current(0)
            prototype = self["prototype"].get()
        self._tmp["AFLOW prototype"] = self._tmp[prototype]

        # Access the metadata
        aflow_prototype = self._tmp[prototype]
        cb_data = crystal_builder_step.prototype_data[aflow_prototype]

        # keep track of the row in a variable, so that the layout is flexible
        # if e.g. rows are skipped to control such as 'method' here
        row = 0
        widgets = []

        self["prototype_group"].grid(row=row, column=0, sticky=tk.EW)
        widgets.append(self["prototype_group"])
        row += 1

        if prototype_group != "common":
            for key in ("n_sites", "n_elements", "spacegroup", "pearson_symbol"):
                self[key].grid(row=row, column=0, sticky=tk.EW)
                widgets.append(self[key])
                row += 1

        self["prototype"].grid(row=row, column=0, sticky=tk.EW)
        widgets.append(self["prototype"])
        row += 1

        # Align the labels
        sw.align_labels(widgets)

        # The information about the crystal
        self["info_frame"].grid(row=row, column=0, sticky=tk.EW)
        row += 1

        self["value AFLOW prototype"].configure(text=cb_data["aflow"])
        self["value Prototype"].configure(text=cb_data["prototype"])
        self["value # Elements"].configure(text=cb_data["n_elements"])
        self["value # Sites"].configure(text=cb_data["n_sites"])
        self["value # Atoms"].configure(text=cb_data["n_atoms"])
        self["value Pearson symbol"].configure(text=cb_data["pearson_symbol"])
        if cb_data["strukturbericht"] is None:
            text = ""
        else:
            text = cb_data["strukturbericht"]
        self["value Strukturbericht designation"].configure(text=text)
        self["value Space group"].configure(text=cb_data["spacegroup"])
        self["value Space group number"].configure(text=cb_data["spacegroup_number"])
        self["value Description"].configure(text=cb_data["description"])

        # And now the cell parameters
        self["cell_frame"].grid(row=row, column=0, sticky=tk.EW)
        row += 1

        cell_data = cb_data["cell"]
        site_data = cb_data["sites"]

        subrow = 0
        widgets = []
        for parameter, value in cell_data:
            w = self[parameter]
            w.grid(row=subrow, sticky=tk.EW)
            subrow += 1
            if aflow_prototype != self._last_aflow_prototype:
                if parameter in ("a", "b", "c"):
                    w.set(value, "Å")
                else:
                    w.set(value, "degree")
            widgets.append(w)
        sw.align_labels(widgets)

        # And the sites
        sf = self["site_frame"]
        sf.grid(row=row, column=0, sticky=tk.EW)
        row += 1

        subrow = 0
        widgets = []
        for site, mult, symbol, x, xmove, y, ymove, z, zmove in site_data:
            i = subrow + 1
            key = f"site {i}"
            if key not in self:
                self[key] = sw.LabeledEntry(sf, labeltext=key)
                self["x " + key] = ttk.Entry(sf)
                self["y " + key] = ttk.Entry(sf)
                self["z " + key] = ttk.Entry(sf)
            w = self[key]
            w.grid(row=subrow, sticky=tk.EW)
            if aflow_prototype != self._last_aflow_prototype:
                w.set(symbol)
            label = f"Site {i} -- {mult}{site}:"
            w.config(labeltext=label)
            widgets.append(w)

            w = self["x " + key]
            w.configure(state=tk.NORMAL)
            w.delete(0, tk.END)
            w.insert(0, x)
            if not xmove:
                w.configure(state="disabled")
            w.grid(row=subrow, column=1, sticky=tk.EW)

            w = self["y " + key]
            w.configure(state=tk.NORMAL)
            w.delete(0, tk.END)
            w.insert(0, y)
            if not ymove:
                w.configure(state="disabled")
            w.grid(row=subrow, column=2, sticky=tk.EW)

            w = self["z " + key]
            w.configure(state=tk.NORMAL)
            w.delete(0, tk.END)
            w.insert(0, z)
            if not zmove:
                w.configure(state="disabled")
            w.grid(row=subrow, column=3, sticky=tk.EW)

            subrow += 1
        sw.align_labels(widgets)

        # Remember the last prototype
        self._last_aflow_prototype = aflow_prototype

        self["frame"].grid_columnconfigure(0, weight=1, minsize=500)

        # All done resetting, so turn bindings back on.
        self._in_reset = False

    def right_click(self, event):
        """
        Handles the right click event on the node.

        See Also
        --------
        TkCrystalBuilder.edit
        """

        super().right_click(event)
        self.popup_menu.add_command(label="Edit..", command=self.edit)

        self.popup_menu.tk_popup(event.x_root, event.y_root, 0)

    def edit(self):
        """Present a dialog for editing the Crystal Builder input

        See Also
        --------
        TkCrystalBuilder.right_click
        """

        if self.dialog is None:
            P = self.node.parameters
            self._last_aflow_prototype = P["AFLOW prototype"].value
            self.create_dialog()

        self.dialog.activate(geometry="centerscreenfirst")

    def handle_dialog(self, result):
        """Handle the closing of the edit dialog

        What to do depends on the button used to close the dialog. If
        the user closes it by clicking the 'x' of the dialog window,
        None is returned, which we take as equivalent to cancel.

        Parameters
        ----------
        result : None or str
            The value of this variable depends on what the button
            the user clicked.

        """

        if result is None or result == "Cancel":
            self.dialog.deactivate(result)
            return

        if result == "Help":
            # display help!!!
            return

        if result != "OK":
            self.dialog.deactivate(result)
            raise RuntimeError("Don't recognize dialog result '{}'".format(result))

        self.dialog.deactivate(result)
        # Shortcut for parameters
        P = self.node.parameters

        # Get the values for all the widgets. This may be overkill, but
        # it is easy! You can sort out what it all means later, or
        # be a bit more selective.
        for key in P:
            if key != "elements":
                P[key].set_from_widget()

        P["AFLOW prototype"].set(self._tmp["AFLOW prototype"])

        aflow_prototype = self._last_aflow_prototype
        cb_data = crystal_builder_step.prototype_data[aflow_prototype]
        site_data = cb_data["sites"]
        i = 0
        elements = []
        for site, mult, symbol, x, xmove, y, ymove, z, zmove in site_data:
            i += 1
            key = f"site {i}"
            elements.append(self[key].get())

            newx = self["x " + key].get()
            newy = self["y " + key].get()
            newz = self["z " + key].get()

        P["elements"].set(elements)

        self._tmp = {}

    def handle_help(self):
        """Shows the help to the user when click on help button."""
        print("Help not implemented yet for Crystal Builder!")
