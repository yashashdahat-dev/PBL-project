"""
I-MACSI Mission-Aware Joint Resource Optimizer.

Given a routed path and an intent vector, jointly determines:
1. Bandwidth allocation per link
2. Beam steering activation per node
3. Computational task placement (offload node)
4. Gateway assignment (Earth downlink node)

This is an augmentation layer invoked AFTER Q-routing finds a path.
It applies mission-dependent constraints to the physical network state.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from intent.mission_intent import IntentVector
from network.topology import ConstellationTopology


@dataclass
class ResourceAllocationPlan:
    """Output of the joint optimizer — per-path resource decisions."""
    path: List[str]
    intent: IntentVector

    # Bandwidth allocation: link_key -> allocated_mbps
    bandwidth_allocations: Dict[str, float] = field(default_factory=dict)

    # Beam steering: set of node IDs where beam is activated
    beam_steering_nodes: List[str] = field(default_factory=list)

    # Compute offload: node selected for task placement (lowest load on path)
    compute_offload_node: Optional[str] = None
    compute_offload_load: float = 0.0

    # Gateway: node selected for Earth downlink
    gateway_node: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "intent": self.intent.name,
            "bandwidth_allocations": self.bandwidth_allocations,
            "beam_steering_nodes": self.beam_steering_nodes,
            "compute_offload_node": self.compute_offload_node,
            "compute_offload_load": round(self.compute_offload_load, 4),
            "gateway_node": self.gateway_node,
        }


class GraphOptimizer:
    """
    I-MACSI Joint Resource Optimizer.

    Uses a greedy graph-walk approach over the routed path to make
    mission-aware resource allocation decisions. Each decision is
    constrained by the 8D intent vector weights.
    """

    def __init__(self, topology: ConstellationTopology):
        self.topology = topology

        # Telemetry
        self.bandwidth_allocation_events = 0
        self.beam_steering_events = 0
        self.compute_placement_events = 0
        self.gateway_assignment_events = 0

    def optimize(self, path: List[str], intent: IntentVector) -> ResourceAllocationPlan:
        """
        Given a routed path and intent, jointly optimize all resource dimensions.
        """
        plan = ResourceAllocationPlan(path=path, intent=intent)

        if len(path) < 2:
            return plan

        # ---- 1. Bandwidth Allocation ----
        self._allocate_bandwidth(plan)

        # ---- 2. Beam Steering ----
        self._activate_beam_steering(plan)

        # ---- 3. Computational Task Placement ----
        self._place_compute_task(plan)

        # ---- 4. Gateway Assignment ----
        self._assign_gateway(plan)

        return plan

    def _allocate_bandwidth(self, plan: ResourceAllocationPlan):
        """
        Allocate bandwidth to each link on the path proportional to
        the intent's throughput weight, priority, and available capacity.
        
        Higher throughput weight → more bandwidth reserved.
        Higher priority → larger share of remaining capacity.
        """
        intent = plan.intent
        # Base allocation fraction: how much of available BW to reserve
        # Scale by throughput weight (0-1) and priority (1-10)
        alloc_fraction = 0.1 + intent.w_throughput * 0.6 + (intent.priority / 10) * 0.2

        for i in range(len(plan.path) - 1):
            node_a = plan.path[i]
            node_b = plan.path[i + 1]
            link_key = f"{node_a}->{node_b}"

            node = self.topology.nodes.get(node_a)
            if node is None:
                continue
            link = node.isl_interfaces.get(node_b)
            if link is None:
                continue

            available_bw = link.available_bandwidth
            allocated = available_bw * min(alloc_fraction, 0.9)  # Never allocate >90%
            plan.bandwidth_allocations[link_key] = round(allocated, 2)

            # Apply: increase load on the link
            link.current_load += allocated * 0.01  # Fractional load impact
            self.bandwidth_allocation_events += 1

    def _activate_beam_steering(self, plan: ResourceAllocationPlan):
        """
        Activate beam steering on nodes where the intent demands
        high coverage, high reliability, or the mission is high priority.
        
        Beam steering focuses the antenna pattern toward the next hop,
        improving link budget at the cost of narrower coverage.
        """
        intent = plan.intent
        should_steer = (
            intent.w_coverage > 0.1 or
            intent.w_reliability > 0.2 or
            intent.priority >= 8
        )

        if not should_steer:
            return

        for node_id in plan.path:
            node = self.topology.nodes.get(node_id)
            if node is None:
                continue

            if not node.beam_allocation_active:
                node.beam_allocation_active = True
                plan.beam_steering_nodes.append(node_id)
                self.beam_steering_events += 1

    def _place_compute_task(self, plan: ResourceAllocationPlan):
        """
        For compute-heavy missions, select the node on the path with
        the lowest computational load for edge task offloading.
        
        Only activates when compute weight exceeds threshold.
        """
        intent = plan.intent
        if intent.w_compute < 0.05:
            return

        best_node = None
        best_load = float('inf')

        for node_id in plan.path:
            node = self.topology.nodes.get(node_id)
            if node is None:
                continue
            if node.computational_load < best_load:
                best_load = node.computational_load
                best_node = node_id

        if best_node:
            plan.compute_offload_node = best_node
            plan.compute_offload_load = best_load

            # Apply: increase computational load on selected node
            node = self.topology.nodes.get(best_node)
            if node:
                node.computational_load = min(1.0, node.computational_load + intent.w_compute * 0.15)
            self.compute_placement_events += 1

    def _assign_gateway(self, plan: ResourceAllocationPlan):
        """
        Select the best gateway node on the path for Earth downlink.
        Preference: plane-boundary nodes with lowest computational load.
        
        Gateway assignment is relevant for missions requiring ground
        station connectivity (coverage, broadband, emergency).
        """
        intent = plan.intent
        # Only assign gateway if there's a coverage, throughput, or reliability need
        if intent.w_coverage < 0.05 and intent.w_throughput < 0.1 and intent.w_reliability < 0.1:
            return

        best_gateway = None
        best_score = float('inf')

        for node_id in plan.path:
            node = self.topology.nodes.get(node_id)
            if node is None:
                continue

            is_boundary = self.topology.is_gateway_candidate(node_id)
            # Score: lower is better. Boundary nodes get a large bonus (lower score).
            score = node.computational_load
            if is_boundary:
                score -= 0.5  # Strong preference for boundary nodes

            if score < best_score:
                best_score = score
                best_gateway = node_id

        if best_gateway:
            plan.gateway_node = best_gateway
            gw_node = self.topology.nodes.get(best_gateway)
            if gw_node:
                gw_node.gateway_selections += 1
            self.gateway_assignment_events += 1

    def apply_plan(self, plan: ResourceAllocationPlan):
        """
        Apply the resource allocation plan to the physical network.
        Called by the simulation environment after optimization.
        """
        # Bandwidth allocations are already applied during _allocate_bandwidth
        # Beam steering is already applied during _activate_beam_steering
        # Compute placement is already applied during _place_compute_task
        # Gateway assignment is already applied during _assign_gateway
        pass  # All side-effects are applied inline during optimize()
