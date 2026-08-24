# Literature Review: State-of-the-Art AI in Satellite Networking (2023-2026)

This review surveys recent advancements in artificial intelligence applied to Low Earth Orbit (LEO) satellite network routing, resource allocation, and orchestration, primarily focusing on publications from leading IEEE journals over the past three years. This serves as the benchmark foundation for validating the **Intent-Aware Multi-Agent Cognitive Swarm Intelligence (I-MACSI)** architecture.

## 1. Multi-Agent Deep Reinforcement Learning (MADRL)
Traditional routing protocols (OSPF, Dijkstra) struggle with the highly dynamic topology of LEO mega-constellations. Recent research has heavily favored **Multi-Agent Deep Reinforcement Learning (MADRL)**. 

- **Key Advancements**: Works in IEEE Transactions on Wireless Communications (2023-2024) have demonstrated MADRL's ability to decentralize routing decisions. Satellites act as independent agents optimizing a global reward function (e.g., minimizing delay or maximizing throughput) using algorithms like Multi-Agent Proximal Policy Optimization (MAPPO).
- **Limitations**: Standard MADRL relies on fixed reward functions. While excellent for uniform traffic, they fail to adapt when mission objectives shift dynamically (e.g., switching from bulk file transfer to ultra-reliable low-latency emergency communications). 
- **I-MACSI Advantage**: I-MACSI replaces the fixed reward function with **Adaptive Semantic Reward Formulation**, where the intent vector dynamically reshapes the Q-learning reward surface in real-time.

## 2. Federated Multi-Agent Learning (FedMARL)
To address the massive communication overhead required to train centralized MADRL models across thousands of satellites, researchers have introduced **Federated Learning (FL)** into multi-agent systems.

- **Key Advancements**: Recent papers in IEEE JSAC (2024-2025) propose FedMARL frameworks where LEO satellites train local routing policies and periodically aggregate model weights (e.g., Q-tables or Neural Network weights) via Inter-Satellite Links (ISLs) without sharing raw packet data, preserving privacy and reducing overhead.
- **Limitations**: While FedMARL solves the training overhead bottleneck, it remains agnostic to the *semantic* nature of the data it routes. It optimizes the network purely as a bit-pipe.
- **I-MACSI Advantage**: I-MACSI inherits FedMARL for scalable consensus but injects **Cognitive Swarm Intent Caches** into the federation process, ensuring the swarm synchronizes not just routing policies, but active mission awareness.

## 3. Graph Neural Networks (GNN) and GAT-RA
Given that LEO constellations are fundamentally dynamic graphs, **Graph Reinforcement Learning (Graph RL)** and **Graph Attention Networks for Resource Allocation (GAT-RA)** have emerged as powerful tools.

- **Key Advancements**: Studies in IEEE Transactions on Mobile Computing (2025) utilize GATs to capture the topological dependencies of the constellation. These networks allocate bandwidth and compute resources by learning the spatial correlation of traffic congestion.
- **Limitations**: GNNs require extensive offline training and struggle to generalize to sudden, catastrophic topological changes (e.g., cascading node failures or targeted adversarial attacks) without retraining.
- **I-MACSI Advantage**: I-MACSI utilizes a decentralized **Hybrid AI-Optimization** approach. Instead of a monolithic GNN, I-MACSI uses a fast, greedy graph-optimizer locally at each node, constrained by the semantic intent vector. This provides instantaneous, zero-shot adaptation to topology failures.

## 4. Intent-Based Networking (IBN) & Semantic Communications (6G)
With the advent of 6G, the paradigm is shifting from Shannon's classical communication (transmitting bits accurately) to **Semantic Communication** (transmitting meaning/intent).

- **Key Advancements**: Recent IBN frameworks for Software-Defined Networks (SDN), published in IEEE Transactions on Network Science and Engineering (2024-2026), introduce orchestrators that parse natural language intents into network policies. 
- **Limitations**: Current IBN architectures are overwhelmingly centralized. A central SDN controller parses the intent, computes the global policy, and pushes flow rules to switches. In a LEO environment, continuous link to a central Earth controller incurs unacceptable propagation delays and single points of failure.
- **I-MACSI Advantage**: I-MACSI completely decentralizes the intent paradigm. Through the **Intent Dissemination Protocol (Gossip)**, mission objectives are flooded locally through the space segment, allowing the satellite swarm to autonomously satisfy the intent without central orchestration.

## Conclusion: The Gap Addressed by I-MACSI
The current state-of-the-art is fragmented: MADRL and FedMARL optimize decentralized routing but lack mission awareness; IBN provides mission awareness but relies on centralized control; GAT-RA provides resource allocation but is computationally rigid. 

**I-MACSI bridges this gap** by fusing decentralized swarm intelligence (FedMARL) with 6G semantic communications (Intent Vectors) and hybrid resource orchestration, establishing a foundation for true AI-native, mission-driven satellite networks.
