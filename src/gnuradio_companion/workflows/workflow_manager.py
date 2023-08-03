import logging
from collections import ChainMap

logger = logging.getLogger(__name__)

class WorkflowManager():

    workflow_labels= []
    workflow_ids = []
    param_list = ChainMap()
    doc = ""
    flags = []

    def load_workflow_description(self, data, filepath):
        """parse the .workflow.yml file and add it to the list"""
        log = logger.getChild('workflow_loader')
        log.debug('loading %s', filepath)
        
        label = data['label']
        workflow_id = data['id']

        for l in self.workflow_labels:
            if l == label:
                log.error('file already parsed')
            else:
                self.workflow_labels.append(label)
                self.workflow_ids.append(workflow_id)

        self.doc = data['description']
        self.flags = data['flags']
        new_param = {workflow_id: data['parameters']}
        self.param_list = self.param_list.new_child(new_param)