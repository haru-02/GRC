#!/usr/bin/env python
# Copyright 2016 Free Software Foundation, Inc.
# This file is part of GNU Radio
#
# SPDX-License-Identifier: GPL-2.0-or-later
#

import os
import sys


GR_IMPORT_ERROR_MESSAGE = """\
Cannot import gnuradio.

Is the Python path environment variable set correctly?
    All OS: PYTHONPATH

Is the library path environment variable set correctly?
    Linux: LD_LIBRARY_PATH
    Windows: PATH

See https://wiki.gnuradio.org/index.php/ModuleNotFoundError
"""


def import_gnuradio(error_exit):
    try:
        from gnuradio import gr
    except ImportError as err:
        error_exit(err, GR_IMPORT_ERROR_MESSAGE)

    return gr


def load_gtk_bindings(error_exit):
    try:
        import gi
        gi.require_version('Gtk', '3.0')
        gi.require_version('PangoCairo', '1.0')
        gi.require_foreign('cairo', 'Context')

        from gi.repository import Gtk
        success = Gtk.init_check()[0]
        if not success:
            # Don't display a warning dialogue. This seems to be a Gtk bug. If it
            # still can display warning dialogues, it does probably work!
            print(
                "Gtk init_check failed. GRC might not be able to start a GUI.",
                file=sys.stderr)

    except Exception as err:
        error_exit(err, "Failed to initialize GTK. If you are running over ssh, "
                 "did you enable X forwarding and start ssh with -X?")


def check_blocks_path(error_exit):
    if 'GR_DONT_LOAD_PREFS' in os.environ and not os.environ.get('GRC_BLOCKS_PATH', ''):
        error_exit(EnvironmentError("No block definitions available"),
            "Can't find block definitions. Use config.conf or GRC_BLOCKS_PATH.")