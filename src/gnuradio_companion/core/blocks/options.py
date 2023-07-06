# Copyright 2016 Free Software Foundation, Inc.
# This file is part of GNU Radio
#
# SPDX-License-Identifier: GPL-2.0-or-later
#

from . import Block, register_build_in
from ._build import build_params
from ._templates import MakoTemplates
from ._flags import Flags


DOC="""
The options block sets special parameters for the flow graph. Only one option block is allowed per flow graph.

Title, author, and description parameters are for identification purposes.

The window size controls the dimensions of the flow graph editor. The window size (width, height) must be between (300, 300) and (4096, 4096).

The generate options controls the type of code generated. Non-graphical flow graphs should avoid using graphical sinks or graphical variable controls.

In a graphical application, run can be controlled by a variable to start and stop the flowgraph at runtime.

The id of this block determines the name of the generated file and the name of the class. For example, an id of my_block will generate the file my_block.py and class my_block(gr....

The category parameter determines the placement of the block in the block selection window. The category only applies when creating hier blocks. To put hier blocks into the root category, enter / for the category.

The Max Number of Output is the maximum number of output items allowed for any block in the flowgraph; to disable this set the max_nouts equal to 0.Use this to adjust the maximum latency a flowgraph can exhibit.
"""

templates = MakoTemplates()

@register_build_in
class Options(Block):
   
    key = 'options'
    label = 'options'
    flags = ['cpp', 'python']
    documentation = {'': DOC}

    parameters_data = build_params(
            params_raw = [
                
                dict(label='Title',
                     id='title',
                     dtype='string',
                     hide="${ ('none' if title else 'part') }"),

                dict(label='Author',
                     id='author',
                     dtype='string',
                     hide="${ ('none' if author else 'part') }"),
                
                dict(label='Copyright',
                     id='copyright',
                     dtype='string',
                     hide="${ ('none' if copyright else 'part') }"),
                
                dict(label='Description', 
                     id='description',
                     dtype='string',
                     hide="${ ('none' if description else 'part') }"),
                
                dict(label='Output Language', 
                     id='output_language', 
                     dtype='enum', 
                     default='python', 
                     options=['python', 'cpp'], 
                     option_labels=['Python', 'C++']),

                dict(label='Generate Options',
                     id='generate_options',
                     dtype='enum', default='qt_gui',
                     option=['qt_gui, bokeh_gui, no_gui, hb, hb_qt_gui'],
                     option_labels=['QT GUI, Bokeh GUI, No GUI, Heir Block, Heir Block (QT GUI)']),

                dict(label='Linking',
                     id='gen_linking',
                     dtype='enum',
                     default='dynamic',
                     options=['dynamic', 'static'],
                     options_labels=['Dynamic', 'Static'],
                     hide='all'),

                dict(label='Generate CmakeLists.txt',
                     id='gen_cmake',
                     dtype='enum',
                     default='On',
                     options=['On', 'Off'],
                     hide="${ ('part' if output_language == 'cpp' else 'all') }"),

                dict(label='CMake options',
                     id='cmake_opt',
                     dtype='string',
                     default='',
                     hide="${ ('part' if output_language == 'cpp' else 'all') }"),

                dict(label='Category',
                     id='category',
                     dtype='string',
                     default='[GRC Hier Blocks]',
                     hide="${ ('none' if generate_options.startswith('hb') else 'all') }"),

                dict(label='Run Options',
                     id='run_options',
                     dtype='enum',
                     default='prompt',
                     options=['run', 'prompt'],
                     option_labels=['Run to Completion', 'Prompt for Exit'],
                     hide="${ ('none' if generate_options == 'no_gui' else 'all') }"),
                
                dict(label='Widget Placement',
                     id='placement',
                     dtype='int_vector',
                     default=[0,0],
                     hide="${ ('part' if generate_options == 'bokeh_gui' else 'all') }"),

                dict(label='Window size',
                     id='window_size',
                     dtype='int_vector',
                     default=[1000,1000],
                     hide="${ ('part' if generate_options == 'bokeh_gui' else 'all') }"),

                dict(label='Sizing Mode',
                     id='sizing_mode',
                     dtype='enum',
                     default='fixed',
                     options=['fixed', 'stretch_both', 'scale_width', 'scale_height', 'scale_both'],
                     option_labels=['Fixed','Stretch Both','Scale Width','Scale Height', 'Scale Both'],
                     hide="${ ('part' if generate_options == 'bokeh_gui' else 'all') }"),

                dict(label='Run',
                     id='run',
                     dtype='bool',
                     default='True',
                     options=['True', 'False'],
                     option_labels=['Autostart', 'Off'],
                     hide="${ ('all' if generate_options not in ('qt_gui', 'bokeh_gui') else ('part' if run else 'none')) }"),

                dict(label='Max Number of Output',
                     id='max_nouts',
                     dtype='int',
                     default='0',
                     hide="${ ('all' if generate_options.startswith('hb') else ('none' if max_nouts else 'part')) }"),

                dict(label='Realtime Scheduling',
                     id='realtime_scheduling',
                     dtype='enum',
                     options=['', '1'],
                     option_labels=['Off', 'On'],
                     hide="${ ('all' if generate_options.startswith('hb') else ('none' if realtime_scheduling else 'part')) }"),

                dict(label='QSS Theme',
                     id='qt_qss_theme',
                     dtype='file_open',
                     hide="${ ('all' if generate_options != 'qt_gui' else ('none' if qt_qss_theme else 'part')) }"),

                dict(label='Thread-safe setters',
                     id='thread_safe_setters',
                     category='Advanced',
                     dtype='enum',
                     options=['','1'],
                     option_labels=['Off', 'On'],
                     hide='part'),

                dict(label='Catch Block Exceptions',
                     id='catch_exceptions',
                     category='Advanced',
                     dtype='enum',
                     options=['False', 'True'],
                     option_labels=['Off', 'On'],
                     default='True',
                     hide='part'),

                dict(label='Run Command',
                     id='run_command',
                     category='Advanced',
                     dtype='string',
                     default='{python} -u {filename}',
                     hide="${ ('all' if generate_options.startswith('hb') else 'part') }"),

                dict(label='Hier Block Source Path',
                     id='hier_block_src_path',
                     category='Advanced',
                     dtype='string',
                     default='.:',
                     hide='part')
                ],
            have_inputs=True,
            have_outputs=True,
            flags=Block.flags,
            block_id=key
    )

    def _run_asserts(placement):
        if not (len(placement) == 4 or len(placement) == 2):
            self.add.error_message="length of window placement must be 4 or 2 !"
        if not (all(i>=0 for i in placement)):
            self.add.error_message="placement cannot be below 0!"
    
        imports=templates.get('imports',"""from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal"""),
    # callbacks='''if ${run}: self.start()

     #   else: self.stop(); self.wait()'''

    cpp_templates = MakoTemplates(includes=['#include <gnuradio/topblock.h>'])

    file_format=1

    def hide_bokeh_gui_options_if_not_installed(self)
        try:
            import bokehgui
        except ImportError:
            for param in self.parameters_data:
                if param['id'] == 'generate_options':
                    ind = param['options'].index('bokeh_gui')
                    del param['options'][ind]
                    del param['option_labels'][ind]
