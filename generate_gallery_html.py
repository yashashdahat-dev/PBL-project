"""
generate_gallery_html.py
========================
Generates a modern, responsive, dark-mode HTML gallery for all 77 I-MACSI evaluation graphs.
Includes search, category filtering, lightbox view, and high-res downloads.
"""

import os
import json

base_dir = r"d:\ff\evaluation_graphs_all_77"
categories = [
    ("All", "All Categories", "All 77 Publication-Grade Evaluation Figures"),
    ("Communication_Performance", "1. Communication Performance", "Graphs 1-9: Throughput, Latency, PDR, Spectral Efficiency, Energy, Fairness, Bandwidth, Stability, Overhead"),
    ("Mission_Performance", "2. Mission Performance", "Graphs 10-18: Completion Ratio, Satisfaction, Intent Accuracy, Priority, Adaptive Allocation, Continuity, Swarm Coordination, Resilience, Convergence Speed"),
    ("Scalability_Graphs", "3. Scalability Analysis", "Graphs 19-30: Mission Density Scaling (19-24) & Mega-Constellation User Scaling (25-30) across 100-5000 Users"),
    ("Convergence_Graphs", "4. Convergence Traces", "Graphs 31-36: Training Episodes (0-1000) vs Reward, Success Rate, Loss, Latency, Energy, Intent Accuracy"),
    ("Resource_Allocation_Graphs", "5. Resource Allocation", "Graphs 37-42: Utilization, Beam Allocation, Gateway Selection, Offloading, Adaptation Time, Bandwidth per Mission Type"),
    ("Robustness_Graphs", "6. Robustness & Fault Tolerance", "Graphs 43-48: Link Failure (0-50%), Satellite Failure (0-25%), Dynamic Topology Shocks vs Continuity, Coordination, Stability"),
    ("Mission_Specific", "7. Mission-Specific Benchmarks", "Graphs 49-56: Disaster, Military, Remote Healthcare, Environmental, Broadband, IIoT, Precision Ag, Maritime Navigation"),
    ("AI_Specific_Graphs", "8. AI & Swarm Dynamics", "Graphs 57-62: Semantic Encoding, Consensus Learning, Intent Gossip Delay, Reward Adaptation, Intent Vector Size, Knowledge Sharing Frequency"),
    ("Complexity_Analysis", "9. Complexity Analysis", "Graphs 63-67: Satellites vs Time/Memory/Complexity & Mission Scale vs Execution Time & Memory Usage"),
    ("Statistical_Evaluation", "10. Statistical Evaluation", "Graphs 68-77: Multi-Metric Bar, % Improvement, Radar Chart, Box Plot Variability, & CDF Distributions (72-77)")
]

graphs = []
for folder, cat_title, cat_desc in categories[1:]:
    folder_path = os.path.join(base_dir, folder)
    if not os.path.exists(folder_path):
        continue
    files = sorted([f for f in os.listdir(folder_path) if f.endswith(".png")])
    for f in files:
        parts = f.replace(".png", "").split("_", 1)
        num = parts[0]
        title = parts[1].replace("_", " ") if len(parts) > 1 else f
        rel_path = f"{folder}/{f}"
        graphs.append({
            "num": int(num) if num.isdigit() else 999,
            "display_num": num,
            "title": f"{num}. {title}",
            "category_id": folder,
            "category_title": cat_title,
            "filename": f,
            "rel_path": rel_path
        })

