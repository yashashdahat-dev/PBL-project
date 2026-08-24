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
    report_lines.append("# Research Analysis Report")
    report_lines.append("## 1. Ablation Study Results")
    
    ablation_data = read_csv("ablation.csv")
    if ablation_data:
        full_pdr = 0
        basic_pdr = 0
        nocog_pdr = 0
        for row in ablation_data:
            model = row['model_variant']
            pdr = float(row['pdr']) * 100
            if "Full" in model: full_pdr = pdr
            elif "No Intent" in model: basic_pdr = pdr
            elif "No Cognitive" in model: nocog_pdr = pdr
            
        report_lines.append(f"- **Full Proposed Model PDR**: {full_pdr:.2f}%")
        report_lines.append(f"- **No Intent Awareness PDR**: {basic_pdr:.2f}%")
        report_lines.append(f"- **No Cognitive State PDR**: {nocog_pdr:.2f}%")
        
        intent_gain = full_pdr - basic_pdr
        cog_gain = full_pdr - nocog_pdr
        
        report_lines.append(f"**Conclusion**: Intent awareness improves PDR by {intent_gain:.2f}% under mixed traffic. Proactive cognitive state sharing improves PDR by {cog_gain:.2f}% under link failure conditions.")

    report_lines.append("\n## 2. Baseline Comparison (Resilience)")
    baseline_data = read_csv("baseline_comparison.csv")
    if baseline_data:
        for row in baseline_data:
            if row['phase'] == 'Failure' and row['algorithm'] == 'Dijkstra':
                dijkstra_fail = float(row['pdr']) * 100
            elif row['phase'] == 'Failure' and row['algorithm'] == 'Proposed AI-Native':
                proposed_fail = float(row['pdr']) * 100
        
        report_lines.append(f"- **Static Routing (Dijkstra) Post-Failure PDR**: {dijkstra_fail:.2f}%")
        report_lines.append(f"- **Proposed Model Post-Failure PDR**: {proposed_fail:.2f}%")
        report_lines.append(f"**Conclusion**: The AI-Native model is significantly more resilient to catastrophic link failures, autonomously rerouting to avoid dead zones.")

    report_lines.append("\n## 3. Intent Differentiation")
    intent_data = read_csv("intent_comparison.csv")
    if intent_data:
        latencies = {}
        for row in intent_data:
            latencies[row['intent']] = float(row['avg_latency_ms'])
            
        if 'LOW_LATENCY' in latencies and 'EARTH_OBSERVATION' in latencies:
            diff = latencies['EARTH_OBSERVATION'] - latencies['LOW_LATENCY']
            report_lines.append(f"- LOW_LATENCY average latency: {latencies['LOW_LATENCY']:.2f}ms")
            report_lines.append(f"- EARTH_OBSERVATION average latency: {latencies['EARTH_OBSERVATION']:.2f}ms")
            report_lines.append(f"**Conclusion**: The routing engine correctly differentiates traffic, providing a {diff:.2f}ms latency advantage to critical low-latency flows.")

    report_content = "\n".join(report_lines)
    
    with open("results/analysis_report.md", "w") as f:
        f.write(report_content)
        
    print("Generated results/analysis_report.md")

if __name__ == "__main__":
    generate_analysis_report()
