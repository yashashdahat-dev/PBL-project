from network_metrics import NetworkMetrics
from network.topology import ConstellationTopology
from routing.q_routing import QRoutingManager
from simulation.failure import FailureModel
from intent.mission_intent import IntentVector
from network.isl_state import ISLState
from learning.consensus import ConsensusEngine

class SimulationEnvironment:
    def __init__(self, topology: ConstellationTopology, q_manager: QRoutingManager, failure_model: FailureModel):
        self.topology = topology
        self.q_manager = q_manager
        self.failure_model = failure_model
        self.current_step = 0
        self.consensus_engine = ConsensusEngine(sync_interval=20, consensus_weight=0.2)
        
    def step(self):
        """Advances the simulation clock by one tick."""
        self.current_step += 1
        if self.current_step % self.consensus_engine.sync_interval == 0:
            self.consensus_engine.synchronize(self.topology)
        
    def process_traffic_batch(self, flows: list, router_manager, global_metrics: NetworkMetrics = None) -> dict:
        """
        Simulates a batch of TrafficFlows across the network using a specific router manager.
        Tracks deep metrics including End-to-End latency, hops, PDR, Throughput, QoS Satisfaction, and Routing Overhead.
        """
        metrics = {
            "total_packets": len(flows),
            "successful_packets": 0,
            "failed_packets": 0,
            "total_latency_ms": 0.0,
            "total_hops": 0,
            "total_throughput_kbps": 0.0,
            "qos_met_packets": 0,
            "routing_overhead": 0,
            "paths": [],
            "mission_completion_ratio": 0.0,
            "intent_prediction_accuracy": 1.0, # Assumed 1.0 for simulated ground truth
            "adaptive_resource_allocation_efficiency": 0.0
        }
        
        resource_efficiency_scores = []
        
        for flow in flows:
            self.step() # Advance simulation clock to trigger consensus periodically
            
            # Route packet
            path, success = router_manager.route_packet(flow.source_id, flow.dest_id, flow.intent)
            metrics["routing_overhead"] += len(path) - 1 # Assuming 1 Q-update per hop
            
            if success:
                metrics["successful_packets"] += 1
                metrics["paths"].append(path)
                
                # Calculate metrics for the successful path
                hops = len(path) - 1
                metrics["total_hops"] += hops
                
                # Sum the latencies along the physical path and check for failures
                path_latency = 0.0
                path_failed = False
                for i in range(len(path) - 1):
                    node_a = path[i]
                    node_b = path[i+1]
                    link = self.topology.nodes[node_a].isl_interfaces.get(node_b)
                    if not link or link.state == ISLState.FAILED:
                        path_failed = True
                        break
                    path_latency += link.dynamic_latency
                
                if path_failed:
                    metrics["successful_packets"] -= 1
                    metrics["failed_packets"] += 1
                    if global_metrics:
                        global_metrics.total_packets_sent += 1
                        global_metrics.total_missions += 1
                        global_metrics.total_service_time += 1 # service attempted
                        if flow.priority <= 2:
                            global_metrics.priority_missions += 1
                        
                        # Incorrect prediction if we picked a failed path
                        global_metrics.total_intent_predictions += 1
                        global_metrics.total_coordination_events += 1
                    continue
                    
                metrics["total_latency_ms"] += path_latency
                
                if path_latency <= flow.deadline_ms:
                    metrics["qos_met_packets"] += 1
                    
                # Calculate adaptive resource allocation efficiency
                # High priority flows on paths with high latency are less efficient
                efficiency = 1.0 - min((path_latency / flow.deadline_ms) * (1.0 / flow.priority), 1.0)
                resource_efficiency_scores.append(efficiency)
                
                if global_metrics:
                    global_metrics.total_packets_sent += 1
                    global_metrics.total_packets_delivered += 1
                    global_metrics.packet_delays.append(path_latency)
                    global_metrics.total_bits_delivered += flow.packet_size_kb * 8000
                    
                    global_metrics.total_routes += 1
                    global_metrics.stable_routes += 1
                    
                    # Bandwidth
                    allocated_bandwidth = (flow.packet_size_kb * 8000) / 0.002
                    global_metrics.used_bandwidth_hz += allocated_bandwidth

                    # Energy consumption
                    TX_POWER_W = 20
                    packet_transmission_time = 0.002
                    global_metrics.transmission_energy_j += TX_POWER_W * packet_transmission_time
                    
                    CPU_POWER_W = 5
                    computation_time = 0.001
                    global_metrics.computation_energy_j += CPU_POWER_W * computation_time
                    
                    IDLE_POWER_W = 2
                    idle_time = 0.1
                    global_metrics.idle_energy_j += IDLE_POWER_W * idle_time
                    
                    global_metrics.total_missions += 1
                    global_metrics.completed_missions += 1
                    global_metrics.mission_satisfaction_scores.append(efficiency)
                    
                    if flow.priority <= 2:
                        global_metrics.priority_missions += 1
                        global_metrics.priority_missions_completed += 1
                    
                    global_metrics.total_intent_predictions += 1
                    # A correct intent prediction actually meets the mission deadline/requirements
                    if path_latency <= flow.deadline_ms:
                        global_metrics.correct_intent_predictions += 1
                    
                    global_metrics.allocated_resources += 100
                    global_metrics.useful_resources += efficiency * 100
                    
                    global_metrics.total_coordination_events += 1
                    global_metrics.successful_coordination_events += 1
                    
                    global_metrics.total_service_time += 1
                    global_metrics.service_available_time += 1
                    
                # Calculate throughput for this flow (kbps)
                if path_latency > 0:
                    throughput_kbps = (flow.packet_size_kb * 8) / (path_latency / 1000)
                    metrics["total_throughput_kbps"] += throughput_kbps
                    if global_metrics:
                        global_metrics.flow_throughputs.append(throughput_kbps * 1000)
                
            else:
                metrics["failed_packets"] += 1
                if global_metrics:
                    global_metrics.total_packets_sent += 1
                    global_metrics.total_missions += 1
                    global_metrics.total_service_time += 1 # service attempted
                    global_metrics.total_intent_predictions += 1 # Failed to predict a valid intent
                    global_metrics.total_coordination_events += 1 # Coordination occurred but failed
                    if flow.priority <= 2:
                        global_metrics.priority_missions += 1
                
            # Allow learning models to decay their exploration parameter if supported
            if hasattr(router_manager, 'decay_epsilon'):
                router_manager.decay_epsilon()
                
        # Calculate aggregate metrics
        if metrics["successful_packets"] > 0:
            metrics["avg_latency_ms"] = metrics["total_latency_ms"] / metrics["successful_packets"]
            metrics["avg_hops"] = metrics["total_hops"] / metrics["successful_packets"]
            metrics["pdr"] = metrics["successful_packets"] / metrics["total_packets"]
            metrics["packet_loss_rate"] = 1.0 - metrics["pdr"]
            metrics["avg_throughput_kbps"] = metrics["total_throughput_kbps"] / metrics["successful_packets"]
            metrics["qos_satisfaction"] = metrics["qos_met_packets"] / metrics["total_packets"]
            
            # Mission specific metrics
            metrics["mission_completion_ratio"] = metrics["pdr"] * metrics["qos_satisfaction"]
            if resource_efficiency_scores:
                metrics["adaptive_resource_allocation_efficiency"] = sum(resource_efficiency_scores) / len(resource_efficiency_scores)
            else:
                metrics["adaptive_resource_allocation_efficiency"] = 0.0
        else:
            metrics["avg_latency_ms"] = float('inf')
            metrics["avg_hops"] = 0.0
            metrics["pdr"] = 0.0
            metrics["packet_loss_rate"] = 1.0
            metrics["avg_throughput_kbps"] = 0.0
            metrics["qos_satisfaction"] = 0.0
            
        return metrics