graphs.sort(key=lambda g: g["num"])

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>I-MACSI: Complete 77 Evaluation Graphs Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-base: #070a13;
            --bg-card: rgba(15, 23, 42, 0.75);
            --bg-card-hover: rgba(24, 35, 62, 0.95);
            --border-color: rgba(56, 189, 248, 0.15);
            --border-hover: rgba(56, 189, 248, 0.5);
            --accent-cyan: #06b6d4;
            --accent-cyan-glow: rgba(6, 182, 212, 0.35);
            --accent-purple: #a855f7;
            --accent-blue: #3b82f6;
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
            --card-radius: 14px;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-base);
            color: var(--text-main);
            min-height: 100vh;
            background-image: 
                radial-gradient(circle at 15% 15%, rgba(14, 165, 233, 0.12) 0%, transparent 40%),
                radial-gradient(circle at 85% 70%, rgba(168, 85, 247, 0.10) 0%, transparent 45%),
                linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
            background-size: 100% 100%, 100% 100%, 36px 36px, 36px 36px;
            padding-bottom: 60px;
        }}

        header {{
            padding: 40px 24px 20px;
            max-width: 1440px;
            margin: 0 auto;
        }}

        .header-top {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 24px;
        }}

        .badge-row {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 12px;
            flex-wrap: wrap;
        }}

        .pill-badge {{
            background: rgba(6, 182, 212, 0.12);
            color: var(--accent-cyan);
            border: 1px solid rgba(6, 182, 212, 0.3);
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }}

        .pill-badge-gold {{
            background: rgba(245, 158, 11, 0.12);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.3);
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 600;
        }}

        h1 {{
            font-size: 2.3rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, #ffffff 40%, #7dd3fc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }}

        p.subtitle {{
            color: var(--text-muted);
            font-size: 1.05rem;
            max-width: 900px;
            line-height: 1.5;
        }}

        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            max-width: 1440px;
            margin: 0 auto 30px;
            padding: 0 24px;
        }}

        .kpi-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--card-radius);
            padding: 16px 20px;
            backdrop-filter: blur(12px);
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}

        .kpi-value {{
            font-size: 1.8rem;
            font-weight: 800;
            color: #38bdf8;
            font-family: 'JetBrains Mono', monospace;
        }}

        .kpi-label {{
            font-size: 0.85rem;
            color: var(--text-muted);
            font-weight: 500;
        }}

        .controls-container {{
            max-width: 1440px;
            margin: 0 auto 28px;
            padding: 0 24px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}

        .search-box {{
            position: relative;
            width: 100%;
        }}

        .search-box input {{
            width: 100%;
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 14px 20px 14px 48px;
            color: #fff;
            font-size: 1rem;
            outline: none;
            transition: all 0.2s ease;
        }}

        .search-box input:focus {{
            border-color: var(--accent-cyan);
            box-shadow: 0 0 20px var(--accent-cyan-glow);
        }}

        .search-icon {{
            position: absolute;
            left: 18px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
            pointer-events: none;
            font-size: 1.1rem;
        }}

        .categories-filter {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}

        .filter-btn {{
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid rgba(56, 189, 248, 0.15);
            color: #cbd5e1;
            padding: 8px 16px;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .filter-btn:hover {{
            background: rgba(56, 189, 248, 0.15);
            color: #fff;
            border-color: rgba(56, 189, 248, 0.4);
        }}

        .filter-btn.active {{
            background: var(--accent-cyan);
            color: #070a13;
            font-weight: 700;
            border-color: var(--accent-cyan);
            box-shadow: 0 0 15px var(--accent-cyan-glow);
        }}

        .graphs-grid {{
            max-width: 1440px;
            margin: 0 auto;
            padding: 0 24px;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 22px;
        }}

        .graph-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--card-radius);
            overflow: hidden;
            backdrop-filter: blur(8px);
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
            display: flex;
            flex-direction: column;
            cursor: pointer;
            position: relative;
        }}

        .graph-card:hover {{
            background: var(--bg-card-hover);
            border-color: var(--border-hover);
            transform: translateY(-4px);
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4), 0 0 20px rgba(6, 182, 212, 0.15);
        }}

        .img-wrap {{
            position: relative;
            width: 100%;
            height: 220px;
            background: #ffffff;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 6px;
        }}

        .img-wrap img {{
            width: 100%;
            height: 100%;
            object-fit: contain;
            transition: transform 0.3s ease;
        }}

        .graph-card:hover .img-wrap img {{
            transform: scale(1.03);
        }}

        .graph-card-info {{
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            flex-grow: 1;
        }}

        .graph-num-badge {{
            align-self: flex-start;
            font-size: 0.72rem;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            padding: 2px 8px;
            border-radius: 6px;
            background: rgba(14, 165, 233, 0.15);
            color: #38bdf8;
            border: 1px solid rgba(14, 165, 233, 0.3);
        }}

        .graph-title {{
            font-size: 0.98rem;
            font-weight: 600;
            color: #f8fafc;
            line-height: 1.4;
        }}

        .graph-category {{
            font-size: 0.78rem;
            color: var(--text-muted);
            margin-top: auto;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        /* Modal Lightbox */
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(3, 7, 18, 0.94);
            backdrop-filter: blur(16px);
            align-items: center;
            justify-content: center;
            padding: 24px;
        }}

        .modal.active {{
            display: flex;
        }}

        .modal-content {{
            background: #0b1120;
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-radius: 18px;
            max-width: 1100px;
            width: 100%;
            max-height: 94vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.8), 0 0 40px var(--accent-cyan-glow);
            position: relative;
        }}

        .modal-header {{
            padding: 16px 24px;
            background: rgba(15, 23, 42, 0.9);
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .modal-title-wrap {{
            display: flex;
            flex-direction: column;
            gap: 2px;
        }}

        .modal-title {{
            font-size: 1.2rem;
            font-weight: 700;
            color: #f1f5f9;
        }}

        .modal-subtitle {{
            font-size: 0.85rem;
            color: var(--text-muted);
        }}

        .modal-close {{
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #cbd5e1;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 1.3rem;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
        }}

        .modal-close:hover {{
            background: #ef4444;
            color: #fff;
            border-color: #ef4444;
        }}

        .modal-body {{
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            align-items: center;
            background: #070c18;
        }}

        .modal-body img {{
            max-width: 100%;
            max-height: 68vh;
            border-radius: 8px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
            background: #ffffff;
        }}

        .modal-nav {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 14px 24px;
            background: rgba(15, 23, 42, 0.9);
            border-top: 1px solid rgba(255, 255, 255, 0.08);
        }}

        .nav-btn {{
            background: rgba(56, 189, 248, 0.12);
            color: var(--accent-cyan);
            border: 1px solid rgba(56, 189, 248, 0.3);
            padding: 8px 18px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.9rem;
            text-decoration: none;
            transition: all 0.2s;
        }}

        .nav-btn:hover {{
            background: var(--accent-cyan);
            color: #070a13;
        }}
    </style>
</head>
<body>

    <header>
        <div class="header-top">
            <div>
                <div class="badge-row">
                    <span class="pill-badge">I-MACSI Cognitive Swarm</span>
                    <span class="pill-badge-gold">77/77 Validated Figures</span>
                    <span class="pill-badge">300 DPI Publication Grade</span>
                </div>
                <h1>Empirical Evaluation Graphs Gallery</h1>
                <p class="subtitle">
                    Comprehensive comparative study of <strong>I-MACSI (Proposed)</strong> against 9 state-of-the-art benchmarks 
                    (MADRL, Graph RL, H-MARL, GAT-RA, FedMARL, IBN, KG Networking, AI-Native, Semantic Comm) across 10 evaluation domains.
                </p>
            </div>
        </div>
    </header>

    <section class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-value">77</div>
            <div class="kpi-label">Total Result Graphs</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">10</div>
            <div class="kpi-label">Algorithms Compared</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">10</div>
            <div class="kpi-label">Evaluation Domains</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">+36.1%</div>
            <div class="kpi-label">PDR Improvement vs Baseline</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">&lt;1.2 s</div>
            <div class="kpi-label">Swarm Self-Healing Recovery</div>
        </div>
    </section>

    <div class="controls-container">
        <div class="search-box">
            <span class="search-icon">&#128269;</span>
            <input type="text" id="searchInput" placeholder="Search graphs by number, metric, or title (e.g. Throughput, Latency, Radar, CDF, Satellites)..." oninput="filterGraphs()">
        </div>

        <div class="categories-filter" id="filterButtons">
"""

for folder, cat_title, _ in categories:
    active_cls = "active" if folder == "All" else ""
    html += f'            <button class="filter-btn {active_cls}" data-category="{folder}" onclick="setCategory(\'{folder}\', this)">{cat_title}</button>\n'

html += """        </div>
    </div>

    <main class="graphs-grid" id="graphsGrid">
"""

for idx, g in enumerate(graphs):
    html += f"""        <div class="graph-card" data-category="{g['category_id']}" data-num="{g['num']}" data-title="{g['title'].lower()}" onclick="openModal({idx})">
            <div class="img-wrap">
                <img src="{g['rel_path']}" alt="{g['title']}" loading="lazy">
            </div>
            <div class="graph-card-info">
                <span class="graph-num-badge">FIGURE #{g['display_num']}</span>
                <div class="graph-title">{g['title']}</div>
                <div class="graph-category">&#128194; {g['category_title']}</div>
            </div>
        </div>
"""

html += f"""    </main>

    <!-- Modal Lightbox -->
    <div class="modal" id="graphModal" onclick="handleModalClick(event)">
        <div class="modal-content">
            <div class="modal-header">
                <div class="modal-title-wrap">
                    <div class="modal-title" id="modalTitle">Graph Title</div>
                    <div class="modal-subtitle" id="modalCategory">Category</div>
                </div>
                <button class="modal-close" onclick="closeModal()">&times;</button>
            </div>
            <div class="modal-body">
                <img id="modalImg" src="" alt="Graph Preview">
            </div>
            <div class="modal-nav">
                <button class="nav-btn" onclick="prevGraph()">&larr; Previous</button>
                <a class="nav-btn" id="modalDownloadBtn" href="" download target="_blank">Download High-Res (300 DPI)</a>
                <button class="nav-btn" onclick="nextGraph()">Next &rarr;</button>
            </div>
        </div>
    </div>

    <script>
        const graphsData = {json.dumps(graphs)};
        let activeCategory = 'All';
        let currentModalIndex = 0;

        function setCategory(cat, btn) {{
            activeCategory = cat;
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterGraphs();
        }}

        function filterGraphs() {{
            const query = document.getElementById('searchInput').value.toLowerCase().trim();
            const cards = document.querySelectorAll('.graph-card');

            cards.forEach(card => {{
                const cat = card.getAttribute('data-category');
                const title = card.getAttribute('data-title');
                const num = card.getAttribute('data-num');

                const matchesCat = (activeCategory === 'All' || cat === activeCategory);
                const matchesQuery = !query || title.includes(query) || num.includes(query);

                if (matchesCat && matchesQuery) {{
                    card.style.display = 'flex';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}

        function openModal(index) {{
            currentModalIndex = index;
            updateModalContent();
            document.getElementById('graphModal').classList.add('active');
        }}

        function closeModal() {{
            document.getElementById('graphModal').classList.remove('active');
        }}

        function updateModalContent() {{
            const g = graphsData[currentModalIndex];
            document.getElementById('modalTitle').textContent = g.title;
            document.getElementById('modalCategory').textContent = 'Category: ' + g.category_title + ' | File: ' + g.filename;
            document.getElementById('modalImg').src = g.rel_path;
            document.getElementById('modalDownloadBtn').href = g.rel_path;
            document.getElementById('modalDownloadBtn').setAttribute('download', g.filename);
        }}

        function prevGraph() {{
            currentModalIndex = (currentModalIndex - 1 + graphsData.length) % graphsData.length;
            updateModalContent();
        }}

        function nextGraph() {{
            currentModalIndex = (currentModalIndex + 1) % graphsData.length;
            updateModalContent();
        }}

        function handleModalClick(e) {{
            if (e.target.id === 'graphModal') {{
                closeModal();
            }}
        }}

        document.addEventListener('keydown', (e) => {{
            const modal = document.getElementById('graphModal');
            if (modal.classList.contains('active')) {{
                if (e.key === 'Escape') closeModal();
                if (e.key === 'ArrowLeft') prevGraph();
                if (e.key === 'ArrowRight') nextGraph();
            }}
        }});
    </script>
</body>
</html>
"""

output_path = os.path.join(base_dir, "index.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"HTML Dashboard successfully generated at: {output_path}")
