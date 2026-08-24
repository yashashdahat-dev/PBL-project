# pyrefly: ignore [missing-import]
import networkx as nx
# pyrefly: ignore [missing-import]
import matplotlib.pyplot as plt
from typing import List, Optional
from network.isl_state import ISLState

class NetworkVisualizer:
    def __init__(self, topology):
        self.topology = topology

    def draw_snapshot(self, active_path: Optional[List[str]] = None, title: str = ""):
        """Renders 2D grid snapshot of LEO constellation topology and active routes."""

        G = nx.Graph()
        pos = {}
        node_colors = []
        
        # 1. Add nodes and 2D grid positions based on orbital plane and index
        for sat_id, sat_node in self.topology.nodes.items():
            G.add_node(sat_id)
            # Position: plane_id on Y axis, sat_index on X axis
            pos[sat_id] = (sat_node.sat_index, -sat_node.plane_id)
            
            if active_path and sat_id == active_path[0]:
                node_colors.append('#ffeb3b')  # Yellow for Source
            elif active_path and sat_id == active_path[-1]:
                node_colors.append('#ff9800')  # Orange for Destination
            elif active_path and sat_id in active_path:
                node_colors.append('#00e676')  # Bright green for active route nodes
            else:
                node_colors.append('#29b6f6')  # Cyan for standard constellation nodes

        # 2. Add edges for ISLs
        edge_colors = []
        edge_styles = []
        edge_widths = []
        path_edges = set()
        
        if active_path and len(active_path) > 1:
            for i in range(len(active_path) - 1):
                path_edges.add((active_path[i], active_path[i+1]))
                path_edges.add((active_path[i+1], active_path[i]))

        added_edges = set()
        for sat_id, sat_node in self.topology.nodes.items():
            for neighbor_id, link in sat_node.isl_interfaces.items():
                edge_pair = tuple(sorted([sat_id, neighbor_id]))
                if edge_pair in added_edges:
                    continue
                added_edges.add(edge_pair)
                G.add_edge(sat_id, neighbor_id)

                # Check if this edge is part of the active path
                if (sat_id, neighbor_id) in path_edges:
                    edge_colors.append('#00e676')
                    edge_styles.append('solid')
                    edge_widths.append(3.5)
                elif link.state == ISLState.FAILED:
                    edge_colors.append('#ff1744')
                    edge_styles.append('dashed')
                    edge_widths.append(2.0)
                else:
                    edge_colors.append('#b0bec5')
                    edge_styles.append('solid')
                    edge_widths.append(1.0)

        # 3. Draw Plot
        plt.figure(figsize=(10, 6))
        plt.clf()
        
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=700)
        nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold', font_color='black')
        
        for edge, color, style, width in zip(G.edges(), edge_colors, edge_styles, edge_widths):
            nx.draw_networkx_edges(
                G, pos, edgelist=[edge],
                edge_color=color, style=style, width=width
            )

        plt.title(title if title else "LEO Swarm Constellation Topology", fontsize=12, fontweight='bold')
        plt.xlabel("Satellite Index (Intra-plane Orbit)")
        plt.ylabel("Orbital Plane Index")
        plt.grid(True, linestyle=':', alpha=0.5)
        plt.axis('on')
        plt.tight_layout()
        
        # Save to file instead of showing interactively
        import os
        import re
        output_dir = "results/figures"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        filename = f"{title.replace(' ', '_').replace('>', '').replace('-', '').lower()}_snapshot.png"
        filename = re.sub(r'[^a-zA-Z0-9_.]', '', filename)
        if not filename.endswith('.png'):
            filename += '.png'
            
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"Saved snapshot to {filepath}")
        plt.close()

    def draw_3d_snapshot(self, active_path: Optional[List[str]] = None, title: str = ""):
        """Renders a 3D snapshot of the constellation orbiting Earth."""
        import numpy as np
        
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # 1. Draw Earth
        u = np.linspace(0, 2 * np.pi, 100)
        v = np.linspace(0, np.pi, 100)
        x_earth = 6371 * np.outer(np.cos(u), np.sin(v))
        y_earth = 6371 * np.outer(np.sin(u), np.sin(v))
        z_earth = 6371 * np.outer(np.ones(np.size(u)), np.cos(v))
        
        ax.plot_surface(x_earth, y_earth, z_earth, color='royalblue', alpha=0.3, 
                        linewidth=0, antialiased=False)
        
        # 2. Calculate Satellite Positions
        orbit_altitude = 500  # km
        radius = 6371 + orbit_altitude
        
        num_planes = max([sat.plane_id for sat in self.topology.nodes.values()]) + 1
        sats_per_plane = max([sat.sat_index for sat in self.topology.nodes.values()]) + 1
        
        pos_3d = {}
        for sat_id, sat_node in self.topology.nodes.items():
            # Longitude based on plane
            lon = (2 * np.pi / num_planes) * sat_node.plane_id
            # Latitude/Anomaly based on index in plane (inclination approximated)
            lat = (2 * np.pi / sats_per_plane) * sat_node.sat_index
            
            # Convert to Cartesian (assuming polar orbits for visualization)
            x = radius * np.cos(lat) * np.cos(lon)
            y = radius * np.cos(lat) * np.sin(lon)
            z = radius * np.sin(lat)
            
            pos_3d[sat_id] = (x, y, z)
            
        # 3. Draw Edges
        path_edges = set()
        if active_path and len(active_path) > 1:
            for i in range(len(active_path) - 1):
                path_edges.add((active_path[i], active_path[i+1]))
                path_edges.add((active_path[i+1], active_path[i]))
                
        added_edges = set()
        for sat_id, sat_node in self.topology.nodes.items():
            for neighbor_id, link in sat_node.isl_interfaces.items():
                edge_pair = tuple(sorted([sat_id, neighbor_id]))
                if edge_pair in added_edges:
                    continue
                added_edges.add(edge_pair)
                
                x_edge = [pos_3d[sat_id][0], pos_3d[neighbor_id][0]]
                y_edge = [pos_3d[sat_id][1], pos_3d[neighbor_id][1]]
                z_edge = [pos_3d[sat_id][2], pos_3d[neighbor_id][2]]
                
                if (sat_id, neighbor_id) in path_edges:
                    ax.plot(x_edge, y_edge, z_edge, color='#00e676', linewidth=3.5, zorder=5)
                elif link.state == ISLState.FAILED:
                    ax.plot(x_edge, y_edge, z_edge, color='#ff1744', linewidth=2.0, linestyle='dashed', zorder=4)
                else:
                    ax.plot(x_edge, y_edge, z_edge, color='#b0bec5', linewidth=1.0, alpha=0.5, zorder=3)
                    
        # 4. Draw Nodes
        for sat_id, (x, y, z) in pos_3d.items():
            color = '#29b6f6'
            size = 30
            if active_path and sat_id == active_path[0]:
                color = '#ffeb3b'
                size = 100
            elif active_path and sat_id == active_path[-1]:
                color = '#ff9800'
                size = 100
            elif active_path and sat_id in active_path:
                color = '#00e676'
                size = 60
                
            ax.scatter(x, y, z, color=color, s=size, edgecolors='black', zorder=6)
            
        ax.set_title(title if title else "LEO 3D Constellation", fontsize=14, fontweight='bold', pad=20)
        ax.set_axis_off()
        
        # Save to file
        import os
        import re
        output_dir = "results/figures"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        filename = f"3d_{title.replace(' ', '_').replace('>', '').replace('-', '').lower()}_snapshot.png"
        filename = re.sub(r'[^a-zA-Z0-9_.]', '', filename)
        if not filename.endswith('.png'):
            filename += '.png'
            
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='black')
        print(f"Saved 3D snapshot to {filepath}")
        plt.close()
