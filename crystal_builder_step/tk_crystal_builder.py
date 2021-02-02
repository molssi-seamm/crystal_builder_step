# -*- coding: utf-8 -*-

"""The graphical part of a Crystal Builder step"""

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
        self,
        tk_flowchart=None,
        node=None,
        canvas=None,
        x=None,
        y=None,
        w=200,
        h=50
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
        self._last_prototype = None

        super().__init__(
            tk_flowchart=tk_flowchart,
            node=node,
            canvas=canvas,
            x=x,
            y=y,
            w=w,
            h=h
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

        frame = super().create_dialog(title='Crystal Builder')

        # Shortcut for parameters
        P = self.node.parameters

        # Create the frames for cell and atom sites
        cell_frame = self['cell_frame'] = ttk.LabelFrame(
            self['frame'],
            borderwidth=4,
            relief='sunken',
            text='Cell',
            labelanchor='n',
            padding=10
        )
        self['site_frame'] = ttk.LabelFrame(
            self['frame'],
            borderwidth=4,
            relief='sunken',
            text='Atom Sites',
            labelanchor='n',
            padding=10
        )

        # The create the widgets
        for key in ('prototype_group', 'n_sites', 'prototype'):
            self[key] = P[key].widget(frame)
        for key in ('a', 'b', 'c', 'alpha', 'beta', 'gamma'):
            self[key] = P[key].widget(cell_frame)

        # And the sites for the current elements
        i = 0
        for symbol in P['elements'].get():
            i += 1
            key = f'site {i}'
            self[key] = sw.LabeledEntry(self['site_frame'], labeltext=key)
            self[key].set(symbol)

        # Setup bindings
        self['prototype_group'].combobox.bind(
            "<<ComboboxSelected>>", self.reset_dialog
        )
        self['prototype_group'].combobox.bind("<Return>", self.reset_dialog)
        self['prototype_group'].combobox.bind("<FocusOut>", self.reset_dialog)

        self['n_sites'].combobox.bind(
            "<<ComboboxSelected>>", self.reset_dialog
        )
        self['n_sites'].combobox.bind("<Return>", self.reset_dialog)
        self['n_sites'].combobox.bind("<FocusOut>", self.reset_dialog)

        self['prototype'].combobox.bind(
            "<<ComboboxSelected>>", self.reset_dialog
        )
        self['prototype'].combobox.bind("<Return>", self.reset_dialog)
        self['prototype'].combobox.bind("<FocusOut>", self.reset_dialog)

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
        if self._in_reset:
            return
        self._in_reset = True

        # Remove any widgets previously packed
        frame = self['frame']
        for slave in frame.grid_slaves():
            slave.grid_forget()
        for slave in self['cell_frame'].grid_slaves():
            slave.grid_forget()
        for slave in self['site_frame'].grid_slaves():
            slave.grid_forget()

        prototype_group = self['prototype_group'].get()
        n_sites = self['n_sites'].get()
        prototype = self['prototype'].get()

        self._tmp = {}
        cb_prototypes = crystal_builder_step.prototypes
        if prototype_group == 'common':
            prototypes = [*crystal_builder_step.common_prototypes]
            self._tmp = {
                p: v for p, v in crystal_builder_step.common_prototypes.items()
            }
            self['prototype'].combobox.config(values=prototypes)
        elif prototype_group == 'Strukturbericht':
            prototypes = []
            for n_proto_sites, struk, proto, description, aflow in zip(
                    cb_prototypes['n_sites'],
                    cb_prototypes['Strukturbericht designation'],
                    cb_prototypes['prototype'],
                    cb_prototypes['notes'],
                    cb_prototypes['AFLOW prototype']
            ):  # yapf: disable
                if struk is not None:
                    if n_sites == 'any' or n_proto_sites == int(n_sites):
                        key = f'{struk}: {proto}: {description}'
                        prototypes.append(key)
                        self._tmp[key] = aflow
        else:
            prototypes = []
            for n_proto_sites, proto, description, aflow in zip(
                    cb_prototypes['n_sites'],
                    cb_prototypes['prototype'],
                    cb_prototypes['notes'],
                    cb_prototypes['AFLOW prototype']
            ):  # yapf: disable
                if n_sites == 'any' or n_proto_sites == int(n_sites):
                    key = f'{proto}: {description}'
                    prototypes.append(key)
                    self._tmp[key] = aflow
        prototypes.sort()
        self['prototype'].combobox.config(values=prototypes)
        if len(prototypes) == 0:
            width = 300
        else:
            width = max(len(x) for x in prototypes) + 5
        self['prototype'].config(width=width)
        if prototype in prototypes:
            self['prototype'].set(prototype)
        else:
            self['prototype'].combobox.current(0)
            prototype = self['prototype'].get()
        self._tmp['AFLOW prototype'] = self._tmp[prototype]

        # keep track of the row in a variable, so that the layout is flexible
        # if e.g. rows are skipped to control such as 'method' here
        row = 0
        widgets = []

        self['prototype_group'].grid(row=row, column=0, sticky=tk.EW)
        widgets.append(self['prototype_group'])
        row += 1

        if prototype_group != 'common':
            self['n_sites'].grid(row=row, column=0, sticky=tk.EW)
            widgets.append(self['n_sites'])
            row += 1

        self['prototype'].grid(row=row, column=0, sticky=tk.EW)
        widgets.append(self['prototype'])
        row += 1

        # Align the labels
        sw.align_labels(widgets)

        # And now the cell parameters
        self['cell_frame'].grid(row=row, column=0, sticky=tk.EW)
        row += 1

        aflow_prototype = self._tmp[prototype]
        cb_data = crystal_builder_step.prototype_data[aflow_prototype]
        cell_data = cb_data['cell']
        site_data = cb_data['sites']

        subrow = 0
        widgets = []
        for parameter, value in cell_data:
            w = self[parameter]
            w.grid(row=subrow, sticky=tk.EW)
            subrow += 1
            if aflow_prototype != self._last_prototype:
                w.set(value)
            widgets.append(w)
        sw.align_labels(widgets)

        # And the sites
        self['site_frame'].grid(row=row, column=0, sticky=tk.EW)
        row += 1

        subrow = 0
        widgets = []
        for site, mult, symbol in site_data:
            i = subrow + 1
            key = f'site {i}'
            if key not in self:
                self[key] = sw.LabeledEntry(self['site_frame'], labeltext=key)
            w = self[key]
            w.grid(row=subrow, sticky=tk.EW)
            subrow += 1
            if aflow_prototype != self._last_prototype:
                w.set(symbol)
            label = f'Site {i} -- {mult}{site}:'
            w.config(labeltext=label)
            widgets.append(w)
        sw.align_labels(widgets)

        # Remember the last prototype
        self._last_prototype = aflow_prototype

        self['frame'].grid_columnconfigure(0, weight=1, minsize=500)

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
            self._last_prototype = P['AFLOW prototype'].value
            self.create_dialog()

        self.dialog.activate(geometry='centerscreenfirst')

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

        if result is None or result == 'Cancel':
            self.dialog.deactivate(result)
            return

        if result == 'Help':
            # display help!!!
            return

        if result != "OK":
            self.dialog.deactivate(result)
            raise RuntimeError(
                "Don't recognize dialog result '{}'".format(result)
            )

        self.dialog.deactivate(result)
        # Shortcut for parameters
        P = self.node.parameters

        # Get the values for all the widgets. This may be overkill, but
        # it is easy! You can sort out what it all means later, or
        # be a bit more selective.
        for key in P:
            if key != 'elements':
                P[key].set_from_widget()

        P['AFLOW prototype'].set(self._tmp['AFLOW prototype'])

        aflow_prototype = self._last_prototype
        cb_data = crystal_builder_step.prototype_data[aflow_prototype]
        site_data = cb_data['sites']
        i = 0
        elements = []
        for site, mult, symbol in site_data:
            i += 1
            key = f'site {i}'
            elements.append(self[key].get())
        P['elements'].set(elements)

        self._tmp = {}

    def handle_help(self):
        """Shows the help to the user when click on help button.

        """
        print('Help not implemented yet for Crystal Builder!')
