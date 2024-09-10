#  Copyright 2022-Present Autor contributors
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import logging
import threading
from typing import List

from autor.framework.node_runner_thread import NodeRunnerThread
# from autor.framework.activity_block import ActivityBlock
from autor.framework.graph import ActivityBlockGraph
from autor.framework.node import Node


class ActivityBlockMonitor:
    def __init__(self, activity_block, graph: ActivityBlockGraph):
        self._finished: List[Node] = []
        self._activity_block = activity_block
        self._graph = graph
        self._main_thread_condition = threading.Condition()
        #self._activity_thread_condition = threading.Condition()
        self._nbr_running = 0




    def node_finished(self, node: Node):
        with self._main_thread_condition:
            self._finished.append(node)
            self._main_thread_condition.notify_all()

    def run_nodes(self):
        with self._main_thread_condition:

            # Finalize all nodes that have run.
            for node in self._finished:
                self._graph.set_status_finished(node.activity_id)
                self._nbr_running = self._nbr_running - 1
                self._activity_block._postprocess_node_run(node)
            self._finished = []

            # Run all the nodes that are not blocked.
            nodes_to_run: List[Node] = list(self._graph.get_nodes_that_are_ready_to_run())
            for node in nodes_to_run:

                self._graph.set_status_running(node.activity_id)
                node_runner = NodeRunnerThread()
                node_runner.init(activity_block=self._activity_block, node=node, monitor=self)
                self._activity_block._preprocess_node_run(node)
                #logging.info(f"{threading.current_thread().ident}: Monitor: calling thread start()")
                node_runner.start() # Calls self._activity_block._run_node(node)
                #logging.info(f"{threading.current_thread().ident}: Monitor: after calling thread start()")
                self._nbr_running = self._nbr_running + 1

            if self._nbr_running > 0:
                self._wait_for_a_node_to_finish()

    def _wait_for_a_node_to_finish(self):
        with self._main_thread_condition:
            #logging.info(f"{threading.current_thread().ident}: Monitor: waiting for a node to finish")
            self._main_thread_condition.wait()  # Only 1 thread will be waiting here -> no need for a while loop with a condition check.
            self.run_nodes()
