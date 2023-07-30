import logging
from collections import ChainMap

from . import (
        Messages, Constants,
        blocks, params, ports, errors, utils, schema_checker
)

logger = logging.getLogger(__name__)

class WorkflowManager(Element):

    workflow_labels= []
    workflow_ids = []
    param_list = ChainMap()

    def load_workflow_description(self, data, filepath):
        """parse the .workflow.yml file and add it to the list"""
        log = logger.getChild('workflow_loader')
        log.debug('loading %s', filepath)
        
        label = data['label']
        workflow_id = data['id']

        for l in workflow_labels:
            if l == label:
                log.error('file already parsed')
            else
                self.workflow_labels.append(label)
                self.workflow_ids.append(workflow_id)

        doc = data['description']
        flags = data['flags']
        new_param = {workflow_id: data['parameters']}
        param_list = param_list.new_child(new_param)