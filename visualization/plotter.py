# pyrefly: ignore [missing-import]
import matplotlib.pyplot as plt
import csv
import os

class Plotter:
    def __init__(self, results_dir="results", output_dir="results/figures"):
        self.results_dir = results_dir
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def read_csv(self, filename):
        data = []
        filepath = os.path.join(self.results_dir, filename)
        if not os.path.exists(filepath):
            print(f"Warning: {filepath} not found.")
            return data
        with open(filepath, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        return data

    def plot_latency_vs_load(self):
        data = self.read_csv("congestion.csv")
        if not data: return
        loads = [float(row['traffic_load']) for row in data]
        latencies = [float(row['avg_latency_ms']) for row in data]
        
        plt.figure(figsize=(8, 5))
        plt.plot(loads, latencies, marker='o', linestyle='-', color='b')
        plt.title('Average Latency vs Traffic Load')
        plt.xlabel('Traffic Load (Packets/Batch)')
        plt.ylabel('Average Latency (ms)')
        plt.grid(True)
        plt.savefig(os.path.join(self.output_dir, '1_latency_vs_load.png'), dpi=300)
        plt.close()

    def plot_throughput_vs_load(self):
        data = self.read_csv("congestion.csv")
        if not data: return
        loads = [float(row['traffic_load']) for row in data]
        throughputs = [float(row['avg_throughput_kbps']) for row in data]
        
        plt.figure(figsize=(8, 5))
        plt.plot(loads, throughputs, marker='s', linestyle='-', color='g')
        plt.title('Throughput vs Traffic Load')
        plt.xlabel('Traffic Load (Packets/Batch)')
        plt.ylabel('Average Throughput (kbps)')
        plt.grid(True)
        plt.savefig(os.path.join(self.output_dir, '2_throughput_vs_load.png'), dpi=300)
        plt.close()

    def plot_pdr_vs_failures(self):
        data = self.read_csv("link_failure.csv")
        if not data: return
        failures = [float(row['failures_injected']) for row in data]
        pdrs = [float(row['pdr']) * 100 for row in data]
        
        plt.figure(figsize=(8, 5))
        plt.plot(failures, pdrs, marker='^', linestyle='-', color='r')
        plt.title('Packet Delivery Ratio vs Number of Failures')
        plt.xlabel('Number of Injected ISL Failures')
        plt.ylabel('Packet Delivery Ratio (%)')
        plt.grid(True)
        plt.savefig(os.path.join(self.output_dir, '3_pdr_vs_failures.png'), dpi=300)
        plt.close()

    def plot_recovery_vs_failures(self):
        data = self.read_csv("link_failure.csv")
        if not data: return
        failures = [float(row['failures_injected']) for row in data]
        recovery = [float(row['recovery_time_packets']) for row in data]
        
        plt.figure(figsize=(8, 5))
        plt.bar(failures, recovery, color='orange')
        plt.title('Recovery Time vs Number of Failed Links')
        plt.xlabel('Number of Failed Links')
        plt.ylabel('Recovery Time (Packets)')
        plt.xticks(failures)
        plt.grid(axis='y')
        plt.savefig(os.path.join(self.output_dir, '4_recovery_vs_failures.png'), dpi=300)
        plt.close()

    def plot_convergence(self):
        data = self.read_csv("convergence.csv")
        if not data: return
        packets = [float(row['packets_processed']) for row in data]
        pdrs = [float(row['pdr']) * 100 for row in data]
        
        plt.figure(figsize=(8, 5))
        plt.plot(packets, pdrs, marker='.', linestyle='-', color='purple')
        plt.title('Learning Convergence Curve')
        plt.xlabel('Packets Processed')
        plt.ylabel('Packet Delivery Ratio (%)')
        plt.grid(True)
        plt.savefig(os.path.join(self.output_dir, '5_learning_convergence.png'), dpi=300)
        plt.close()

    def plot_intent_comparison(self):
        data = self.read_csv("intent_comparison.csv")
        if not data: return
        intents = [row['intent'] for row in data]
        latencies = [float(row['avg_latency_ms']) for row in data]
        
        plt.figure(figsize=(14, 7))
        colors = ['blue', 'green', 'red'] * (len(intents) // 3 + 1)
        plt.bar(intents, latencies, color=colors[:len(intents)])
        plt.title('Intent-wise Performance Comparison (Latency)')
        plt.xlabel('Mission Intent')
        plt.ylabel('Average Latency (ms)')
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, '6_intent_comparison.png'), dpi=300)
        plt.close()

    def plot_scalability(self):
        data = self.read_csv("scalability.csv")
        if not data: return
        sats = [str(row['total_satellites']) for row in data]
        times = [float(row['computation_time_seconds']) for row in data]
        
        plt.figure(figsize=(8, 5))
        plt.plot(sats, times, marker='o', linestyle='-', color='brown')
        plt.title('Scalability: Network Size vs Computation Time')
        plt.xlabel('Number of Satellites')
        plt.ylabel('Computation Time (seconds)')
        plt.grid(True)
        plt.savefig(os.path.join(self.output_dir, '7_scalability.png'), dpi=300)
        plt.close()

    def plot_baseline_comparison(self):
        data = self.read_csv("baseline_comparison.csv")
        if not data: return
        
        algo_data_train = {}
        algo_data_fail = {}
        for row in data:
            algo = row['algorithm']
            if algo not in algo_data_train:
                algo_data_train[algo] = []
                algo_data_fail[algo] = []
            
            if row['phase'] == 'Training':
                algo_data_train[algo].append(float(row['pdr']) * 100)
            elif row['phase'] == 'Failure':
                algo_data_fail[algo].append(float(row['pdr']) * 100)
                
        import numpy as np
        algorithms = list(algo_data_train.keys())
        pdr_train = [np.mean(algo_data_train[a]) for a in algorithms]
        pdr_fail = [np.mean(algo_data_fail[a]) for a in algorithms]
                
        import numpy as np
        x = np.arange(len(algorithms))
        width = 0.35
        
        plt.figure(figsize=(10, 6))
        plt.bar(x - width/2, pdr_train, width, label='Normal Training')
        plt.bar(x + width/2, pdr_fail, width, label='Post-Failure')
        
        plt.title('Routing Performance Comparison')
        plt.ylabel('Packet Delivery Ratio (%)')
        plt.xticks(x, algorithms)
        plt.legend()
        plt.grid(axis='y')
        plt.savefig(os.path.join(self.output_dir, '8_baseline_comparison.png'), dpi=300)
        plt.close()

    def plot_ablation_study(self):
        data = self.read_csv("ablation.csv")
        if not data: return
        
        import numpy as np
        model_data_normal = {}
        model_data_failure = {}
        
        for row in data:
            variant = row['model_variant']
            if variant not in model_data_normal:
                model_data_normal[variant] = []
                model_data_failure[variant] = []
            if row['phase'] == 'Normal':
                model_data_normal[variant].append(float(row['pdr']) * 100)
            elif row['phase'] == 'Failure':
                model_data_failure[variant].append(float(row['pdr']) * 100)
                
        models = list(model_data_normal.keys())
        pdr_normal = [np.mean(model_data_normal[m]) for m in models]
        pdr_failure = [np.mean(model_data_failure[m]) for m in models]
        
        x = np.arange(len(models))
        width = 0.35
        
        plt.figure(figsize=(12, 6))
        plt.bar(x - width/2, pdr_normal, width, label='Normal', color='steelblue')
        plt.bar(x + width/2, pdr_failure, width, label='Post-Failure', color='coral')
        
        plt.title('Ablation Study: Component Impact on PDR')
        plt.ylabel('Packet Delivery Ratio (%)')
        plt.xticks(x, models, rotation=30, ha='right')
        plt.legend()
        plt.grid(axis='y')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, '9_ablation_study.png'), dpi=300)
        plt.close()

    def plot_baseline_latency(self):
        """Baseline comparison: Average Latency across algorithms."""
        data = self.read_csv("baseline_comparison.csv")
        if not data: return

        import numpy as np
        algo_data_train = {}
        algo_data_fail = {}
        for row in data:
            algo = row['algorithm']
            if algo not in algo_data_train:
                algo_data_train[algo] = []
                algo_data_fail[algo] = []
            
            if row['phase'] == 'Training':
                algo_data_train[algo].append(float(row['avg_latency_ms']))
            elif row['phase'] == 'Failure':
                algo_data_fail[algo].append(float(row['avg_latency_ms']))
                
        algorithms = list(algo_data_train.keys())
        lat_train = [np.mean(algo_data_train[a]) for a in algorithms]
        lat_fail = [np.mean(algo_data_fail[a]) for a in algorithms]

        x = np.arange(len(algorithms))
        width = 0.35

        plt.figure(figsize=(10, 6))
        bars1 = plt.bar(x - width/2, lat_train, width, label='Normal Training', color='steelblue')
        bars2 = plt.bar(x + width/2, lat_fail, width, label='Post-Failure', color='coral')

        for bar in bars1:
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                     f'{bar.get_height():.1f}', ha='center', va='bottom', fontsize=9)
        for bar in bars2:
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                     f'{bar.get_height():.1f}', ha='center', va='bottom', fontsize=9)

        plt.title('Baseline Comparison: Average Latency')
        plt.ylabel('Average Latency (ms)')
        plt.xticks(x, algorithms)
        plt.legend()
        plt.grid(axis='y')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, '10_baseline_latency.png'), dpi=300)
        plt.close()

    def plot_baseline_throughput(self):
        """Baseline comparison: Throughput across algorithms."""
        data = self.read_csv("baseline_comparison.csv")
        if not data: return

        import numpy as np
        algo_data_train = {}
        algo_data_fail = {}
        for row in data:
            algo = row['algorithm']
            if algo not in algo_data_train:
                algo_data_train[algo] = []
                algo_data_fail[algo] = []
            
            if row['phase'] == 'Training':
                algo_data_train[algo].append(float(row['avg_throughput_kbps']) / 1000)
            elif row['phase'] == 'Failure':
                algo_data_fail[algo].append(float(row['avg_throughput_kbps']) / 1000)
                
        algorithms = list(algo_data_train.keys())
        tp_train = [np.mean(algo_data_train[a]) for a in algorithms]
        tp_fail = [np.mean(algo_data_fail[a]) for a in algorithms]

        x = np.arange(len(algorithms))
        width = 0.35

        plt.figure(figsize=(10, 6))
        plt.bar(x - width/2, tp_train, width, label='Normal Training', color='seagreen')
        plt.bar(x + width/2, tp_fail, width, label='Post-Failure', color='salmon')

        plt.title('Baseline Comparison: Average Throughput')
        plt.ylabel('Average Throughput (Mbps)')
        plt.xticks(x, algorithms)
        plt.legend()
        plt.grid(axis='y')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, '11_baseline_throughput.png'), dpi=300)
        plt.close()

    def plot_baseline_qos(self):
        """Baseline comparison: QoS Satisfaction across algorithms."""
        data = self.read_csv("baseline_comparison.csv")
        if not data: return

        import numpy as np
        algo_data_train = {}
        algo_data_fail = {}
        for row in data:
            algo = row['algorithm']
            if algo not in algo_data_train:
                algo_data_train[algo] = []
                algo_data_fail[algo] = []
            
            if row['phase'] == 'Training':
                algo_data_train[algo].append(float(row['qos_satisfaction']) * 100)
            elif row['phase'] == 'Failure':
                algo_data_fail[algo].append(float(row['qos_satisfaction']) * 100)
                
        algorithms = list(algo_data_train.keys())
        qos_train = [np.mean(algo_data_train[a]) for a in algorithms]
        qos_fail = [np.mean(algo_data_fail[a]) for a in algorithms]

        x = np.arange(len(algorithms))
        width = 0.35

        plt.figure(figsize=(10, 6))
        plt.bar(x - width/2, qos_train, width, label='Normal Training', color='mediumpurple')
        plt.bar(x + width/2, qos_fail, width, label='Post-Failure', color='gold')

        plt.title('Baseline Comparison: QoS Satisfaction')
        plt.ylabel('QoS Satisfaction (%)')
        plt.xticks(x, algorithms)
        plt.legend()
        plt.grid(axis='y')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, '12_baseline_qos.png'), dpi=300)
        plt.close()

    def plot_intent_pdr(self):
        """Intent-wise PDR comparison."""
        data = self.read_csv("intent_comparison.csv")
        if not data: return

        intents = [row['intent'] for row in data]
        pdrs = [float(row['pdr']) * 100 for row in data]
        priorities = [int(row['priority']) for row in data]

        # Color by priority: higher priority = darker shade
        import matplotlib.cm as cm
        norm_priorities = [p / max(priorities) for p in priorities]
        colors = [cm.RdYlGn(1.0 - np) for np in norm_priorities]

        plt.figure(figsize=(14, 7))
        bars = plt.bar(intents, pdrs, color=colors)

        for bar, prio in zip(bars, priorities):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                     f'P{prio}', ha='center', va='bottom', fontsize=8, fontweight='bold')

        plt.title('Intent-wise Packet Delivery Ratio (colored by priority)')
        plt.xlabel('Mission Intent')
        plt.ylabel('Packet Delivery Ratio (%)')
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, '13_intent_pdr.png'), dpi=300)
        plt.close()

    def plot_intent_qos(self):
        """Intent-wise QoS Satisfaction comparison."""
        data = self.read_csv("intent_comparison.csv")
        if not data: return

        intents = [row['intent'] for row in data]
        qos = [float(row['qos_satisfaction']) * 100 for row in data]
        mission_completion = [float(row['mission_completion_ratio']) * 100 for row in data]

        import numpy as np
        x = np.arange(len(intents))
        width = 0.35

        plt.figure(figsize=(14, 7))
        plt.bar(x - width/2, qos, width, label='QoS Satisfaction', color='teal')
        plt.bar(x + width/2, mission_completion, width, label='Mission Completion', color='darkorange')

        plt.title('Intent-wise QoS Satisfaction & Mission Completion')
        plt.xlabel('Mission Intent')
        plt.ylabel('Percentage (%)')
        plt.xticks(x, intents, rotation=45, ha='right')
        plt.legend()
        plt.grid(axis='y')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, '14_intent_qos.png'), dpi=300)
        plt.close()

    def plot_scalability_comparison(self):
        """Scalability: PDR & Latency across constellation sizes and traffic loads."""
        data = self.read_csv("scalability_comparison.csv")
        if not data: return

        import numpy as np

        # Group by constellation size
        constellations = {}
        for row in data:
            size = row['constellation_size']
            if size not in constellations:
                constellations[size] = {'loads': [], 'pdrs': [], 'latencies': []}
            constellations[size]['loads'].append(int(row['traffic_load']))
            constellations[size]['pdrs'].append(float(row['packet_delivery_ratio']))
            constellations[size]['latencies'].append(float(row['average_latency_ms']))

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        markers = ['o', 's', '^', 'D']
        colors = ['steelblue', 'coral', 'seagreen', 'mediumpurple']

        for i, (size, vals) in enumerate(constellations.items()):
            ax1.plot(vals['loads'], vals['pdrs'], marker=markers[i % 4],
                     color=colors[i % 4], label=f'{size}', linewidth=2)
            ax2.plot(vals['loads'], vals['latencies'], marker=markers[i % 4],
                     color=colors[i % 4], label=f'{size}', linewidth=2)

        ax1.set_title('PDR vs Traffic Load by Constellation Size')
        ax1.set_xlabel('Traffic Load (Packets/Batch)')
        ax1.set_ylabel('Packet Delivery Ratio (%)')
        ax1.legend(title='Constellation')
        ax1.grid(True)

        ax2.set_title('Latency vs Traffic Load by Constellation Size')
        ax2.set_xlabel('Traffic Load (Packets/Batch)')
        ax2.set_ylabel('Average Latency (ms)')
        ax2.legend(title='Constellation')
        ax2.grid(True)

        plt.suptitle('Scalability Analysis Across Constellation Sizes', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, '15_scalability_comparison.png'), dpi=300)
        plt.close()

    def plot_evaluation_radar(self):
        """Radar chart of overall system evaluation metrics."""
        data = self.read_csv("evaluation_report.csv")
        if not data: return

        import numpy as np

        # Select key metrics for radar
        metric_map = {
            'Packet Delivery Ratio (%)': 'PDR',
            'Mission Completion Ratio (%)': 'Mission\nCompletion',
            'Intent Prediction Accuracy (%)': 'Intent\nPrediction',
            'Resource Allocation Efficiency (%)': 'Resource\nAllocation',
            'Service Continuity (%)': 'Service\nContinuity',
            'Dynamic Resilience (%)': 'Dynamic\nResilience',
            'Swarm Coordination Efficiency (%)': 'Swarm\nCoordination',
            'Routing Stability (%)': 'Routing\nStability',
            'Bandwidth Utilization (%)': 'Bandwidth\nUtilization',
        }

        labels = []
        values = []
        for row in data:
            metric = row['metric']
            if metric in metric_map:
                labels.append(metric_map[metric])
                values.append(float(row['value']))

        if not values: return

        N = len(labels)
        angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
        values_plot = values + [values[0]]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        ax.fill(angles, values_plot, alpha=0.25, color='steelblue')
        ax.plot(angles, values_plot, 'o-', linewidth=2, color='steelblue')

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=9)
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=8)
        ax.set_title('Overall System Evaluation Metrics', y=1.08, fontsize=14, fontweight='bold')

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, '16_evaluation_radar.png'), dpi=300)
        plt.close()

    def plot_ablation_latency(self):
        """Ablation study: Latency comparison across model variants."""
        data = self.read_csv("ablation.csv")
        if not data: return

        import numpy as np
        model_data_normal = {}
        model_data_failure = {}
        
        for row in data:
            variant = row['model_variant']
            if variant not in model_data_normal:
                model_data_normal[variant] = []
                model_data_failure[variant] = []
            if row['phase'] == 'Normal':
                model_data_normal[variant].append(float(row['avg_latency_ms']))
            elif row['phase'] == 'Failure':
                model_data_failure[variant].append(float(row['avg_latency_ms']))
                
        models = list(model_data_normal.keys())
        lat_normal = [np.mean(model_data_normal[m]) for m in models]
        lat_failure = [np.mean(model_data_failure[m]) for m in models]

        x = np.arange(len(models))
        width = 0.35

        plt.figure(figsize=(12, 6))
        bars1 = plt.bar(x - width/2, lat_normal, width, label='Normal', color='steelblue')
        bars2 = plt.bar(x + width/2, lat_failure, width, label='Post-Failure', color='coral')

        for bar in bars1:
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                     f'{bar.get_height():.1f}', ha='center', va='bottom', fontsize=8)
        for bar in bars2:
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                     f'{bar.get_height():.1f}', ha='center', va='bottom', fontsize=8)

        plt.title('Ablation Study: Component Impact on Latency')
        plt.ylabel('Average Latency (ms)')
        plt.xticks(x, models, rotation=30, ha='right')
        plt.legend()
        plt.grid(axis='y')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, '17_ablation_latency.png'), dpi=300)
        plt.close()

    def generate_all(self):
        print("Generating research plots...")
        self.plot_latency_vs_load()
        self.plot_throughput_vs_load()
        self.plot_pdr_vs_failures()
        self.plot_recovery_vs_failures()
        self.plot_convergence()
        self.plot_intent_comparison()
        self.plot_scalability()
        self.plot_baseline_comparison()
        self.plot_ablation_study()
        self.plot_baseline_latency()
        self.plot_baseline_throughput()
        self.plot_baseline_qos()
        self.plot_intent_pdr()
        self.plot_intent_qos()
        self.plot_scalability_comparison()
        self.plot_evaluation_radar()
        self.plot_ablation_latency()
        print("All 17 plots saved to results/figures/")

if __name__ == "__main__":
    plotter = Plotter()
    plotter.generate_all()

