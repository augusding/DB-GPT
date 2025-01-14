"""DAGManager is a component of AWEL, it is used to manage DAGs.

DAGManager will load DAGs from dag_dirs, and register the trigger nodes
to TriggerManager.
"""
import logging
from typing import Dict, List

from dbgpt.component import BaseComponent, ComponentType, SystemApp

from .base import DAG
from .loader import LocalFileDAGLoader

logger = logging.getLogger(__name__)


class DAGManager(BaseComponent):
    """The component of DAGManager."""

    name = ComponentType.AWEL_DAG_MANAGER

    def __init__(self, system_app: SystemApp, dag_dirs: List[str]):
        """Initialize a DAGManager.

        Args:
            system_app (SystemApp): The system app.
            dag_dirs (List[str]): The directories to load DAGs.
        """
        super().__init__(system_app)
        self.dag_loader = LocalFileDAGLoader(dag_dirs)
        self.system_app = system_app
        self.dag_map: Dict[str, DAG] = {}

    def init_app(self, system_app: SystemApp):
        """Initialize the DAGManager."""
        self.system_app = system_app

    def load_dags(self):
        """Load DAGs from dag_dirs."""
        dags = self.dag_loader.load_dags()
        triggers = []
        for dag in dags:
            dag_id = dag.dag_id
            if dag_id in self.dag_map:
                raise ValueError(f"Load DAG error, DAG ID {dag_id} has already exist")
            self.dag_map[dag_id] = dag
            triggers += dag.trigger_nodes
        from ..trigger.trigger_manager import DefaultTriggerManager

        trigger_manager: DefaultTriggerManager = self.system_app.get_component(
            ComponentType.AWEL_TRIGGER_MANAGER,
            DefaultTriggerManager,
            default_component=None,
        )
        if trigger_manager:
            for trigger in triggers:
                trigger_manager.register_trigger(trigger)
            trigger_manager.after_register()
        else:
            logger.warn("No trigger manager, not register dag trigger")
