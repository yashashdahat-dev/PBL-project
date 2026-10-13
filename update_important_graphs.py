"""
update_important_graphs.py
==========================
Updates d:/ff/evaluation_graphs with the new research-grade, verified graphs
from evaluation_graphs_new/figures_png/, exactly matching the folder structure
and filenames of the curated important graphs collection.
"""

import os
import shutil

src_dir = r"d:\ff\evaluation_graphs_new\figures_png"
dest_root = r"d:\ff\evaluation_graphs"

# Mapping: (Folder_Name, Source_Figure_Num, Dest_Filename)
mappings = [
    # Communication Performance
    ("Communication_Performance", 1, "01_Satellites_vs_Throughput.png"),
    ("Communication_Performance", 2, "02_Satellites_vs_Latency.png"),
    ("Communication_Performance", 3, "03_Satellites_vs_PDR.png"),

    # Mission Performance
    ("Mission_Performance", 10, "10_Missions_vs_Completion.png"),
    ("Mission_Performance", 12, "12_Missions_vs_Intent_Accuracy.png"),
    ("Mission_Performance", 13, "13_Missions_vs_Priority_Preservation.png"),

    # Scalability
    ("Scalability", 19, "19_Mission_Density_vs_Throughput.png"),
    ("Scalability", 20, "20_Mission_Density_vs_Latency.png"),
    ("Scalability", 25, "25_Users_vs_Throughput.png"),

    # Convergence
    ("Convergence", 31, "31_Episodes_vs_Reward.png"),
    ("Convergence", 32, "32_Training_Episodes_vs_Mission_Success_Rate.png"),
    ("Convergence", 33, "33_Training_Episodes_vs_Convergence_Loss.png"),

    # Resource Allocation
    ("Resource_Allocation", 37, "37_Resource_vs_MissionType.png"),
    ("Resource_Allocation", 38, "38_Beam_Allocation_Efficiency_vs_Mission_Type.png"),
    ("Resource_Allocation", 39, "39_Gateway_Selection_Accuracy_vs_Mission_Type.png"),

    # Robustness
    ("Robustness", 43, "43_Failure_vs_Completion.png"),
    ("Robustness", 44, "Satellite_Failure_Rate_vs_Throughput.png"),  # or 44_
    ("Robustness", 44, "44_Satellite_Failure_Rate_vs_Throughput.png"),
    ("Robustness", 45, "45_Satellite_Failure_Rate_vs_Latency.png"),

    # Mission Specific
    ("Mission_Specific", 49, "49_Disaster_Mission_vs_Throughput.png"),
    ("Mission_Specific", 50, "50_Military_Mission_vs_Security_Satisfaction.png"),
    ("Mission_Specific", 51, "51_Remote_Healthcare_vs_Latency.png"),

    # AI Specific
    ("AI_Specific", 57, "57_Semantic_Encoding_Accuracy_vs_Mission_Success.png"),
    ("AI_Specific", 59, "59_Intent_Dissemination_Delay_vs_Mission_Completion.png"),
    ("AI_Specific", 61, "61_Mission_Intent_Vector_Size_vs_Computational_Complexity.png"),

    # Complexity
    ("Complexity", 63, "63_Number_of_Satellites_vs_Execution_Time.png"),
    ("Complexity", 64, "64_Number_of_Satellites_vs_Memory_Consumption.png"),
    ("Complexity", 65, "65_Number_of_Satellites_vs_Computational_Complexity.png"),

    # Statistical
    ("Statistical", 68, "68_Average_Performance_Comparison.png"),
    ("Statistical", 69, "69_Percentage_Improvement.png"),
    ("Statistical", 70, "70_Radar_Chart_Comparison.png"),
    ("Statistical", 71, "71_Box_Plot_Variability.png"),
    ("Statistical", 72, "72_CDF_Latency.png"),
    ("Statistical", 73, "73_CDF_Throughput.png")
]

src_files = os.listdir(src_dir)

updated_count = 0
for folder_name, fig_num, dest_name in mappings:
    target_folder = os.path.join(dest_root, folder_name)
    os.makedirs(target_folder, exist_ok=True)

    # Find the corresponding source file
    prefix = f"figure_{fig_num:02d}_"
    matched_src = [f for f in src_files if f.startswith(prefix) and f.endswith(".png")]
    if not matched_src:
        print(f"Warning: No match found for figure {fig_num}")
        continue

    src_file = os.path.join(src_dir, matched_src[0])
    dest_file = os.path.join(target_folder, dest_name)
    shutil.copy2(src_file, dest_file)
    updated_count += 1
    print(f"  [UPDATED] {folder_name}/{dest_name} <- {matched_src[0]}")

print("=" * 70)
print(f"Successfully updated {updated_count} important graphs in: {dest_root}")
print("=" * 70)
