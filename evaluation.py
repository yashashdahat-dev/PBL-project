import numpy as np
import csv
import os


class LEOEvaluator:
    """
    Evaluation framework for Intent-Aware Multi-Agent Cognitive Swarm Q-Routing.

    Conventional Metrics:
        Latency, Throughput, PDR, Routing Stability, Spectral Efficiency,
        Energy Consumption, Computational Overhead, Fairness Index,
        Bandwidth Utilization.

    Mission-Specific Metrics:
        Mission Completion Ratio, Mission Satisfaction Index,
        Intent Prediction Accuracy, Resource Allocation Efficiency,
        Mission Priority Preservation, Service Continuity,
        Dynamic Resilience, Swarm Coordination Efficiency,
        Learning Convergence Speed, Computational Complexity, Scalability.
    """

    def __init__(self, total_simulation_time: float):
        self.total_simulation_time = total_simulation_time

        # Packet statistics
        self.sent_packets = 0
        self.delivered_packets = 0
        self.packet_delays = []      # ms per delivered packet
        self.delivered_bits = 0.0   # bits

        # Routing
        self.total_routes = 0
        self.stable_routes = 0

        # Bandwidth
        self.total_bandwidth = 0.0  # Hz
        self.used_bandwidth = 0.0   # Hz

        # Energy
        self.transmission_energy = 0.0  # Joules
        self.computation_energy = 0.0   # Joules

        # Computation overhead
        self.actual_computation = 0.0
        self.baseline_computation = 0.0

        # Per-flow throughput for Jain fairness
        self.flow_throughputs = []

        # Mission statistics
        self.total_missions = 0
        self.completed_missions = 0
        self.mission_satisfaction = []   # 0.0 – 1.0 per mission

        # Intent prediction
        self.correct_intents = 0
        self.total_intents = 0

        # Resource allocation
        self.useful_resources = 0.0
        self.allocated_resources = 0.0

        # High-priority missions
        self.high_priority_total = 0
        self.high_priority_completed = 0

        # Service continuity
        self.service_available_time = 0.0

        # Dynamic resilience
        self.performance_before_change = []
        self.performance_after_change = []

        # Swarm coordination
        self.successful_coordination = 0
        self.total_coordination = 0

        # Learning
        self.learning_convergence_step = None

        # Scalability log
        self.scalability_log = []

    # ------------------------------------------------------------------
    # CONVENTIONAL METRICS
    # ------------------------------------------------------------------

    def average_latency(self) -> float:
        if not self.packet_delays:
            return 0.0
        return float(np.mean(self.packet_delays))

    def throughput(self) -> float:
        if self.total_simulation_time == 0:
            return 0.0
        return self.delivered_bits / self.total_simulation_time

    def packet_delivery_ratio(self) -> float:
        if self.sent_packets == 0:
            return 0.0
        return (self.delivered_packets / self.sent_packets) * 100.0

    def routing_stability(self) -> float:
        if self.total_routes == 0:
            return 0.0
        return (self.stable_routes / self.total_routes) * 100.0

    def spectral_efficiency(self) -> float:
        if self.total_bandwidth == 0:
            return 0.0
        return self.throughput() / self.total_bandwidth

    def energy_consumption(self) -> float:
        return self.transmission_energy + self.computation_energy

    def computational_overhead(self) -> float:
        if self.baseline_computation == 0:
            return 0.0
        return (self.actual_computation / self.baseline_computation) * 100.0

    def fairness_index(self) -> float:
        x = np.array(self.flow_throughputs, dtype=float)
        if len(x) == 0:
            return 0.0
        numerator = float(np.sum(x) ** 2)
        denominator = float(len(x) * np.sum(x ** 2))
        if denominator == 0:
            return 0.0
        return numerator / denominator

    def bandwidth_utilization(self) -> float:
        if self.total_bandwidth == 0:
            return 0.0
        return (self.used_bandwidth / self.total_bandwidth) * 100.0

    # ------------------------------------------------------------------
    # MISSION-SPECIFIC METRICS
    # ------------------------------------------------------------------

    def mission_completion_ratio(self) -> float:
        if self.total_missions == 0:
            return 0.0
        return (self.completed_missions / self.total_missions) * 100.0

    def mission_satisfaction_index(self) -> float:
        if not self.mission_satisfaction:
            return 0.0
        return float(np.mean(self.mission_satisfaction))

    def intent_prediction_accuracy(self) -> float:
        if self.total_intents == 0:
            return 0.0
        return (self.correct_intents / self.total_intents) * 100.0

    def resource_allocation_efficiency(self) -> float:
        if self.allocated_resources == 0:
            return 0.0
        return (self.useful_resources / self.allocated_resources) * 100.0

    def mission_priority_preservation(self) -> float:
        if self.high_priority_total == 0:
            return 0.0
        return (self.high_priority_completed / self.high_priority_total) * 100.0

    def service_continuity(self) -> float:
        if self.total_simulation_time == 0:
            return 0.0
        return (self.service_available_time / self.total_simulation_time) * 100.0

    def dynamic_resilience(self) -> float:
        if not self.performance_before_change:
            return 0.0
        before = float(np.mean(self.performance_before_change))
        after = float(np.mean(self.performance_after_change))
        if before == 0:
            return 0.0
        return (after / before) * 100.0

    def swarm_coordination_efficiency(self) -> float:
        if self.total_coordination == 0:
            return 0.0
        return (self.successful_coordination / self.total_coordination) * 100.0

    def learning_convergence_speed(self):
        return self.learning_convergence_step

    def computational_complexity(
        self,
        number_of_agents: int,
        number_of_states: int,
        number_of_actions: int
    ) -> int:
        return number_of_agents * number_of_states * number_of_actions

    # ------------------------------------------------------------------
    # HELPER: Q-CONVERGENCE MONITOR
    # ------------------------------------------------------------------

    def check_q_convergence(
        self,
        current_q: float,
        step: int,
        previous_q: list,
        threshold: float = 0.001,
        window: int = 20
    ) -> list:
        """
        Call once per step with the max absolute Q-table delta.
        Sets self.learning_convergence_step when stable for `window` steps.

        Usage:
            q_history = []
            for step in range(STEPS):
                delta = max_abs_q_table_change(q_table, old_q_table)
                q_history = evaluator.check_q_convergence(delta, step, q_history)
        """
        previous_q.append(current_q)
        if (
            len(previous_q) >= window
            and self.learning_convergence_step is None
        ):
            recent = previous_q[-window:]
            if max(recent) - min(recent) < threshold:
                self.learning_convergence_step = step
                print(f"[Evaluator] Q-learning converged at step {step}.")
        return previous_q

    # ------------------------------------------------------------------
    # HELPER: SCALABILITY LOG
    # ------------------------------------------------------------------

    def log_scalability_point(
        self,
        num_satellites: int,
        num_missions: int,
        computation_time: float
    ):
        """Record one experiment entry keyed by constellation size."""
        self.scalability_log.append({
            "num_satellites": num_satellites,
            "num_missions": num_missions,
            "pdr": self.packet_delivery_ratio(),
            "avg_latency_ms": self.average_latency(),
            "throughput_bps": self.throughput(),
            "mission_completion_ratio": self.mission_completion_ratio(),
            "computation_time_s": computation_time,
        })

    # ------------------------------------------------------------------
    # REPORT GENERATION
    # ------------------------------------------------------------------

    def generate_report(
        self,
        number_of_agents: int = 1,
        number_of_states: int = 1,
        number_of_actions: int = 1
    ) -> dict:
        return {
            # Conventional
            "Average E2E Latency (ms)": self.average_latency(),
            "Throughput (bits/sec)": self.throughput(),
            "Packet Delivery Ratio (%)": self.packet_delivery_ratio(),
            "Routing Stability (%)": self.routing_stability(),
            "Spectral Efficiency (bits/sec/Hz)": self.spectral_efficiency(),
            "Energy Consumption (J)": self.energy_consumption(),
            "Computational Overhead (%)": self.computational_overhead(),
            "Fairness Index": self.fairness_index(),
            "Bandwidth Utilization (%)": self.bandwidth_utilization(),
            # Mission-specific
            "Mission Completion Ratio (%)": self.mission_completion_ratio(),
            "Mission Satisfaction Index": self.mission_satisfaction_index(),
            "Intent Prediction Accuracy (%)": self.intent_prediction_accuracy(),
            "Resource Allocation Efficiency (%)": self.resource_allocation_efficiency(),
            "Mission Priority Preservation (%)": self.mission_priority_preservation(),
            "Service Continuity (%)": self.service_continuity(),
            "Dynamic Resilience (%)": self.dynamic_resilience(),
            "Swarm Coordination Efficiency (%)": self.swarm_coordination_efficiency(),
            "Learning Convergence Speed (steps)": self.learning_convergence_speed(),
            "Computational Complexity (Q-table entries)": self.computational_complexity(
                number_of_agents, number_of_states, number_of_actions
            ),
        }

    def print_report(self, report: dict):
        print()
        print("=" * 72)
        print("  LEO AI-NATIVE NETWORK PERFORMANCE EVALUATION")
        print("=" * 72)
        for metric, value in report.items():
            if value is None:
                print(f"  {metric:<50}: Not converged")
            elif isinstance(value, float):
                print(f"  {metric:<50}: {value:.4f}")
            else:
                print(f"  {metric:<50}: {value}")
        print("=" * 72)
        if self.scalability_log:
            print()
            print("  SCALABILITY LOG")
            print("  " + "-" * 68)
            hdr = f"  {'Satellites':>12} {'Missions':>10} {'PDR (%)':>10} {'Latency ms':>12} {'Comp (s)':>10}"
            print(hdr)
            print("  " + "-" * 68)
            for row in self.scalability_log:
                print(
                    f"  {row['num_satellites']:>12}"
                    f" {row['num_missions']:>10}"
                    f"   {row['pdr']:>8.2f}"
                    f" {row['avg_latency_ms']:>12.2f}"
                    f" {row['computation_time_s']:>10.4f}"
                )
            print("=" * 72)

    def save_report_csv(
        self,
        report: dict,
        filepath: str = "results/evaluation_report.csv"
    ):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["metric", "value"])
            for metric, value in report.items():
                writer.writerow([metric, value if value is not None else "N/A"])
        if self.scalability_log:
            sp = filepath.replace("evaluation_report.csv", "scalability_report.csv")
            with open(sp, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.scalability_log[0].keys())
                writer.writeheader()
                writer.writerows(self.scalability_log)
        print(f"[Evaluator] Report saved -> {filepath}")


