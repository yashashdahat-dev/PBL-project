import matplotlib.pyplot as plt
import csv
import os
import collections
import numpy as np

class IntentPlotter:
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
        plt.figure(figsize=(10, 6))
        
        grouped = collections.defaultdict(lambda: {'loads': [], 'latencies': []})
        for row in data:
            if 'intent' in row:
                grouped[row['intent']]['loads'].append(float(row['traffic_load']))
                grouped[row['intent']]['latencies'].append(float(row['avg_latency_ms']))
                
        markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h']
        for i, (intent, vals) in enumerate(grouped.items()):
            plt.plot(vals['loads'], vals['latencies'], marker=markers[i%len(markers)], linestyle='-', label=intent)
            
        plt.title('Average Latency vs Traffic Load (Intent-Aware)')
        plt.xlabel('Traffic Load (Packets/Batch)')
        plt.ylabel('Average Latency (ms)')
        plt.legend()
        plt.grid(True)
        plt.savefig(os.path.join(self.output_dir, '1_latency_vs_load.png'), dpi=300)
        plt.close()

    def plot_throughput_vs_load(self):
        data = self.read_csv("congestion.csv")
        if not data: return
        plt.figure(figsize=(10, 6))
        
        grouped = collections.defaultdict(lambda: {'loads': [], 'tps': []})
        for row in data:
            if 'intent' in row:
                grouped[row['intent']]['loads'].append(float(row['traffic_load']))
                grouped[row['intent']]['tps'].append(float(row['avg_throughput_kbps']))
                
        markers = ['o', 's', '^', 'D']
        for i, (intent, vals) in enumerate(grouped.items()):
            plt.plot(vals['loads'], vals['tps'], marker=markers[i%len(markers)], linestyle='-', label=intent)
            
        plt.title('Throughput vs Traffic Load (Intent-Aware)')
        plt.xlabel('Traffic Load (Packets/Batch)')
        plt.ylabel('Average Throughput (kbps)')
        plt.legend()
        plt.grid(True)
        plt.savefig(os.path.join(self.output_dir, '2_throughput_vs_load.png'), dpi=300)
        plt.close()

    def plot_pdr_vs_failures(self):
        data = self.read_csv("link_failure.csv")
        if not data: return
        plt.figure(figsize=(10, 6))
        
        grouped = collections.defaultdict(lambda: {'fails': [], 'pdrs': []})
        for row in data:
            if 'intent' in row:
                grouped[row['intent']]['fails'].append(float(row['failures_injected']))
                grouped[row['intent']]['pdrs'].append(float(row['pdr']) * 100)
                
        markers = ['o', 's', '^', 'D']
        for i, (intent, vals) in enumerate(grouped.items()):
            plt.plot(vals['fails'], vals['pdrs'], marker=markers[i%len(markers)], linestyle='-', label=intent)
            
        plt.title('Packet Delivery Ratio vs Number of Failures (Intent-Aware)')
        plt.xlabel('Number of Injected ISL Failures')
        plt.ylabel('Packet Delivery Ratio (%)')
        plt.legend()
        plt.grid(True)
        plt.savefig(os.path.join(self.output_dir, '3_pdr_vs_failures.png'), dpi=300)
        plt.close()

    def plot_recovery_vs_failures(self):
        data = self.read_csv("link_failure.csv")
        if not data: return
        plt.figure(figsize=(10, 6))
        
        intents = []
        failures_list = []
        for row in data:
            if 'intent' in row:
                f = float(row['failures_injected'])
                i = row['intent']
                if f not in failures_list: failures_list.append(f)
                if i not in intents: intents.append(i)
                
        failures_list.sort()
        x = np.arange(len(failures_list))
        width = 0.8 / max(1, len(intents))
        
        for idx, intent in enumerate(intents):
            recovs = []
            for f in failures_list:
                val = 0
                for row in data:
                    if row.get('intent') == intent and float(row['failures_injected']) == f:
                        v = row['recovery_time_packets']
                        val = float(v) if v != 'inf' else 50
                        break
                recovs.append(val)
            plt.bar(x + idx*width - 0.4 + width/2, recovs, width, label=intent)
        
        plt.xticks(x, failures_list)
        plt.legend()
        plt.title('Recovery Time vs Number of Failed Links (Intent-Aware)')
        plt.xlabel('Number of Failed Links')
        plt.ylabel('Recovery Time (Packets)')
        plt.grid(axis='y')
        plt.savefig(os.path.join(self.output_dir, '4_recovery_vs_failures.png'), dpi=300)
        plt.close()

    def plot_convergence(self):
        data = self.read_csv("convergence.csv")
        if not data: return
        plt.figure(figsize=(10, 6))
        
        grouped = collections.defaultdict(lambda: {'pkts': [], 'pdrs': []})
        for row in data:
            if 'intent' in row:
                grouped[row['intent']]['pkts'].append(float(row['packets_processed']))
                grouped[row['intent']]['pdrs'].append(float(row['pdr']) * 100)
                
        markers = ['o', 's', '^', 'D']
        for i, (intent, vals) in enumerate(grouped.items()):
            plt.plot(vals['pkts'], vals['pdrs'], marker=markers[i%len(markers)], linestyle='-', label=intent)
            
        plt.title('Learning Convergence Curve (Intent-Aware)')
        plt.xlabel('Packets Processed')
        plt.ylabel('Packet Delivery Ratio (%)')
        plt.legend()
        plt.grid(True)
        plt.savefig(os.path.join(self.output_dir, '5_learning_convergence.png'), dpi=300)
        plt.close()

    def plot_intent_comparison(self):
        # 6 is already intent-aware intrinsically
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
        plt.figure(figsize=(10, 6))
        
        grouped = collections.defaultdict(lambda: {'sats': [], 'times': []})
        for row in data:
            if 'intent' in row:
                grouped[row['intent']]['sats'].append(str(row['total_satellites']))
                grouped[row['intent']]['times'].append(float(row['computation_time_seconds']))
                
        markers = ['o', 's', '^', 'D']
        for i, (intent, vals) in enumerate(grouped.items()):
            plt.plot(vals['sats'], vals['times'], marker=markers[i%len(markers)], linestyle='-', label=intent)
            
        plt.title('Scalability: Network Size vs Computation Time (Intent-Aware)')
        plt.xlabel('Number of Satellites')
        plt.ylabel('Computation Time (seconds)')
        plt.legend()
        plt.grid(True)
        plt.savefig(os.path.join(self.output_dir, '7_scalability.png'), dpi=300)
        plt.close()

    def plot_baseline_comparison(self):
        data = self.read_csv("baseline_comparison.csv")
        if not data: return
        
        algorithms = []
        intents = []
        for row in data:
            if row.get('algorithm') and row['algorithm'] not in algorithms: algorithms.append(row['algorithm'])
            if row.get('intent') and row['intent'] not in intents: intents.append(row['intent'])
            
        plt.figure(figsize=(14, 7))
        x = np.arange(len(algorithms))
        width = 0.8 / max(1, len(intents))
        
        for idx, intent in enumerate(intents):
            pdr_train = []
            for algo in algorithms:
                v = [float(r['pdr'])*100 for r in data if r.get('algorithm')==algo and r.get('intent')==intent and r.get('phase')=='Training']
                pdr_train.append(v[0] if v else 0)
            plt.bar(x + idx*width - 0.4 + width/2, pdr_train, width, label=intent)
            
        plt.title('Routing Performance Comparison (Intent-Aware, Training Phase)')
        plt.ylabel('Packet Delivery Ratio (%)')
        plt.xticks(x, algorithms)
        plt.legend(title='Mission Intent')
        plt.grid(axis='y')
        plt.savefig(os.path.join(self.output_dir, '8_baseline_comparison.png'), dpi=300)
        plt.close()

    def plot_ablation_study(self):
        data = self.read_csv("ablation.csv")
        if not data: return
        
        models = []
        intents = []
        for row in data:
            if row.get('model_variant') and row['model_variant'] not in models: models.append(row['model_variant'])
            if row.get('intent') and row['intent'] not in intents: intents.append(row['intent'])
            
        plt.figure(figsize=(14, 7))
        x = np.arange(len(models))
        width = 0.8 / max(1, len(intents))
        
        for idx, intent in enumerate(intents):
            pdr_normal = []
            for m in models:
                v = [float(r['pdr'])*100 for r in data if r.get('model_variant')==m and r.get('intent')==intent and r.get('phase')=='Normal']
                pdr_normal.append(v[0] if v else 0)
            plt.bar(x + idx*width - 0.4 + width/2, pdr_normal, width, label=intent)
            
        plt.title('Ablation Study: Component Impact on PDR (Intent-Aware, Normal Phase)')
        plt.ylabel('Packet Delivery Ratio (%)')
        plt.xticks(x, models, rotation=30, ha='right')
        plt.legend(title='Mission Intent')
        plt.grid(axis='y')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, '9_ablation_study.png'), dpi=300)
        plt.close()

    def generate_all(self):
        print("Generating intent-aware research plots (1-9)...")
        self.plot_latency_vs_load()
        self.plot_throughput_vs_load()
        self.plot_pdr_vs_failures()
        self.plot_recovery_vs_failures()
        self.plot_convergence()
        self.plot_intent_comparison()
        self.plot_scalability()
        self.plot_baseline_comparison()
        self.plot_ablation_study()
        print("Completed.")

if __name__ == "__main__":
    plotter = IntentPlotter()
    plotter.generate_all()
