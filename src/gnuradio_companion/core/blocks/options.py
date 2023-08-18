# Copyright 2016 Free Software Foundation, Inc.
# This file is part of GNU Radio
#
# SPDX-License-Identifier: GPL-2.0-or-later
#

from . import Block, register_build_in
from ._build import build_params
from ._templates import MakoTemplates
from ._flags import Flags
from ...workflows.workflow_manager import WorkflowManager
from collections import ChainMap

templates = MakoTemplates()

@register_build_in
class Options(Block):
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.workflows = self.parent_platform.workflow_manager.workflows
        self.workflow_labels = self.workflows.workflow_labels
        self.workflow_ids = self.workflows.workflow_ids
        self. workflow_params = ChainMap()
        
        for i in self.workflow_labels:
            params = build_params(self.workflows.param_list[i],
                                  have_inputs=True,
                                  have_outputs=True,
                                  flags=Block.flags,
                                  block_id=self.key)
            
            self.workflow_params = self.workflow_params.new_child({i : params})
        
        #create parameter objects for all parameter data
        #change the parameters based on workflow chosen once init runs.
        # workflow_params = build_params(self.parent_platform.workflow_manager.workflows.param_list[self.key], 
        #                                have_inputs=True, 
        #                                have_outputs=True, 
        #                                flags=Block.flags, 
        #                                block_id=self.key)
        # self.parameters.update(workflow_params)
        # print(self.parameters.maps())
        
        self.parameters_data['workflow']['options'] = self.workflow_ids
        self.parameters_data['workflow']['option_labels'] = self.workflow_labels
        self.documentation = {'': self.workflows.docs[self.key]}
        self.flags = self.workflows.flags[self.key]

    key = 'options'
    label = 'options'

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

                dict(label='Workflow', 
                     id='workflow',
                     dtype='enum', 
                     default='python',
                     options=[], 
                     option_labels=[]),
                ],
            have_inputs=True,
            have_outputs=True,
            flags=Block.flags,
            block_id=key
    )

    def _run_asserts(self, placement):
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

    def hide_bokeh_gui_options_if_not_installed(self):
        try:
            import bokehgui
        except ImportError:
            for param in self.parameters_data:
                if param['id'] == 'generate_options':
                    ind = param['options'].index('bokeh_gui')
                    del param['options'][ind]
                    del param['option_labels'][ind]
