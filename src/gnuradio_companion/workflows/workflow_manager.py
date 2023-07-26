import logging
from collections import namedtuple

from . import (
        Messages, Constants,
        blocks, params, ports, errors, utils, schema_checker
)

logger = logging.getLogger(__name__)

class WorkflowManager(Element):

    workflow_labels=[]
    # workflow_parameters = namedtuple('workflow_parameters', ['label', 'id', 'dtype', 'default', 'hide', 'options', 'option_labels'])

    def load_workflow_description(self, data, filepath):
        """parse the .workflow.yml file and add it to the list"""
        log = logger.getChild('workflow_loader')
        log.debug('loading %s', filepath)
        
        label = data['label']

        for l in workflow_labels:
            if l == label:
                log.error('file already parsed')
            else
                self.checkworkflow_path.append(label)

        doc = data['description']
        flags = data['flags']
        params = data['parameters']
        # parameters = []

        # for a in params:
        #     S = workflow_parameters()
        #     S.label = a['label']
        #     S.id = a['id']
        #     S.dtype = a['dtype']
        #     S.default = a['default']
        #     if a['hide']: S.hide = a['hide']
        #     if a['option']: S.option = a['option']
        #     if a['option_labels']: S.option_labels = a['option_labels']
        #     parameters.append(S)