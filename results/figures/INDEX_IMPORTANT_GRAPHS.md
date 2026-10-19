# 🎯 Curated Important Evaluation Graphs for I-MACSI

This folder contains the **33 essential, flagship research graphs** selected across the 10 evaluation domains of the **I-MACSI** mega-constellation paper. All figures are calibrated against authentic simulation data with **95% Confidence Intervals** across 50 Monte Carlo trials.

---

## 1. 📡 Communication Performance
*Core physical and link-layer metrics under scaling constellation size (20 to 200 satellites).*
- [01_Satellites_vs_Throughput.png](./Communication_Performance/01_Satellites_vs_Throughput.png): Throughput (Gbps) scaling vs. constellation size.
- [02_Satellites_vs_Latency.png](./Communication_Performance/02_Satellites_vs_Latency.png): End-to-end packet latency (ms) comparison.
- [03_Satellites_vs_PDR.png](./Communication_Performance/03_Satellites_vs_PDR.png): Packet Delivery Ratio (%) across satellites.

---

## 2. 🎯 Mission Performance & Intent Awareness
*Heterogeneous multi-mission QoS satisfaction and priority handling (5 to 100 missions).*
- [10_Missions_vs_Completion.png](./Mission_Performance/10_Missions_vs_Completion.png): Mission completion ratio (%) under rising concurrent missions.
- [12_Missions_vs_Intent_Accuracy.png](./Mission_Performance/12_Missions_vs_Intent_Accuracy.png): 8D Intent prediction and matching accuracy (%).
- [13_Missions_vs_Priority_Preservation.png](./Mission_Performance/13_Missions_vs_Priority_Preservation.png): Preservation of emergency/military mission priority.

---

## 3. 📈 Scalability Analysis
*Traffic overload stress tests across mission densities and massive user counts (100 to 5000).*
- [19_Mission_Density_vs_Throughput.png](./Scalability/19_Mission_Density_vs_Throughput.png): Constellation throughput vs. mission density (0.2–2.0 missions/node).
- [20_Mission_Density_vs_Latency.png](./Scalability/20_Mission_Density_vs_Latency.png): E2E latency resilience under buffer queuing stress.
- [25_Users_vs_Throughput.png](./Scalability/25_Users_vs_Throughput.png): Total system throughput under massive user scaling.

---

## 4. 🔄 Training Convergence & Learning Dynamics
*Multi-agent Q-learning stability and loss decay over 1000 training episodes.*
- [31_Episodes_vs_Reward.png](./Convergence/31_Episodes_vs_Reward.png): Cumulative episodic reward trajectory.
- [32_Training_Episodes_vs_Mission_Success_Rate.png](./Convergence/32_Training_Episodes_vs_Mission_Success_Rate.png): Policy success rate progression.
- [33_Training_Episodes_vs_Convergence_Loss.png](./Convergence/33_Training_Episodes_vs_Convergence_Loss.png): TD Bellman error / MSE loss decay.

---

## 5. ⚡ Resource Allocation
*Fine-grained slice allocation across 8 standardized mission profiles.*
- [37_Resource_vs_MissionType.png](./Resource_Allocation/37_Resource_vs_MissionType.png): Resource utilization (%) by mission profile.
- [38_Beam_Allocation_Efficiency_vs_Mission_Type.png](./Resource_Allocation/38_Beam_Allocation_Efficiency_vs_Mission_Type.png): RF beam hopping efficiency (%).
- [39_Gateway_Selection_Accuracy_vs_Mission_Type.png](./Resource_Allocation/39_Gateway_Selection_Accuracy_vs_Mission_Type.png): Feeder link gateway assignment precision (%).

---

## 6. 🛡️ Robustness & Fault Tolerance
*Constellation self-healing under harsh space conditions (0–50% link severance, 0–25% node loss).*
- [43_Failure_vs_Completion.png](./Robustness/43_Failure_vs_Completion.png): Mission completion ratio vs. link failure probability.
- [44_Satellite_Failure_Rate_vs_Throughput.png](./Robustness/44_Satellite_Failure_Rate_vs_Throughput.png): Constellation throughput under radiation/satellite outages.
- [45_Satellite_Failure_Rate_vs_Latency.png](./Robustness/45_Satellite_Failure_Rate_vs_Latency.png): Detour latency penalty under satellite dropouts.

---

## 7. 🌍 Mission-Specific Benchmarks
*Workload evaluations across critical real-world satellite applications.*
- [49_Disaster_Mission_vs_Throughput.png](./Mission_Specific/49_Disaster_Mission_vs_Throughput.png): High-throughput emergency disaster relief traffic.
- [50_Military_Mission_vs_Security_Satisfaction.png](./Mission_Specific/50_Military_Mission_vs_Security_Satisfaction.png): Cryptographic hardware path enforcement for defense data.
- [51_Remote_Healthcare_vs_Latency.png](./Mission_Specific/51_Remote_Healthcare_vs_Latency.png): Ultra-low latency guarantee for remote telesurgery.

---

## 8. 🧠 AI & Cognitive Swarm Dynamics
*Mechanisms governing swarm consensus, gossip protocols, and representation size.*
- [57_Semantic_Encoding_Accuracy_vs_Mission_Success.png](./AI_Specific/57_Semantic_Encoding_Accuracy_vs_Mission_Success.png): Intent representation accuracy vs. mission success.
- [59_Intent_Dissemination_Delay_vs_Mission_Completion.png](./AI_Specific/59_Intent_Dissemination_Delay_vs_Mission_Completion.png): Bounded gossip delay (TTL=2) impact.
- [61_Mission_Intent_Vector_Size_vs_Computational_Complexity.png](./AI_Specific/61_Mission_Intent_Vector_Size_vs_Computational_Complexity.png): Complexity trade-off across 4D, 8D, 16D, and 32D intent vectors.

---

## 9. ⚙️ Complexity & Hardware Feasibility
*Wall-clock execution time, RAM footprint, and algorithmic operation bounds.*
- [63_Number_of_Satellites_vs_Execution_Time.png](./Complexity/63_Number_of_Satellites_vs_Execution_Time.png): Sub-second routing execution time vs. constellation scale.
- [64_Number_of_Satellites_vs_Memory_Consumption.png](./Complexity/64_Number_of_Satellites_vs_Memory_Consumption.png): On-board RAM consumption (MB) fitting space avionics.
- [65_Number_of_Satellites_vs_Computational_Complexity.png](./Complexity/65_Number_of_Satellites_vs_Computational_Complexity.png): Relative operations per hop compared to deep models.

---

## 10. 📊 Statistical Synthesis & Distributions
*Holistic multi-metric synthesis, percentage improvements, and continuous empirical CDFs.*
- [68_Average_Performance_Comparison.png](./Statistical/68_Average_Performance_Comparison.png): Multi-metric normalized score across 8 QoS dimensions.
- [69_Percentage_Improvement.png](./Statistical/69_Percentage_Improvement.png): Average percentage improvement of I-MACSI over all 9 baselines (+18.5% to +62.0%).
- [70_Radar_Chart_Comparison.png](./Statistical/70_Radar_Chart_Comparison.png): 6-dimensional QoS radar footprint.
- [71_Box_Plot_Variability.png](./Statistical/71_Box_Plot_Variability.png): Performance variability across 50 independent trials.
- [72_CDF_Latency.png](./Statistical/72_CDF_Latency.png): Continuous Cumulative Distribution Function of packet latency.
- [73_CDF_Throughput.png](./Statistical/73_CDF_Throughput.png): Continuous Cumulative Distribution Function of flow throughput.
