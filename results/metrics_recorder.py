import csv
import os

class MetricsRecorder:
    def __init__(self, output_dir: str = "results"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def record_metrics(self, experiment_name: str, metrics_list: list):
        """
        Writes a list of metrics dictionaries to a CSV file.
        Each dictionary corresponds to a row.
        """
        if not metrics_list:
            return
            
        filename = os.path.join(self.output_dir, f"{experiment_name}.csv")
        
        # Get all keys to use as headers
        headers = []
        for metrics in metrics_list:
            for key in metrics.keys():
                if key not in headers and key != "paths": # Exclude raw paths from CSV
                    headers.append(key)
                    
        with open(filename, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            for metrics in metrics_list:
                # Filter out 'paths' and other non-scalar types before writing
                row = {k: v for k, v in metrics.items() if k in headers}
                writer.writerow(row)
                
        print(f"Metrics saved to {filename}")
