import math
import time
from collections import defaultdict


class NetworkMetrics:

    def __init__(self):
        # -----------------------------
        # Communication statistics
        # -----------------------------
        self.total_packets_sent = 0
        self.total_packets_delivered = 0

        self.total_bits_delivered = 0

        self.total_bandwidth_hz = 0
        self.used_bandwidth_hz = 0

        self.packet_delays = []

        # -----------------------------
        # Routing
        # -----------------------------
        self.total_routes = 0
        self.stable_routes = 0

        self.route_changes = 0
        self.successful_recoveries = 0

        # -----------------------------
        # Energy
        # -----------------------------
        self.transmission_energy_j = 0
        self.computation_energy_j = 0
        self.idle_energy_j = 0

        # -----------------------------
        # Computation
        # -----------------------------
        self.computation_operations = 0
        self.computation_time = 0

        # -----------------------------
        # Fairness
        # -----------------------------
        self.flow_throughputs = []

        # -----------------------------
        # Mission metrics
        # -----------------------------
        self.total_missions = 0
        self.completed_missions = 0

        self.mission_satisfaction_scores = []

        self.total_intent_predictions = 0
        self.correct_intent_predictions = 0

        self.allocated_resources = 0
        self.useful_resources = 0

        self.priority_missions = 0
        self.priority_missions_completed = 0

        # -----------------------------
        # Service continuity
        # -----------------------------
        self.total_service_time = 0
        self.service_available_time = 0

        # -----------------------------
        # Resilience
        # -----------------------------
        self.performance_before_failure = []
        self.performance_after_recovery = []

        # -----------------------------
        # Swarm coordination
        # -----------------------------
        self.total_coordination_events = 0
        self.successful_coordination_events = 0

        # -----------------------------
        # Learning
        # -----------------------------
        self.convergence_step = None

        # -----------------------------
        # I-MACSI specific
        # -----------------------------
        self.intent_dissemination_messages = 0
        self.resource_reorg_events = 0
        self.encryption_events = 0
        self.gateway_selections = 0
        
        self.joint_optimization_events = 0
        self.bandwidth_allocation_events = 0
        self.beam_steering_events = 0
        self.compute_placement_events = 0
        self.gateway_assignment_events = 0

    # ==========================================================
    # COMMUNICATION METRICS
    # ==========================================================

    def average_latency(self):

        if not self.packet_delays:
            return 0

        return sum(self.packet_delays) / len(self.packet_delays)


    def throughput(self, simulation_time):

        if simulation_time <= 0:
            return 0

        return self.total_bits_delivered / simulation_time


    def packet_delivery_ratio(self):

        if self.total_packets_sent == 0:
            return 0

        return min(100.0, (
            self.total_packets_delivered /
            self.total_packets_sent
        ) * 100)


    # ==========================================================
    # SPECTRAL EFFICIENCY
    # ==========================================================

    def spectral_efficiency(self, simulation_time):

        """
        Spectral Efficiency =
        Throughput / Bandwidth

        Unit:
        bits/sec/Hz
        """

        throughput = self.throughput(simulation_time)

        if self.total_bandwidth_hz <= 0:
            return 0

        return throughput / self.total_bandwidth_hz


    # ==========================================================
    # ENERGY CONSUMPTION
    # ==========================================================

    def energy_consumption(self):

        """
        Total Energy =
        Transmission Energy +
        Computation Energy +
        Idle Energy
        """

        return (
            self.transmission_energy_j +
            self.computation_energy_j +
            self.idle_energy_j
        )


    # ==========================================================
    # ENERGY PER SUCCESSFUL BIT
    # ==========================================================

    def energy_per_bit(self):

        """
        Energy efficiency metric.

        Joules per successfully delivered bit.
        """

        if self.total_bits_delivered == 0:
            return 0

        return (
            self.energy_consumption() /
            self.total_bits_delivered
        )


    # ==========================================================
    # BANDWIDTH UTILIZATION
    # ==========================================================

    def bandwidth_utilization(self):

        if self.total_bandwidth_hz <= 0:
            return 0

        return (
            self.used_bandwidth_hz /
            self.total_bandwidth_hz
        ) * 100


    # ==========================================================
    # ROUTING STABILITY
    # ==========================================================

    def routing_stability(self):

        if self.total_routes == 0:
            return 0

        return (
            self.stable_routes /
            self.total_routes
        ) * 100


    # ==========================================================
    # FAIRNESS INDEX
    # ==========================================================

    def fairness_index(self):

        """
        Jain's Fairness Index

        F = (sum(x)^2) /
            (n * sum(x^2))
        """

        if not self.flow_throughputs:
            return 0

        n = len(self.flow_throughputs)

        total = sum(self.flow_throughputs)

        square_sum = sum(
            x * x for x in self.flow_throughputs
        )

        if square_sum == 0:
            return 0

        return (
            total * total
        ) / (
            n * square_sum
        )


    # ==========================================================
    # COMPUTATIONAL OVERHEAD
    # ==========================================================

    def computational_overhead(self, baseline_operations):

        if baseline_operations <= 0:
            return 0

        return (
            self.computation_operations /
            baseline_operations
        ) * 100


    # ==========================================================
    # MISSION COMPLETION
    # ==========================================================

    def mission_completion_ratio(self):

        if self.total_missions == 0:
            return 0

        return (
            self.completed_missions /
            self.total_missions
        ) * 100


    # ==========================================================
    # MISSION SATISFACTION INDEX
    # ==========================================================

    def mission_satisfaction_index(self):

        if not self.mission_satisfaction_scores:
            return 0

        return (
            sum(self.mission_satisfaction_scores) /
            len(self.mission_satisfaction_scores)
        )


    # ==========================================================
    # INTENT PREDICTION ACCURACY
    # ==========================================================

    def intent_prediction_accuracy(self):

        if self.total_intent_predictions == 0:
            return 0

        return (
            self.correct_intent_predictions /
            self.total_intent_predictions
        ) * 100


    # ==========================================================
    # ADAPTIVE RESOURCE ALLOCATION
    # ==========================================================

    def resource_allocation_efficiency(self):

        if self.allocated_resources == 0:
            return 0

        return (
            self.useful_resources /
            self.allocated_resources
        ) * 100


    # ==========================================================
    # MISSION PRIORITY PRESERVATION
    # ==========================================================

    def priority_preservation(self):

        if self.priority_missions == 0:
            return 0

        return (
            self.priority_missions_completed /
            self.priority_missions
        ) * 100


    # ==========================================================
    # SERVICE CONTINUITY
    # ==========================================================

    def service_continuity(self):

        if self.total_service_time <= 0:
            return 0

        return (
            self.service_available_time /
            self.total_service_time
        ) * 100


    # ==========================================================
    # DYNAMIC RESILIENCE
    # ==========================================================

    def resilience(self):

        if not self.performance_before_failure:
            return 0

        if not self.performance_after_recovery:
            return 0

        before = (
            sum(self.performance_before_failure) /
            len(self.performance_before_failure)
        )

        after = (
            sum(self.performance_after_recovery) /
            len(self.performance_after_recovery)
        )

        if before == 0:
            return 0

        return (
            after / before
        ) * 100


    # ==========================================================
    # SWARM COORDINATION
    # ==========================================================

    def swarm_coordination_efficiency(self):

        if self.total_coordination_events == 0:
            return 0

        return (
            self.successful_coordination_events /
            self.total_coordination_events
        ) * 100


    # ==========================================================
    # LEARNING CONVERGENCE
    # ==========================================================

    def learning_convergence_speed(self):

        if self.convergence_step is None:
            return 0

        return self.convergence_step


    # ==========================================================
    # I-MACSI: INTENT DISSEMINATION OVERHEAD
    # ==========================================================

    def intent_dissemination_overhead(self):
        """
        Ratio of intent dissemination messages to total packets sent.
        Lower is more efficient.
        """
        if self.total_packets_sent == 0:
            return 0
        return self.intent_dissemination_messages / self.total_packets_sent


    # ==========================================================
    # I-MACSI: RESOURCE REORGANIZATION RATE
    # ==========================================================

    def resource_reorganization_rate(self):
        """
        Resource reorganization events per packet.
        Indicates how actively the swarm adapts its resources.
        """
        if self.total_packets_sent == 0:
            return 0
        return self.resource_reorg_events / self.total_packets_sent

    # ==========================================================
    # I-MACSI: JOINT OPTIMIZATION EVENTS
    # ==========================================================

    def joint_optimization_rate(self):
        """
        Graph optimization events (BW, beam, compute, gateway) per packet.
        """
        if self.total_packets_sent == 0:
            return 0
        return self.joint_optimization_events / self.total_packets_sent


    # ==========================================================
    # COMPUTATIONAL COMPLEXITY
    # ==========================================================

    def q_learning_complexity(
        self,
        number_of_agents,
        number_of_states,
        number_of_actions
    ):

        """
        Q-table size:

        O(Agents × States × Actions)
        """

        return (
            number_of_agents *
            number_of_states *
            number_of_actions
        )


    # ==========================================================
    # COMPLETE METRICS
    # ==========================================================

    def calculate_all(
        self,
        simulation_time,
        baseline_operations=1,
        number_of_agents=1,
        number_of_states=1,
        number_of_actions=1
    ):

        return {

            # Conventional metrics

            "average_latency_ms":
                self.average_latency(),

            "throughput_bps":
                self.throughput(
                    simulation_time
                ),

            "packet_delivery_ratio":
                self.packet_delivery_ratio(),

            "routing_stability":
                self.routing_stability(),

            "spectral_efficiency":
                self.spectral_efficiency(
                    simulation_time
                ),

            "energy_consumption_j":
                self.energy_consumption(),

            "energy_per_bit_j":
                self.energy_per_bit(),

            "computational_overhead":
                self.computational_overhead(
                    baseline_operations
                ),

            "fairness_index":
                self.fairness_index(),

            "bandwidth_utilization":
                self.bandwidth_utilization(),

            # Mission metrics

            "mission_completion_ratio":
                self.mission_completion_ratio(),

            "mission_satisfaction_index":
                self.mission_satisfaction_index(),

            "intent_prediction_accuracy":
                self.intent_prediction_accuracy(),

            "resource_allocation_efficiency":
                self.resource_allocation_efficiency(),

            "mission_priority_preservation":
                self.priority_preservation(),

            "service_continuity":
                self.service_continuity(),

            "dynamic_resilience":
                self.resilience(),

            "swarm_coordination_efficiency":
                self.swarm_coordination_efficiency(),

            "learning_convergence_speed":
                self.learning_convergence_speed(),

            "computational_complexity":
                self.q_learning_complexity(
                    number_of_agents,
                    number_of_states,
                    number_of_actions
                ),

            # I-MACSI metrics

            "intent_dissemination_overhead":
                self.intent_dissemination_overhead(),

            "resource_reorganization_rate":
                self.resource_reorganization_rate(),

            "encryption_events":
                self.encryption_events,

            "gateway_selections":
                self.gateway_selections,
                
            "joint_optimization_rate":
                self.joint_optimization_rate(),
                
            "bandwidth_allocation_events":
                self.bandwidth_allocation_events,
                
            "beam_steering_events":
                self.beam_steering_events,
                
            "compute_placement_events":
                self.compute_placement_events,
        }
