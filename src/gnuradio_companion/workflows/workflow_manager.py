import logging
from .workflow import workflow

logger = logging.getLogger(__name__)

class WorkflowManager():
    
    def __init__(self):
        self.workflows = workflow()

    def load_workflow_description(self, data, filepath):
        """parse the .workflow.yml file and add it to the list"""
        print("running load_workflow_description")
        log = logger.getChild('workflow_loader')
        log.debug('loading %s', filepath)

        if data['id'] in self.workflows.workflow_ids:
            log.error('file already parsed')
        else:
            self.workflows.workflow_labels.append(data['label'])
            self.workflows.workflow_ids.append(data['id'])
            self.workflows.docs[data['id']] = data['description']
            self.workflows.flags[data['id']] = data['flags']
            self.workflows.param_list[data['id']] = data['parameters']