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
from typing import Dict, List

from autor.flow_configuration.activity_block_configuration import ActivityBlockConfiguration
from autor.flow_configuration.activity_configuration import ActivityConfiguration
from autor.framework.autor_framework_exception import AutorFrameworkValueException, AutorFrameworkException
from autor.framework.check import Check
from autor.framework.constants import ActivityGroupType, NodeStatus
from autor.framework.keys import FlowConfigurationKeys as cfg
from autor.framework.node import Node


class ActivityBlockGraph:
    def __init__(self):
        # Counters used for generating unique activity ids
        self._bb_counter = 0
        self._ba_counter = 0
        self._ma_counter = 0
        self._aa_counter = 0
        self._ab_counter = 0

        self._next_main_index = 0

        self._autogen_group_counter = 0
        self._autogen_track_counter = 0

        self._activity_block_id = None
        self._activity_block_config = None

        self._is_first_node = True
        self._is_first_group = True

        self._first_nodes_of_first_group:List[Node] = []
        self._prev_group:str = None

        # Fan-in nodes. These are the nodes that become
        # parents to all nodes that are first in track in a new group.
        self._group_parents:List[Node] = []

        self._tracks_last_node:Dict[str,Node] = {}


        self._ready_to_run:List[Node] = []
        # self._running:List[Node] = []
        # self._finished:List[Node] = []
        # self._blocked:List[Node] = []

        self._nodes:Dict[Node] = {} # All nodes of the graph. Format: {activity_id:Node}

        self._nbr_finished:int = 0

    def has_node(self, activity_id:str)->bool:
        return activity_id in self._nodes

    def get_activity_ids(self)->List[str]:
        return self._nodes.keys()

    def mark_all_nodes_as_interrupted(self):
        for activity_id in self._nodes:
            self._nodes[activity_id].interrupted = True

    def mark_node_and_all_descendants_as_interrupted(self, node:Node):
        self._rec_mark_children_interrupted(node)

    def _rec_mark_children_interrupted(self, node:Node):
        node.interrupted = True
        children:List = node.children
        for child in children:
            self._rec_mark_children_interrupted(child)







    def graph_finished(self)->bool:
        return len(list(self._nodes.values())) == self._nbr_finished

    def get_nodes_that_are_ready_to_run(self)->List[Node]:
        return self._ready_to_run

    def set_status_running(self, activity_id:str):
        node = self._nodes[activity_id]
        Check.true(node.status is NodeStatus.READY_TO_RUN, msg=f"NodeStatus RUNNING can only be assigned to nodes in state READY_TO_RUN. Had status: {node.status}")
        node.status = NodeStatus.RUNNING
        self._ready_to_run.remove(node)

    def set_status_finished(self, activity_id:str):
        node = self._nodes[activity_id]
        Check.true(node.status is NodeStatus.RUNNING, msg="NodeStatus FINISHED can only be assigned to nodes in state RUNNING")
        node.status = NodeStatus.FINISHED
        self._nbr_finished = self._nbr_finished + 1


        for child in node.children:
            # If all the parents of the child node have finished running -> child is ready to run.
            all_parents_finished = True
            for parent in child.parents:
                all_parents_finished = all_parents_finished & (parent.status == NodeStatus.FINISHED)

            if all_parents_finished:
                child.status = NodeStatus.READY_TO_RUN
                if child not in self._ready_to_run:
                    self._ready_to_run.append(child)



    def _add_node(self, node:Node):
        #logging.warning(f"Adding node: {node.activity_id} with rerun: {node.rerun}")
        self._nodes[node.activity_id] = node

        group:str = node.activity_config.concurrency_group
        track:str = node.activity_config.concurrency_track

        if group is None:
            self._autogen_group_counter = self._autogen_group_counter + 1
            group = f"autoGenGroup{self._autogen_group_counter}"

        if track is None:
            self._autogen_track_counter = self._autogen_track_counter + 1
            track = f"autoGenTrack{self._autogen_track_counter}"


        # New group -> fan in previous tracks
        if self._prev_group != group and not self._is_first_node:

            self._is_first_group = False

            # ----------- create new group parents -----------------#
            # The last nodes of each track of the previous group become
            # parent nodes to the current group.
            self._group_parents = []
            for _, last_node in self._tracks_last_node.items():
                self._group_parents.append(last_node)
                
            # ----------- reset track info -------------------------#
            self._tracks_last_node = {}  # Reset to give a clean start for the new group


                # Same group -> continue building tracks
                #else:
        # If the track already exists -> add the node to the end of the track
        if track in self._tracks_last_node:
            #logging.warning(f"222 Adding node: {node.activity_id} with rerun: {node.rerun}")
            prev_node:Node = self._tracks_last_node[track]
            prev_node.add_child(node)
            node.add_parent(prev_node)
            self._tracks_last_node[track] = node # node becomes the last node

            # Nodes can inherit the need to re-run from their parents.
            # But the parent cannot remove the child's need to rerun.
            if prev_node.rerun:
                if node.rerun:
                    logging.warning(f"(*)Activity: {node.activity_id} explicitly requested to re-run, "
                                    f"while the re-run of this activity is already activated by "
                                    f"one of the previous activities.")
                node.rerun = True



        # New track. Group parents become the node parents.
        else:
            #logging.warning(f"333 Adding node: {node.activity_id} with rerun: {node.rerun}")
            at_lest_one_parent_reruns = False
            for parent in self._group_parents:
                #logging.warning(f"1 node: {node.activity_id} rerun: {node.rerun}, parent: {parent.activity_id} rerun: {parent.rerun}")
                parent.add_child(node)
                #logging.warning(f"2 node: {node.activity_id} rerun: {node.rerun}, parent: {parent.activity_id} rerun: {parent.rerun}")
                node.add_parent(parent)
                #logging.warning(f"3 node: {node.activity_id} rerun: {node.rerun}, parent: {parent.activity_id} rerun: {parent.rerun}")

                # Nodes can inherit the need to re-run from their parents.
                # But the parent cannot remove the child's need to rerun.
                if parent.rerun:
                    at_lest_one_parent_reruns = True
                    if node.rerun:
                        #logging.warning(f"3332 Adding node: {node.activity_id} with rerun: {node.rerun}, parent {parent.activity_id} with rerun: {parent.rerun}")

                        logging.warning(f"(**)Activity: {node.activity_id} explicitly requested to re-run, "
                                        f"while the re-run of this activity is already activated by "
                                        f"one of the previous activities.")

            if not node.rerun:
                node.rerun = at_lest_one_parent_reruns

            self._tracks_last_node[track] = node
            if self._is_first_group:
                self._first_nodes_of_first_group.append(node)
                node.status = NodeStatus.READY_TO_RUN
                self._ready_to_run.append(node)


        self._is_first_node = False
        self._prev_group = group

        

    def _rec_print_children(self, node:Node):
        node.print()
        for child in node.children:
            self._rec_print_children(child)



    def print(self):
        if len(self._first_nodes_of_first_group)==0:
            logging.info("The first node group contains no nodes -> no graph has been created.")
            return

        for node in self._first_nodes_of_first_group:
            self._rec_print_children(node)










    def initiate(self, activity_block_config:ActivityBlockConfiguration,rerun_activity_ids:List=[]):
        self._prepare_config(activity_block_config)

        #logging.warning(f"rerun activity list: {','.join(rerun_activity_ids)}")

        # --------------------- BEFORE-BLOCK ----------------------------#
        for act_conf_before_block in self._activity_block_configs_before_block:
            activity_id = (
                self._activity_block_id
                + "-"
                + self._get_activity_name(act_conf_before_block, ActivityGroupType.BEFORE_BLOCK)
            )
            rerun = activity_id in rerun_activity_ids
            node = Node(
                activity_id,
                ActivityGroupType.BEFORE_BLOCK,
                act_conf_before_block,
                rerun
            )
            self._add_node(node)


        # -----------------------   M A I N - B L O C K   B E G I N   ---------------------------#
        for act_conf_main in self._activity_block_configs_main_activities:
            before_activity_nodes = []
            after_activity_nodes = []

            main_name = self._get_activity_name(act_conf_main, ActivityGroupType.MAIN_ACTIVITY)

            # ----------------------- BEFORE-ACTIVITY --------------------------#
            for act_conf_before in self._activity_block_configs_before_activity:
                activity_id = (
                    self._activity_block_id
                    + "-"
                    + main_name
                    + "-"
                    + self._get_activity_name(act_conf_before, ActivityGroupType.BEFORE_ACTIVITY)
                )
                rerun = activity_id in rerun_activity_ids
                ba_node = Node(
                    activity_id,
                    ActivityGroupType.BEFORE_ACTIVITY,
                    act_conf_before,
                    rerun
                )
                self._add_node(ba_node)
                before_activity_nodes.append(ba_node)

                # activity_group_type = ActivityGroupType.BEFORE_ACTIVITY
                # activity_name = self._get_activity_name(act_conf_before, activity_group_type)
                # activity_id = f"{self._activity_block_id}-{main_name}-{activity_name}"
                # node = Node(activity_id,activity_group_type,act_conf_before)


            # ------------------------ MAIN-ACTIVITY ---------------------------#
            activity_id = self._activity_block_id + "-" + main_name
            rerun = activity_id in rerun_activity_ids
            ma_node = Node(activity_id, ActivityGroupType.MAIN_ACTIVITY, act_conf_main, rerun)
            #logging.warning(f"Adding node: {activity_id} with rerun: {rerun}")
            self._add_node(ma_node)
            self._next_main_index = self._next_main_index + 1

            # ------------------------ AFTER-ACTIVITY ---------------------------#
            for act_conf_after in self._activity_block_configs_after_activity:
                activity_id = (
                    self._activity_block_id
                    + "-"
                    + main_name
                    + "-"
                    + self._get_activity_name(act_conf_after, ActivityGroupType.AFTER_ACTIVITY)
                )
                rerun = activity_id in rerun_activity_ids
                aa_node = Node(
                    activity_id,
                    ActivityGroupType.AFTER_ACTIVITY,
                    act_conf_after,
                    rerun
                )
                self._add_node(aa_node)
                after_activity_nodes.append(aa_node)

            # Add main-activity nodes to before-activity nodes. Needed for rules.
            for ba in before_activity_nodes:
                ba.main_activity_node = ma_node

            ma_node.before_activity_nodes = before_activity_nodes

            for aa in after_activity_nodes:
                aa.main_activity_node = node
                aa.before_activity_nodes = before_activity_nodes
            # Add before-activity nodes to main activities


        # ----------------------------   M A I N - B L O C K   E N D   ----------------------------#

        # ----------------------- AFTER-BLOCK ------------------------------#
        for act_conf_after_block in self._activity_block_configs_after_block:
            activity_id = (
                self._activity_block_id
                + "-"
                + self._get_activity_name(act_conf_after_block, ActivityGroupType.AFTER_BLOCK)
            )
            rerun = activity_id in rerun_activity_ids
            node = Node(
                activity_id,
                ActivityGroupType.AFTER_BLOCK,
                act_conf_after_block,
                rerun
            )
            self._add_node(node)





    def _get_activity_name(self, conf, group):

        # if self._mode == Mode.ACTIVITY:
        #     Check.is_non_empty_string(self._activity_name_special, msg="Internal error. Mode ACTIVITY requires activity_name, which should be created by Autor internal bootstrap extension. In this mode Autor generates a Flow Configuration with the acitivity_name.")
        #     default_name= self._activity_name_special

        if group == ActivityGroupType.BEFORE_BLOCK:
            self._bb_counter = self._bb_counter + 1
            default_name = cfg.BEFORE_BLOCK + str(self._bb_counter)

        elif group == ActivityGroupType.BEFORE_ACTIVITY:
            self._ba_counter = self._ba_counter + 1
            default_name = cfg.BEFORE_ACTIVITY + str(self._ba_counter)

        elif group == ActivityGroupType.MAIN_ACTIVITY:
            self._ma_counter = self._ma_counter + 1
            default_name = cfg.ACTIVITY + str(self._ma_counter)

        elif group == ActivityGroupType.AFTER_ACTIVITY:
            self._aa_counter = self._aa_counter + 1
            default_name = cfg.AFTER_ACTIVITY + str(self._aa_counter)

        elif group == ActivityGroupType.AFTER_BLOCK:
            self._ab_counter = self._ab_counter + 1
            default_name = cfg.AFTER_BLOCK + str(self._ab_counter)
        else:
            raise AutorFrameworkException("Unhandled ActivityGroupType: " + str(group))

        if conf.name is not None:
            return conf.name

        conf.name = default_name

        return default_name

    def _prepare_config(self, activity_block_config:ActivityBlockConfiguration):
        try:
            # pylint: disable=line-too-long
            # fmt: off
            self._activity_block_config = activity_block_config
            self._activity_block_id = activity_block_config.name
            self._activity_block_configs_main_activities = self._activity_block_config.activities
            self._activity_block_configs_before_block    = self._activity_block_config.before_block
            self._activity_block_configs_after_block     = self._activity_block_config.after_block
            self._activity_block_configs_before_activity = self._activity_block_config.before_activity
            self._activity_block_configs_after_activity  = self._activity_block_config.after_activity

            # fmt: on
            # pylint: enable=line-too-long

            if (
                len(self._activity_block_configs_main_activities) == 0
                and len(self._activity_block_configs_before_block) == 0
                and len(self._activity_block_configs_after_block) == 0
                and len(self._activity_block_configs_before_activity) == 0
                and len(self._activity_block_configs_after_activity) == 0
            ):
                raise AutorFrameworkValueException(
                    (
                        "No activity configurations found in the configuration of the activity"
                        + f" block: {str(self._activity_block_id)!r} -> no activities to run"
                    )
                )

        except Exception as e:
            raise AutorFrameworkException(
                f"Could not create activity configurations: {e.__class__.__name__}: {str(e)}"
            ) from e





