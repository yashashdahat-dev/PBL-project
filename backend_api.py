import asyncio
import threading
import json
import websockets
from flask import Flask, jsonify, request
from flask_cors import CORS

# Import simulation logic
from config import Config
from network.topology import ConstellationTopology
from network.isl_state import ISLState
from intent.mission_intent import StandardIntents, IntentExtractionEngine
from routing.intent_router import IntentRouter
from routing.q_routing import QRoutingManager
from learning.q_learning import QLearningEngine
from simulation.environment import SimulationEnvironment
from simulation.failure import FailureModel
from simulation.traffic import TrafficGenerator
from network_metrics import NetworkMetrics

# --- Initialize Global Simulation State ---
NUM_SATELLITES = 16
SATS_PER_PLANE = 4
NUM_PLANES = 4

print("Initializing LEO Digital Twin Backend...")
topology = ConstellationTopology(num_planes=NUM_PLANES, sats_per_plane=SATS_PER_PLANE)
topology.build_network()
config = Config()
router = QRoutingManager(
    topology,
    IntentRouter(max_latency_ms=50.0, max_bw_mbps=1000.0, max_loss=1.0),
    QLearningEngine(alpha=config.learning.alpha, gamma=config.learning.gamma),
    epsilon=0.2,
    epsilon_decay=0.995
)
env = SimulationEnvironment(topology, router, FailureModel(topology))

global_metrics = NetworkMetrics()
global_metrics.total_bandwidth_hz = 1e9

# Pre-train routing with all three intent types
print("Pre-training Q-routing swarm (100 episodes)...")
traffic_gen = TrafficGenerator(topology)
batch = traffic_gen.generate_batch(100)
env.process_traffic_batch(batch, router, global_metrics)
print(f"Pre-training complete. Epsilon: {router.epsilon:.4f}")

# Map frontend intent strings to StandardIntents objects
INTENT_MAP = {
    "LOW_LATENCY": StandardIntents.LOW_LATENCY,
    "CRITICAL_DISASTER": StandardIntents.CRITICAL_DISASTER,
    "EARTH_OBSERVATION": StandardIntents.EARTH_OBSERVATION,
    "SECURE_MISSION": StandardIntents.SECURE_MISSION,
    "ENVIRONMENTAL_MONITORING": StandardIntents.ENVIRONMENTAL_MONITORING,
    "AUTONOMOUS_MARITIME": StandardIntents.AUTONOMOUS_MARITIME,
    "MILITARY_RECONNAISSANCE": StandardIntents.MILITARY_RECONNAISSANCE,
    "GLOBAL_INTERNET": StandardIntents.GLOBAL_INTERNET,
    "REMOTE_HEALTHCARE": StandardIntents.REMOTE_HEALTHCARE,
    "PRECISION_AGRI": StandardIntents.PRECISION_AGRI,
    "INDUSTRIAL_IOT": StandardIntents.INDUSTRIAL_IOT
}

# --- Flask REST API ---
app = Flask(__name__)
CORS(app)

@app.route("/network", methods=["GET"])
def get_network():
    satellites = []
    links = []
    added_links = set()

    for sat_id, sat_node in topology.nodes.items():
        satellites.append({
            "id": sat_id,
            "status": "ACTIVE"
        })
        for neighbor_id, link in sat_node.isl_interfaces.items():
            if link.state == ISLState.ACTIVE:
                link_tuple = tuple(sorted([sat_id, neighbor_id]))
                if link_tuple not in added_links:
                    links.append([sat_id, neighbor_id])
                    added_links.add(link_tuple)

    return jsonify({"satellites": satellites, "links": links})

@app.route("/network/state", methods=["GET"])
def get_network_state():
    """Full live network state — link loads, congestion, failed links."""
    result = {}
    for sat_id, sat_node in topology.nodes.items():
        neighbors = {}
        for nbr_id, link in sat_node.isl_interfaces.items():
            neighbors[nbr_id] = {
                "state": link.state.name,
                "latency_ms": round(link.dynamic_latency, 2) if link.state.name != "FAILED" else None,
                "congestion": round(link.congestion_level, 3),
                "bandwidth_mbps": round(link.available_bandwidth, 1),
                "packet_loss": round(link.packet_loss, 4),
            }
        result[sat_id] = {"neighbors": neighbors}
    return jsonify(result)

@app.route("/route/calculate", methods=["POST"])
def calculate_route():
    data = request.json
    src = data.get("source")
    dst = data.get("destination")
    intent_str = data.get("intent", "CRITICAL_DISASTER")

    if src not in topology.nodes:
        return jsonify({"error": f"Unknown source: {src}"}), 400
    if dst not in topology.nodes:
        return jsonify({"error": f"Unknown destination: {dst}"}), 400

    if intent_str in INTENT_MAP:
        target_intent = INTENT_MAP[intent_str]
    else:
        # Dynamically extract intent using the cognitive engine
        target_intent = IntentExtractionEngine.extract_intent(intent_str)

    # Run the cognitive Q-routing through the environment to update all global metrics
    from simulation.traffic import TrafficFlow
    flow = TrafficFlow(src, dst, 100.0, 5.0, target_intent) # 100kb, priority 5
    if target_intent == StandardIntents.LOW_LATENCY:
        flow.deadline_ms = 50.0
    elif target_intent == StandardIntents.EARTH_OBSERVATION:
        flow.deadline_ms = 500.0
    elif target_intent == StandardIntents.SECURE_MISSION:
        flow.deadline_ms = 200.0
        
    res = env.process_traffic_batch([flow], router, global_metrics)
    path = res["paths"][0] if res["paths"] else [src]
    success = res["successful_packets"] > 0

    broadcast_event({
        "type": "route_update",
        "source": src,
        "destination": dst,
        "route": path,
        "intent": intent_str,
        "success": success,
        "hops": len(path) - 1
    })

    return jsonify({"route": path, "success": success, "hops": len(path) - 1})

