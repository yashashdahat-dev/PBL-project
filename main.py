import sys
import subprocess

# Automatically check and download required dependencies if missing
try:
    # pyrefly: ignore [missing-import]
    import matplotlib
    # pyrefly: ignore [missing-import]
    import networkx
except ImportError:
    print("[SETUP] Automatically downloading & installing missing dependencies (matplotlib, networkx)...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib", "networkx"])

import time
from config import Config
from network.topology import ConstellationTopology
from network.isl_state import ISLState
from intent.mission_intent import StandardIntents
from routing.intent_router import IntentRouter
from routing.q_routing import QRoutingManager
from learning.q_learning import QLearningEngine
from visualization.network_visualizer import NetworkVisualizer
from simulation.environment import SimulationEnvironment
from simulation.failure import FailureModel

def run_interactive_simulation():
    config = Config()
    print("=" * 80)
    print(" LEO SWARM INTERACTIVE Q-ROUTING VISUALIZER ")
    print("=" * 80)

    # 1. Initialize Network & Agents
    topology = ConstellationTopology(num_planes=4, sats_per_plane=4)
    topology.build_network()
    router = IntentRouter(max_latency_ms=50.0, max_bw_mbps=1000.0, max_loss=1.0)
    ql_engine = QLearningEngine(alpha=config.learning.alpha, gamma=config.learning.gamma)
    
    # Initialize decentralized QRouting Manager and Simulation Environment
    q_manager = QRoutingManager(topology, router, ql_engine, epsilon=config.learning.epsilon, epsilon_decay=config.learning.epsilon_decay)
    failure_model = FailureModel(topology)
    env = SimulationEnvironment(topology, q_manager, failure_model)
    
    visualizer = NetworkVisualizer(topology)

    source_id = "P0_S0"
    destination_id = "P2_S3"
    intent = StandardIntents.LOW_LATENCY

    from simulation.traffic import TrafficGenerator
    traffic_gen = TrafficGenerator(topology)

    # 2. Pre-train Swarm Q-Tables (Normal Network)
    print("\n[PHASE 1] Training Swarm Q-Routing...")
    
    # Run 40 packets of training
    train_batch = traffic_gen.generate_batch(40)
    # Force the last packet to be our specific visual path
    train_batch[-1].source_id = source_id
    train_batch[-1].dest_id = destination_id
    train_batch[-1].intent = intent
    
    results = env.process_traffic_batch(train_batch, q_manager)
    optimal_path = results["paths"][-1]

    # Render Optimal Route Visual
    print("\n[VISUAL] Rendering Optimal Path (Low Latency Intent)...")
    visualizer.draw_snapshot(active_path=optimal_path, title=f"Optimal Q-Route: {' -> '.join(optimal_path)}")

    # 3. Simulate Link Failure Event
    if len(optimal_path) >= 2:
        failed_link_a = optimal_path[0]
        failed_link_b = optimal_path[1]
        print(f"\n[EVENT] Injecting Link Failure: {failed_link_a} <-> {failed_link_b}")
        
        # Manually trigger failure for visual demonstration, though FailureModel supports random injection
        topology.nodes[failed_link_a].update_link_state(failed_link_b, ISLState.FAILED)
        topology.nodes[failed_link_b].update_link_state(failed_link_a, ISLState.FAILED) # Bidirectional failure

        # Render Failure Visual
        visualizer.draw_snapshot(active_path=[source_id], title=f"ISL Failure Injected ({failed_link_a} <-> {failed_link_b})")
    else:
        print("Path too short to inject failure.")

    # 4. Swarm Dynamic Re-Routing Recovery
    print("[PHASE 2] Swarm Autonomous Re-Routing (Measuring Recovery Time)...")
    # Increase exploration slightly for recovery
    q_manager.epsilon = 0.1
    
    # Simulate packets until swarm finds a successful route
    recovery_packets_needed = 0
    recovered_path = []
    
    for ep in range(25):
        recovery_packets_needed += 1
        # Send a single targeted packet to test recovery
        test_batch = traffic_gen.generate_batch(1)
        test_batch[0].source_id = source_id
        test_batch[0].dest_id = destination_id
        test_batch[0].intent = intent
        
        res = env.process_traffic_batch(test_batch, q_manager)
        if res["successful_packets"] > 0:
            recovered_path = res["paths"][0]
            print(f"Swarm successfully recovered route after {recovery_packets_needed} failed packet attempts.")
            break
            
    # Continue learning to stabilize route
    stabilize_batch = traffic_gen.generate_batch(10)
    env.process_traffic_batch(stabilize_batch, q_manager)

    # Render Recovered Route Visual
    if recovered_path:
        print("\n[VISUAL] Rendering Swarm Recovered Route...")
        visualizer.draw_snapshot(active_path=recovered_path, title=f"Autonomous Swarm Recovery Path: {' -> '.join(recovered_path)}")
    else:
        print("\n[FAILED] Swarm could not recover route.")

if __name__ == "__main__":
    run_interactive_simulation()