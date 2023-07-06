# Copyright 2016 Free Software Foundation, Inc.
# This file is part of GNU Radio
#
# SPDX-License-Identifier: GPL-2.0-or-later
#


from . import epy_block_io, expr_utils, extract_docs, flow_graph_complexity
from ..blocks.options import hide_bokeh_gui_options_if_not_installed


def to_list(value):
    if not value:
        return []
    elif isinstance(value, str):
        return [value]
    else:
        return list(value)