@app.route("/intent/extract", methods=["POST"])
def extract_intent_endpoint():
    data = request.json
    description = data.get("description", "")
    
    extracted = IntentExtractionEngine.extract_intent(description)
    
    return jsonify({
        "name": extracted.name,
        "w_latency": round(extracted.w_latency, 2),
        "w_throughput": round(extracted.w_throughput, 2),
        "w_reliability": round(extracted.w_reliability, 2),
        "w_congestion": round(extracted.w_congestion, 2),
        "priority": extracted.priority
    })

@app.route("/simulate/failure", methods=["POST"])
def simulate_failure():
    data = request.json
    src = data.get("source")
    dst = data.get("destination")

    if src not in topology.nodes:
        return jsonify({"status": "error", "message": f"Unknown node: {src}"}), 400
    if dst not in topology.nodes[src].isl_interfaces:
        return jsonify({"status": "error", "message": f"No direct link between {src} and {dst}"}), 400

    topology.nodes[src].update_link_state(dst, ISLState.FAILED)
    topology.nodes[dst].update_link_state(src, ISLState.FAILED)

    broadcast_event({
        "type": "link_failure",
        "link": [src, dst],
        "reason": "USER_INJECTED"
    })
    return jsonify({"status": "success", "link": [src, dst]})

@app.route("/simulate/recovery", methods=["POST"])
def simulate_recovery():
    data = request.json
    src = data.get("source")
    dst = data.get("destination")

    if src not in topology.nodes:
        return jsonify({"status": "error", "message": f"Unknown node: {src}"}), 400
    if dst not in topology.nodes[src].isl_interfaces:
        return jsonify({"status": "error", "message": f"No direct link between {src} and {dst}"}), 400

    topology.nodes[src].update_link_state(dst, ISLState.ACTIVE)
    topology.nodes[dst].update_link_state(src, ISLState.ACTIVE)

    broadcast_event({
        "type": "link_recovery",
        "link": [src, dst]
    })
    return jsonify({"status": "success", "link": [src, dst]})

@app.route("/simulate/random_failure", methods=["POST"])
def random_failure():
    """Inject a random active link failure into the network."""
    import random
    active_links = []
    for node_id, node in topology.nodes.items():
        for nbr_id, link in node.isl_interfaces.items():
            if link.state == ISLState.ACTIVE and node_id < nbr_id:
                active_links.append((node_id, nbr_id))
    if not active_links:
        return jsonify({"status": "no_active_links"}), 400
    node_a, node_b = random.choice(active_links)
    topology.nodes[node_a].update_link_state(node_b, ISLState.FAILED)
    topology.nodes[node_b].update_link_state(node_a, ISLState.FAILED)
    broadcast_event({"type": "link_failure", "link": [node_a, node_b], "reason": "RANDOM_FAILURE"})
    return jsonify({"status": "success", "link": [node_a, node_b]})

@app.route("/train", methods=["POST"])
def train_more():
    """Run additional training episodes."""
    data = request.json or {}
    count = min(data.get("count", 50), 500)
    batch = traffic_gen.generate_batch(count)
    results = env.process_traffic_batch(batch, router, global_metrics)
    return jsonify({
        "episodes": count,
        "pdr": round(results["pdr"], 3),
        "avg_latency_ms": round(results["avg_latency_ms"], 2),
        "avg_hops": round(results["avg_hops"], 2),
        "epsilon": round(router.epsilon, 4)
    })

@app.route("/metrics", methods=["GET"])
def get_metrics():
    # Dynamic recalculation based on current environment state
    metrics_report = global_metrics.calculate_all(
        simulation_time=global_metrics.total_packets_sent,
        baseline_operations=1000,
        number_of_agents=NUM_SATELLITES,
        number_of_states=NUM_SATELLITES,
        number_of_actions=4
    )
    
    # Clean up non-finite numbers before jsonifying
    for key, value in metrics_report.items():
        if value is None:
            metrics_report[key] = 0.0
            
    return jsonify(metrics_report)

def run_flask():
    app.run(host="0.0.0.0", port=8000, debug=False, use_reloader=False)

# --- WebSocket Server ---
connected_clients = set()
loop = None

async def websocket_handler(websocket):
    connected_clients.add(websocket)
    try:
        async for _ in websocket:
            pass  # One-way push server
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        connected_clients.discard(websocket)

def broadcast_event(event_data: dict):
    if loop and loop.is_running():
        msg = json.dumps(event_data)
        for client in list(connected_clients):
            asyncio.run_coroutine_threadsafe(client.send(msg), loop)

async def main_ws():
    global loop
    loop = asyncio.get_running_loop()
    print("WebSocket server running on ws://localhost:8001")
    async with websockets.serve(websocket_handler, "0.0.0.0", 8001):
        await asyncio.Future()  # run forever

def run_websockets():
    asyncio.run(main_ws())

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_websockets()
