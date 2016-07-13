"""
Copyright 2007, 2008, 2009 Free Software Foundation, Inc.
This file is part of GNU Radio

GNU Radio Companion is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

GNU Radio Companion is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

from __future__ import absolute_import
import math

from gi.repository import Gtk, PangoCairo, Pango

from . import Actions, Colors, Utils, Constants
from .Element import Element

from ..core.Element import property_nop_write
from ..core.Port import Port as _Port


class Port(_Port, Element):
    """The graphical port."""

    def __init__(self, block, n, dir):
        """
        Port constructor.
        Create list of connector coordinates.
        """
        _Port.__init__(self, block, n, dir)
        Element.__init__(self)
        self._connector_coordinate = (0, 0)
        self._hovering = True
        self._force_label_unhidden = False
        self._bg_color = (0, 0, 0)
        self._line_width_factor = 1.0

        self._width = self.height = 0
        self.connector_length = 0

        self.label_layout = Gtk.DrawingArea().create_pango_layout('')
        self.label_layout.set_alignment(Pango.Alignment.CENTER)

    @property
    def width(self):
        return self._width if not self._label_hidden() else Constants.PORT_LABEL_HIDDEN_WIDTH

    @width.setter
    def width(self, value):
        self._width = value
        self.label_layout.set_width(value * Pango.SCALE)

    def _get_color(self):
        """
        Get the color that represents this port's type.
        Codes differ for ports where the vec length is 1 or greater than 1.

        Returns:
            a hex color code.
        """
        color = Colors.PORT_TYPE_TO_COLOR[self.get_type()]
        vlen = self.get_vlen()
        if vlen > 1:
            dark = (0, 0, 30 / 255.0, 50 / 255.0, 70 / 255.0)[min(4, vlen)]
            color = tuple(max(c - dark, 0) for c in color)
        return color

    def create_shapes(self):
        """Create new areas and labels for the port."""
        self.clear()

        if self.is_horizontal():
            self.areas.append([0, 0, self.width, self.height])
        elif self.is_vertical():
            self.areas.append([0, 0, self.height, self.width])

        self._connector_coordinate = {
            0:   (self.width, self.height / 2),
            90:  (self.height / 2, 0),
            180: (0, self.height / 2),
            270: (self.height / 2, self.width)
        }[self.get_connector_direction()]

    def create_labels(self):
        """Create the labels for the socket."""

        if self.domain in (Constants.GR_MESSAGE_DOMAIN, Constants.DEFAULT_DOMAIN):
            self._line_width_factor = 1.0
        else:
            self._line_width_factor = 2.0

        self._bg_color = self._get_color()

        layout = self.label_layout
        layout.set_markup("""<span foreground="black" font_desc="{font}">{name}</span>""".format(
            name=Utils.encode(self.get_name()), font=Constants.PORT_FONT
        ))
        label_width, label_height = self.label_layout.get_pixel_size()

        self.width = 2 * Constants.PORT_LABEL_PADDING + label_width
        self.height = 2 * Constants.PORT_LABEL_PADDING + label_height
        if self.get_type() == 'bus':
            self.height += 2 * label_height
        self.height += self.height % 2  # uneven height

    def draw(self, widget, cr, border_color, bg_color):
        """
        Draw the socket with a label.
        """
        cr.set_line_width(self._line_width_factor * cr.get_line_width())
        Element.draw(self, widget, cr, border_color, self._bg_color)

        if self._label_hidden():
            return  # this port is folded (no label)

        if self.is_vertical():
            cr.rotate(-math.pi / 2)
            cr.translate(-self.width, 0)
        cr.translate(0, Constants.PORT_LABEL_PADDING)

        PangoCairo.update_layout(cr, self.label_layout)
        PangoCairo.show_layout(cr, self.label_layout)

    def get_connector_coordinate(self):
        """
        Get the coordinate where connections may attach to.

        Returns:
            the connector coordinate (x, y) tuple
        """
        return [sum(c) for c in zip(self._connector_coordinate, self.get_coordinate(),
                                    self.parent_block.get_coordinate())]

    def get_connector_direction(self):
        """
        Get the direction that the socket points: 0,90,180,270.
        This is the rotation degree if the socket is an output or
        the rotation degree + 180 if the socket is an input.

        Returns:
            the direction in degrees
        """
        if self.is_source:
            return self.rotation
        elif self.is_sink:
            return (self.rotation + 180) % 360

    @property_nop_write
    def rotation(self):
        return self.parent_block.rotation

    def rotate(self, direction):
        """
        Rotate the parent rather than self.

        Args:
            direction: degrees to rotate
        """
        self.parent.rotate(direction)

    def move(self, delta_coor):
        """
        Move the parent rather than self.

        Args:
            delta_corr: the (delta_x, delta_y) tuple
        """
        self.parent.move(delta_coor)

    @property
    def highlighted(self):
        return self.parent_block.highlighted

    @highlighted.setter
    def highlighted(self, value):
        self.parent_block.highlighted = value

    def _label_hidden(self):
        """
        Figure out if the label should be hidden

        Returns:
            true if the label should not be shown
        """
        return self._hovering and not self._force_label_unhidden and Actions.TOGGLE_AUTO_HIDE_PORT_LABELS.get_active()

    def force_label_unhidden(self, enable=True):
        """
        Disable showing the label on mouse-over for this port

        Args:
            enable: true to override the mouse-over behaviour
        """
        self._force_label_unhidden = enable

    def mouse_over(self):
        """
        Called from flow graph on mouse-over
        """
        self._hovering = False
        return Actions.TOGGLE_AUTO_HIDE_PORT_LABELS.get_active()  # only redraw if necessary

    def mouse_out(self):
        """
        Called from flow graph on mouse-out
        """
        self._hovering = True
        return Actions.TOGGLE_AUTO_HIDE_PORT_LABELS.get_active()  # only redraw if necessary