# ======================================================================
# DEMO  (python evaluation.py)
# ======================================================================

if __name__ == "__main__":
    SIMULATION_TIME = 100   # seconds

    ev = LEOEvaluator(total_simulation_time=SIMULATION_TIME)
    q_history = []

    for step in range(SIMULATION_TIME):
        # Packet
        ev.sent_packets += 1
        if np.random.rand() > 0.05:
            ev.delivered_packets += 1
            ev.packet_delays.append(np.random.uniform(20, 80))
            ev.delivered_bits += 1000 * 8

        # Routing
        ev.total_routes += 1
        if np.random.rand() > 0.08:
            ev.stable_routes += 1

        # Bandwidth
        ev.total_bandwidth += 1e6
        ev.used_bandwidth += np.random.uniform(6e5, 9e5)

        # Energy
        ev.transmission_energy += 0.05
        ev.computation_energy += 0.01

        # Overhead
        ev.actual_computation += 0.002
        ev.baseline_computation += 0.001

        # Fairness
        ev.flow_throughputs.append(np.random.uniform(500, 1500))

        # Missions
        ev.total_missions += 1
        if np.random.rand() > 0.08:
            ev.completed_missions += 1
        ev.mission_satisfaction.append(np.random.uniform(0.7, 1.0))

        # Intent prediction
        ev.total_intents += 1
        if np.random.rand() > 0.07:
            ev.correct_intents += 1

        # Resources
        ev.allocated_resources += 100
        ev.useful_resources += np.random.uniform(70, 95)

        # Priority missions
        ev.high_priority_total += 1
        if np.random.rand() > 0.03:
            ev.high_priority_completed += 1

        # Service continuity
        ev.service_available_time += np.random.uniform(0.8, 1.0)

        # Dynamic resilience split at step 50
        perf = ev.packet_delivery_ratio()
        if step < 50:
            ev.performance_before_change.append(perf)
        else:
            ev.performance_after_change.append(perf * 0.95)

        # Swarm coordination
        ev.total_coordination += 1
        if np.random.rand() > 0.07:
            ev.successful_coordination += 1

        # Q-convergence
        delta = abs(np.random.normal(0, 1.0 / (step + 1)))
        q_history = ev.check_q_convergence(delta, step, q_history)

    # Scalability snapshot
    ev.log_scalability_point(num_satellites=16, num_missions=100, computation_time=0.068)

    report = ev.generate_report(number_of_agents=16, number_of_states=50, number_of_actions=8)
    ev.print_report(report)
    ev.save_report_csv(report)
