# -*- coding: utf-8 -*-

"""The graphical part of a Crystal Builder step"""

import seamm
from seamm_util import ureg, Q_, units_class  # noqa: F401
import seamm_widgets as sw
import crystal_builder_step  # noqa: F401
import Pmw
import pprint  # noqa: F401
import tkinter as tk
import tkinter.ttk as ttk


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

        self.dialog = Pmw.Dialog(
            self.toplevel,
            buttons=('OK', 'Help', 'Cancel'),
            defaultbutton='OK',
            master=self.toplevel,
            title='Edit Crystal Builder step',
            command=self.handle_dialog
        )
        self.dialog.withdraw()

        # The information about widgets is held in self['xxxx'], i.e. this
        # class is in part a dictionary of widgets. This makes accessing
        # the widgets easier and allows loops, etc.

        # Create a frame to hold everything. This is always called 'frame'.
        self['frame'] = ttk.Frame(self.dialog.interior())
        self['frame'].pack(expand=tk.YES, fill=tk.BOTH)
        # Shortcut for parameters
        P = self.node.parameters

        # The create the widgets
        for key in P:
            self[key] = P[key].widget(self['frame'])

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

        # Remove any widgets previously packed
        frame = self['frame']
        for slave in frame.grid_slaves():
            slave.grid_forget()

        # Shortcut for parameters
        P = self.node.parameters

        # keep track of the row in a variable, so that the layout is flexible
        # if e.g. rows are skipped to control such as 'method' here
        row = 0
        widgets = []
        for key in P:
            self[key].grid(row=row, column=0, sticky=tk.EW)
            widgets.append(self[key])
            row += 1

        # Align the labels
        sw.align_labels(widgets)

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
            P[key].set_from_widget()

    def handle_help(self):
        """Shows the help to the user when click on help button.

        """
        print('Help not implemented yet for Crystal Builder!')
