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
        
        plt.figure(figsize=(8, 5))
        plt.bar(intents, latencies, color=['blue', 'green', 'red'])
        plt.title('Intent-wise Performance Comparison (Latency)')
        plt.xlabel('Mission Intent')
        plt.ylabel('Average Latency (ms)')
        plt.grid(axis='y')
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
        
        algorithms = []
        pdr_train = []
        pdr_fail = []
        
        for row in data:
            algo = row['algorithm']
            if algo not in algorithms:
                algorithms.append(algo)
                
            if row['phase'] == 'Training':
                pdr_train.append(float(row['pdr']) * 100)
            elif row['phase'] == 'Failure':
                pdr_fail.append(float(row['pdr']) * 100)
                
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
        
        models = [row['model_variant'] for row in data]
        pdrs = [float(row['pdr']) * 100 for row in data]
        
        plt.figure(figsize=(8, 5))
        plt.bar(models, pdrs, color=['green', 'orange', 'red'])
        plt.title('Ablation Study: Component Impact on PDR')
        plt.ylabel('Packet Delivery Ratio (%)')
        plt.grid(axis='y')
        plt.savefig(os.path.join(self.output_dir, '9_ablation_study.png'), dpi=300)
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
        print("All plots saved to results/figures/")

if __name__ == "__main__":
    plotter = Plotter()
    plotter.generate_all()
