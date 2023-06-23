# Copyright 2016 Free Software Foundation, Inc.
# This file is part of GNU Radio
#
# SPDX-License-Identifier: GPL-2.0-or-later
#

from . import Block, register_build_in
from ._build import build.params

@register_build_in
class Options(Block):
   
    Key = 'options'
    label = 'options'
    flags = ['cpp', 'python']

    parameters.data = build_params(
            params_raw = [
                
                dict(label='Title',
                     id='title',
                     dtype='string',
                     hide=${ ('none' if title else 'part') }),

                dict(label='Author',
                     id='author',
                     dtype='string',
                     hide=${ ('none' if author else 'part') }),
                
                dict(label='Copyright',
                     id='copyright',
                     dtype='string',
                     hide=${ ('none' if copyright else 'part') }),
                
                dict(label='Description', 
                     id='description',
                     dtype='string',
                     hide=${ ('none' if description else 'part') }),
                
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
                     hide=${ ('part' if output_language == 'cpp' else 'all') }),

                dict(label='CMake options',
                     id='cmake_opt',
                     dtype='string',
                     default='',
                     hide=${ ('part' if output_language == 'cpp' else 'all') }),

                dict(label='Category',
                     id='category',
                     dtype='string',
                     default='[GRC Hier Blocks]',
                     hide=${ ('none' if generate_options.startswith('hb') else 'all') }),

                dict(label='Run Options',
                     id='run_options',
                     dtype='enum',
                     default='prompt'
                     options=['run', 'prompt']
                     options),
                
                dict(label='Widget Placement',
                     id='placement',
                     dtype='int_vector',
                     default=[0,0]
                     hide=${ ('part' if generate_options == 'bokeh_gui' else 'all') }),

                dict(label='Window size',
                     id='window_size',
                     dtype='int_vector',
                     default=[1000,1000],
                     hide=${ ('part' if generate_options == 'bokeh_gui' else 'all') }),

                dict(label='Sizing Mode',
                     id='sizing_mode',
                     dtype='enum',
                     default='fixed',
                     options=['fixed', 'stretch_both', 'scale_width', 'scale_height', 'scale_both'],
                     option_labels=['Fixed','Stretch Both','Scale Width','Scale Height', 'Scale Both'],
                     hide=${ ('part' if generate_options == 'bokeh_gui' else 'all') }),

                dict(label='Run',
                     id='run',
                     dtype='bool',
                     default='True',
                     options=['True', 'False'],
                     option_labels=['Autostart', 'Off'],
                     hide=${ ('all' if generate_options not in ('qt_gui', 'bokeh_gui') else ('part' if run else 'none')) }),

                dict(label='Max Number of Output',
                     id='max_nouts',
                     dtype='int',
                     default='0',
                     hide=${ ('all' if generate_options.startswith('hb') else ('none' if max_nouts else 'part')) }),

                dict(label='Realtime Scheduling',
                     id='realtime_scheduling',
                     dtype='enum',
                     options=['', '1'],
                     option_labels=['Off', 'On'],
                     hide=${ ('all' if generate_options.startswith('hb') else ('none' if realtime_scheduling else 'part')) }),

                dict(label='QSS Theme',
                     id='qt_qss_theme',
                     dtype='file_open',
                     hide=${ ('all' if generate_options != 'qt_gui' else ('none' if qt_qss_theme else 'part')) }),

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
                     hide=${ ('all' if generate_options.startswith('hb') else 'part') }),

                dict(label='Hier Block Source Path',
                     id='hier_block_src_path',
                     category='Advanced',
                     dtype='string',
                     default='.:',
                     hide='part')
                ],
    )

    def _run_asserts(self.parameters.data.placement):
        if not (len(placement) == 4 or len(placement) == 2):
            self.add.error_message="length of window placement must be 4 or 2 !"
        if not (all(i>=0 for i in placement))
            self.add.error_message="placement cannot be below 0!"
    
    cpp_templates=()
    file_format=1

    
