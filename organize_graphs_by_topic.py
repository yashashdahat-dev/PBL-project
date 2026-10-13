"""
organize_graphs_by_topic.py
===========================
Creates a clean, dedicated folder structure:
d:/ff/evaluation_graphs_by_topic/
  1. Communication Performance/
  2. Mission Performance/
  3. Scalability Analysis/
  4. Convergence Traces/
  5. Resource Allocation/
  6. Robustness and Fault Tolerance/
  7. Mission-Specific Benchmarks/
  8. AI and Swarm Dynamics/
  9. Complexity Analysis/
  10. Statistical Evaluation/

Copies all 77 publication-grade high-res figures into their respective topic folders.
Only image graph files (.png) are stored in each topic folder.
"""

import os
import shutil

src_png_dir = r"d:\ff\evaluation_graphs_new\figures_png"
dest_root = r"d:\ff\evaluation_graphs_by_topic"

topics = [
    ("1. Communication Performance", 1, 9),
    ("2. Mission Performance", 10, 18),
    ("3. Scalability Analysis", 19, 30),
    ("4. Convergence Traces", 31, 36),
    ("5. Resource Allocation", 37, 42),
    ("6. Robustness and Fault Tolerance", 43, 48),
    ("7. Mission-Specific Benchmarks", 49, 56),
    ("8. AI and Swarm Dynamics", 57, 62),
    ("9. Complexity Analysis", 63, 67),
    ("10. Statistical Evaluation", 68, 77)
]

os.makedirs(dest_root, exist_ok=True)

png_files = sorted([f for f in os.listdir(src_png_dir) if f.endswith(".png")])

copied_count = 0

for folder_name, start_num, end_num in topics:
    topic_dir = os.path.join(dest_root, folder_name)
    os.makedirs(topic_dir, exist_ok=True)

    topic_pngs = []
    for f in png_files:
        # File format: figure_01_throughput_vs_satellites.png
        prefix = f.split("_")[1]
        if prefix.isdigit():
            num = int(prefix)
            if start_num <= num <= end_num:
                topic_pngs.append(f)

    for f in topic_pngs:
        src = os.path.join(src_png_dir, f)
        dest = os.path.join(topic_dir, f)
        shutil.copy2(src, dest)
        copied_count += 1
        print(f"  [OK] {folder_name} <- {f}")

print("=" * 70)
print(f"Successfully organized {copied_count} graphs into {len(topics)} topic folders!")
print(f"Destination: {dest_root}")
print("=" * 70)
