import logging
from threading import Thread

from autor.framework.constants import ExceptionType
from autor.framework.exception_handler import ExceptionHandler
from autor.framework.node import Node


class NodeRunnerThread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._activity_block = None
        self._node: Node = None
        self._monitor = None

    def init(self, activity_block, node: Node, monitor):
        self._activity_block = activity_block
        self._node = node
        self._monitor = monitor

    def run(self):
        try:
            self._activity_block._run_node(self._node)
        except Exception as ex:
            descr = f"Node runner thread caught an exception: {str(ex)}"
            ExceptionHandler.register_exception(ex=ex, description=descr, ex_type=ExceptionType.INTERNAL)
            self._activity_block.abort_autor(descr)
        finally:
            self._monitor.node_finished(self._node)
