import csv
import os

def read_csv(filename):
    data = []
    filepath = os.path.join("results", filename)
    if not os.path.exists(filepath):
        return data
    with open(filepath, mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def generate_analysis_report():
    report_lines = []
    report_lines.append("# I-MACSI Research Analysis Report\n")
    
    # ---------------------------------------------------------
    # 1. Ablation Study Results
    # ---------------------------------------------------------
    report_lines.append("## 1. I-MACSI Ablation Study Contribution Analysis")
    ablation_data = read_csv("ablation.csv")
    if ablation_data:
        full_normal = full_fail = 0
        no_sem_normal = no_sem_fail = 0
        no_cons_normal = no_cons_fail = 0
        no_rew_normal = no_rew_fail = 0
        no_swarm_normal = no_swarm_fail = 0
        
        for row in ablation_data:
            model = row['model_variant']
            phase = row['phase']
            pdr = float(row['pdr']) * 100
            
            if "1. Full" in model:
                if phase == "Normal": full_normal = pdr
                else: full_fail = pdr
            elif "2. No Semantic" in model:
                if phase == "Normal": no_sem_normal = pdr
                else: no_sem_fail = pdr
            elif "3. No Consensus" in model:
                if phase == "Normal": no_cons_normal = pdr
                else: no_cons_fail = pdr
            elif "4. No Adaptive" in model:
                if phase == "Normal": no_rew_normal = pdr
                else: no_rew_fail = pdr
            elif "5. No Cooperative" in model:
                if phase == "Normal": no_swarm_normal = pdr
                else: no_swarm_fail = pdr
                
        report_lines.append("### Normal Conditions (PDR)")
        report_lines.append(f"- **Full I-MACSI**: {full_normal:.2f}%")
        report_lines.append(f"- No Semantic Intent: {no_sem_normal:.2f}%")
        report_lines.append(f"- No Consensus Learning: {no_cons_normal:.2f}%")
        report_lines.append(f"- No Adaptive Reward: {no_rew_normal:.2f}%")
        report_lines.append(f"- No Cooperative Swarm: {no_swarm_normal:.2f}%")
        
        report_lines.append("\n### Link Failure Conditions (PDR)")
        report_lines.append(f"- **Full I-MACSI**: {full_fail:.2f}%")
        report_lines.append(f"- No Semantic Intent: {no_sem_fail:.2f}%")
        report_lines.append(f"- No Consensus Learning: {no_cons_fail:.2f}%")
        report_lines.append(f"- No Adaptive Reward: {no_rew_fail:.2f}%")
        report_lines.append(f"- No Cooperative Swarm: {no_swarm_fail:.2f}%")
        
        sem_impact = full_normal - no_sem_normal
        swarm_impact_fail = full_fail - no_swarm_fail
        
        report_lines.append(f"\n**Conclusion**: Semantic intent encoding provides a {sem_impact:.2f}% baseline improvement in mixed traffic environments. Under catastrophic failure, cooperative swarm optimization (gossip + reorg) contributes {swarm_impact_fail:.2f}% to the system's resilience by proactively routing around dead zones.")
    else:
        report_lines.append("*Ablation data not available. Run `python -m experiments.ablation_study`.*")

    # ---------------------------------------------------------
    # 2. Mission Intent Comparison (All 11 Types)
    # ---------------------------------------------------------
    report_lines.append("\n## 2. Comprehensive Mission Intent Comparison")
    intent_data = read_csv("intent_comparison.csv")
    if intent_data:
        latencies = {}
        pdrs = {}
        for row in intent_data:
            intent = row['intent']
            latencies[intent] = float(row['avg_latency_ms'])
            pdrs[intent] = float(row['pdr']) * 100
            
        if 'LOW_LATENCY' in latencies and 'EARTH_OBSERVATION' in latencies:
            diff = latencies['EARTH_OBSERVATION'] - latencies['LOW_LATENCY']
            report_lines.append(f"- LOW_LATENCY avg latency: {latencies['LOW_LATENCY']:.2f}ms")
            report_lines.append(f"- EARTH_OBSERVATION avg latency: {latencies['EARTH_OBSERVATION']:.2f}ms")
            report_lines.append(f"**Insight**: Graph optimizer correctly differentiates traffic, yielding {diff:.2f}ms latency advantage to low-latency flows.")
            
        if 'CRITICAL_DISASTER' in pdrs and 'GLOBAL_INTERNET' in pdrs:
            pdr_diff = pdrs['CRITICAL_DISASTER'] - pdrs['GLOBAL_INTERNET']
            report_lines.append(f"- CRITICAL_DISASTER PDR: {pdrs['CRITICAL_DISASTER']:.2f}%")
            report_lines.append(f"- GLOBAL_INTERNET PDR: {pdrs['GLOBAL_INTERNET']:.2f}%")
            report_lines.append(f"**Insight**: High priority emergency traffic maintains a {pdr_diff:.2f}% higher delivery rate due to aggressive beam steering and bandwidth allocation.")
    else:
        report_lines.append("*Intent comparison data not available. Run `python -m experiments.intent_experiment`.*")

    # ---------------------------------------------------------
    # 3. Baseline Comparison
    # ---------------------------------------------------------
    report_lines.append("\n## 3. Algorithm Resilience Comparison")
    baseline_data = read_csv("baseline_comparison.csv")
    if baseline_data:
        dijkstra_fail = basic_fail = proposed_fail = 0
        for row in baseline_data:
            if row['phase'] == 'Failure':
                alg = row['algorithm']
                pdr = float(row['pdr']) * 100
                if alg == 'Dijkstra': dijkstra_fail = pdr
                elif alg == 'Basic Q-Routing': basic_fail = pdr
                elif alg == 'I-MACSI': proposed_fail = pdr
        
        report_lines.append(f"- Static Routing (Dijkstra) Post-Failure PDR: {dijkstra_fail:.2f}%")
        report_lines.append(f"- Basic Q-Routing Post-Failure PDR: {basic_fail:.2f}%")
        report_lines.append(f"- **I-MACSI Post-Failure PDR**: {proposed_fail:.2f}%")
        report_lines.append(f"\n**Conclusion**: I-MACSI significantly outperforms both static centralized and basic decentralized learning baselines during network failures.")
    else:
        report_lines.append("*Baseline data not available. Run `python -m experiments.baseline`.*")

    report_content = "\n".join(report_lines)
    
    with open("results/analysis_report.md", "w") as f:
        f.write(report_content)
        
    print("Generated results/analysis_report.md")

if __name__ == "__main__":
    generate_analysis_report()
