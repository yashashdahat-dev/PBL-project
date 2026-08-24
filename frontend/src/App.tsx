import React, { useEffect, useCallback, useState } from 'react';
import Scene from './components/Scene';
import HUDMetrics from './components/HUDMetrics';
import EventTicker from './components/EventTicker';
import CoordinatePanel from './components/CoordinatePanel';
import MissionPerformance from './components/MissionPerformance';
import { useSimulationStore, intentColors, intentLabels, type Intent } from './hooks/useSimulationStore';

const API = 'http://localhost:8000';
const WS  = 'ws://localhost:8001';

function App() {
  const source      = useSimulationStore(s => s.source);
  const destination = useSimulationStore(s => s.destination);
  const intent      = useSimulationStore(s => s.intent);
  const satellites  = useSimulationStore(s => s.satellites);
  const activeRoute = useSimulationStore(s => s.activeRoute);

  const setSource      = useSimulationStore(s => s.setSource);
  const setDestination = useSimulationStore(s => s.setDestination);
  const setIntent      = useSimulationStore(s => s.setIntent);
  const setActiveRoute = useSimulationStore(s => s.setActiveRoute);
  const setSatellites  = useSimulationStore(s => s.setSatellites);
  const setLinks       = useSimulationStore(s => s.setLinks);
  const addEvent       = useSimulationStore(s => s.addEvent);
  const addFailedLink  = useSimulationStore(s => s.addFailedLink);
  const removeFailedLink = useSimulationStore(s => s.removeFailedLink);

  const [backendOnline, setBackendOnline] = useState(false);
  const [isRouting, setIsRouting] = useState(false);
  const [isTraining, setIsTraining] = useState(false);
  const [trainingStats, setTrainingStats] = useState<{ pdr?: number; avg_latency_ms?: number; epsilon?: number } | null>(null);
  const [intentVector, setIntentVector] = useState<Record<string, number> | null>(null);

  // Fetch initial network state from backend
  useEffect(() => {
    fetch(`${API}/network`)
      .then(r => r.json())
      .then(data => {
        setBackendOnline(true);
        setSatellites(data.satellites || []);
        setLinks(data.links || []);
        const ids = (data.satellites || []).map((s: { id: string }) => s.id).sort();
        if (ids.length >= 2) {
          setSource(ids[0]);
          setDestination(ids[ids.length - 1]);
        }
        addEvent('Backend connected — 4×4 LEO constellation loaded', 'info');
      })
      .catch(() => {
        // Backend not running — populate default 4x4 constellation for demo
        const sats: { id: string; status: string }[] = [];
        const links: [string, string][] = [];
        for (let p = 0; p < 4; p++) {
          for (let s = 0; s < 4; s++) {
            sats.push({ id: `P${p}_S${s}`, status: 'ACTIVE' });
            // intra-plane links
            const nextS = (s + 1) % 4;
            links.push([`P${p}_S${s}`, `P${p}_S${nextS}`]);
          }
        }
        // inter-plane links
        for (let p = 0; p < 4; p++) {
          const nextP = (p + 1) % 4;
          for (let s = 0; s < 4; s++) {
            links.push([`P${p}_S${s}`, `P${nextP}_S${s}`]);
          }
        }
        setSatellites(sats);
        setLinks(links);
        setSource('P0_S0');
        setDestination('P3_S3');
        addEvent('Backend offline — running in demo mode (no routing)', 'info');
      });
  }, []);

  // WebSocket live updates
  useEffect(() => {
    if (!backendOnline) return;
    let ws: WebSocket;
    let retryTimeout: ReturnType<typeof setTimeout>;

    const connect = () => {
      ws = new WebSocket(WS);
      ws.onopen = () => addEvent('WebSocket connected', 'info');
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'route_update') {
          setActiveRoute(data.route ?? []);
          const status = data.success ? '✓' : '✗';
          addEvent(`${status} Route ${data.source}→${data.destination} | ${data.hops} hops | ${data.intent}`, 'route');
        } else if (data.type === 'link_failure') {
          const key = [...data.link].sort().join('-');
          addFailedLink(key);
          addEvent(`⚡ ISL FAILED: ${data.link[0]} ↔ ${data.link[1]} [${data.reason}]`, 'failure');
        } else if (data.type === 'link_recovery') {
          const key = [...data.link].sort().join('-');
          removeFailedLink(key);
          addEvent(`✓ ISL RECOVERED: ${data.link[0]} ↔ ${data.link[1]}`, 'recovery');
        }
      };
      ws.onerror = () => ws.close();
      ws.onclose = () => { retryTimeout = setTimeout(connect, 3000); };
    };

    connect();
    return () => { ws?.close(); clearTimeout(retryTimeout); };
  }, [backendOnline]);

  // Poll network links every 5s to sync failures
  useEffect(() => {
    if (!backendOnline) return;
    const poll = setInterval(() => {
      fetch(`${API}/network`)
        .then(r => r.json())
        .then(data => setLinks(data.links || []))
        .catch(() => {});
    }, 5000);
    return () => clearInterval(poll);
  }, [backendOnline]);

  const handleCalculateRoute = useCallback(async () => {
    if (!source || !destination || isRouting) return;
    setIsRouting(true);
    try {
      const res = await fetch(`${API}/route/calculate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source, destination, intent }),
      });
      const data = await res.json();
      if (data.route) {
        setActiveRoute(data.route);
        addEvent(`Route: ${source}→${destination} | ${data.hops} hops`, 'route');
      }
      // I-MACSI: Fetch 8D intent vector for custom intents
      if (!(intent in intentLabels)) {
        try {
          const ivRes = await fetch(`${API}/intent/extract`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ description: intent }),
          });
          const ivData = await ivRes.json();
          setIntentVector(ivData);
        } catch { /* ignore */ }
      }
    } catch {
      // Demo mode
      const demoRoute = [source, destination];
      setActiveRoute(demoRoute);
      addEvent(`Demo: ${source} → ${destination}`, 'route');
    } finally {
      setIsRouting(false);
    }
  }, [source, destination, intent, isRouting]);

  const handleFailLink = useCallback(async () => {
    if (!source || !destination) return;
    try {
      const res = await fetch(`${API}/simulate/failure`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source, destination }),
      });
      if (!res.ok) {
        const err = await res.json();
        addEvent(`Error: ${err.message}`, 'failure');
      }
    } catch {
      const key = [source, destination].sort().join('-');
      addFailedLink(key);
      addEvent(`ISL FAILED: ${source} ↔ ${destination}`, 'failure');
    }
  }, [source, destination]);

  const handleRecoverLink = useCallback(async () => {
    if (!source || !destination) return;
    try {
      const res = await fetch(`${API}/simulate/recovery`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source, destination }),
      });
      if (!res.ok) {
        const err = await res.json();
        addEvent(`Error: ${err.message}`, 'recovery');
      }
    } catch {
      const key = [source, destination].sort().join('-');
      removeFailedLink(key);
      addEvent(`ISL RECOVERED: ${source} ↔ ${destination}`, 'recovery');
    }
  }, [source, destination]);

  const handleRandomFailure = useCallback(async () => {
    try {
      await fetch(`${API}/simulate/random_failure`, { method: 'POST' });
    } catch {
      addEvent('Random failure: backend offline', 'failure');
    }
  }, []);

  const handleTrainMore = useCallback(async () => {
    if (isTraining) return;
    setIsTraining(true);
    try {
      const res = await fetch(`${API}/train`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ count: 50 }),
      });
      const data = await res.json();
      setTrainingStats(data);
      addEvent(`Training: PDR=${(data.pdr * 100).toFixed(1)}% | ε=${data.epsilon.toFixed(4)} | ${data.avg_latency_ms.toFixed(1)}ms avg`, 'info');
    } catch {
      addEvent('Training failed: backend offline', 'failure');
    } finally {
      setIsTraining(false);
    }
  }, [isTraining]);

  const allSatelliteIds = satellites.map(s => s.id).sort();

  return (
    <>
      {/* 3D Canvas */}
      <div className="canvas-container">
        <Scene />
      </div>

      <div className="scanline-overlay" />

      {/* HUD Layer */}
      <div className="hud-layer">

        {/* Top Bar */}
        <div className="hud-top">
          <div className="corner-panel top-left-panel">
            <div className="panel-bracket top-left" />
            <div className="title-text">
              <span className="title-main">LEO DIGITAL TWIN</span>
              <span className="title-sub">AI-NATIVE COGNITIVE SWARM ROUTING</span>
            </div>
            <div className="status-indicator">
              <span className="status-dot" style={{ background: backendOnline ? '#00e676' : '#ff5252' }} />
              <span className="status-text">{backendOnline ? 'BACKEND ONLINE' : 'DEMO MODE'}</span>
            </div>
          </div>

          <HUDMetrics />

          <div className="corner-panel top-right-panel">
            <div className="panel-bracket top-right" />
            <div className="coord-display">
              <div className="coord-line">ORB: 4×4 LEO CONSTELLATION</div>
              <div className="coord-line">ALT: ~550 KM | INCL: 53°</div>
              <div className="coord-line">ISL BAND: Ka | BW: 1 Gbps</div>
            </div>

            {/* Live satellite coordinate readouts */}
            <div className="sat-coords-panel">
              <CoordinatePanel />
              <MissionPerformance />

              {/* Training stats */}
              {trainingStats && (
                <div className="sat-coord-row" style={{ borderColor: '#c77dff' }}>
                  <span className="sat-coord-label" style={{ color: '#c77dff' }}>LAST TRAINING</span>
                  <div className="sat-coord-vals">
                    <span className="sat-coord-val">PDR {((trainingStats.pdr ?? 0) * 100).toFixed(1)}%</span>
                    <span className="sat-coord-val">ε {trainingStats.epsilon?.toFixed(4)}</span>
                    <span className="sat-coord-val">{trainingStats.avg_latency_ms?.toFixed(1)} ms</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Bottom Row */}
        <div className="hud-bottom">
          {/* Left: Control Panel */}
          <div className="corner-panel control-panel">
            <div className="panel-bracket bottom-left" />
            <div className="panel-title">ROUTING CONTROL</div>

            <div className="selector-row">
              <div className="selector-group">
                <label className="selector-label">SOURCE NODE</label>
                <select
                  className="hud-select"
                  value={source}
                  onChange={e => setSource(e.target.value)}
                >
                  {allSatelliteIds.map(id => (
                    <option key={id} value={id}>{id}</option>
                  ))}
                </select>
              </div>
              <div className="selector-arrow">→</div>
              <div className="selector-group">
                <label className="selector-label">DESTINATION NODE</label>
                <select
                  className="hud-select"
                  value={destination}
                  onChange={e => setDestination(e.target.value)}
                >
                  {allSatelliteIds.map(id => (
                    <option key={id} value={id}>{id}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* I-MACSI Intent selector */}
            <div className="intent-row">
              <label className="selector-label">I-MACSI MISSION INTENT</label>
              <input
                type="text"
                className="hud-select"
                style={{ cursor: 'text', marginBottom: '4px' }}
                placeholder="Describe intent (e.g. 'encrypted military drone surveillance')"
                value={intent}
                onChange={e => {
                  setIntent(e.target.value);
                  setIntentVector(null);
                }}
              />
              <div className="intent-pills" style={{ flexWrap: 'wrap' }}>
                {Object.keys(intentLabels).map(i => (
                  <button
                    key={i}
                    className={`intent-pill ${intent === i ? 'active' : ''}`}
                    style={{ '--pill-color': intentColors[i] || '#64ffda' } as React.CSSProperties}
                    onClick={() => { setIntent(i); setIntentVector(null); }}
                  >
                    {intentLabels[i] || i}
                  </button>
                ))}
              </div>
            </div>

            {/* I-MACSI 8D Intent Vector Display */}
            {intentVector && (
              <div className="route-display" style={{ marginBottom: '10px' }}>
                <div className="route-label">8D INTENT VECTOR</div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2px 12px', fontFamily: 'var(--text-mono)', fontSize: '0.62rem' }}>
                  {['w_latency', 'w_throughput', 'w_reliability', 'w_congestion', 'w_energy', 'w_security', 'w_coverage', 'w_compute'].map(dim => {
                    const val = intentVector[dim] ?? 0;
                    const label = dim.replace('w_', '').toUpperCase();
                    const barColor = val > 0.3 ? '#64ffda' : val > 0.1 ? '#546e7a' : '#1a2a3a';
                    return (
                      <div key={dim} style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <span style={{ width: '70px', color: 'var(--text-dim)' }}>{label}</span>
                        <div style={{ flex: 1, height: '6px', background: '#0a1628', borderRadius: '3px', overflow: 'hidden' }}>
                          <div style={{ width: `${Math.min(val * 100, 100)}%`, height: '100%', background: barColor, borderRadius: '3px', transition: 'width 0.3s' }} />
                        </div>
                        <span style={{ width: '32px', textAlign: 'right', color: 'var(--text-primary)' }}>{(val * 100).toFixed(0)}%</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Action buttons */}
            <div className="action-row">
              <button className="action-btn primary" onClick={handleCalculateRoute} disabled={isRouting}>
                {isRouting ? '⟳ ROUTING...' : '▶ CALCULATE ROUTE'}
              </button>
              <button className="action-btn danger" onClick={handleFailLink}>
                ✕ INJECT FAILURE
              </button>
              <button className="action-btn success" onClick={handleRecoverLink}>
                ↺ RECOVER LINK
              </button>
            </div>
            <div className="action-row">
              <button className="action-btn warning" onClick={handleRandomFailure}>
                ⚡ RANDOM FAILURE
              </button>
              <button className="action-btn info-btn" onClick={handleTrainMore} disabled={isTraining}>
                {isTraining ? '⟳ TRAINING...' : '▲ TRAIN +50'}
              </button>
            </div>

            {/* Route display */}
            {activeRoute.length > 1 && (
              <div className="route-display">
                <div className="route-label">ACTIVE ROUTE ({activeRoute.length - 1} HOPS)</div>
                <div className="route-path">
                  {activeRoute.map((node, i) => (
                    <span key={i}>
                      <span className="route-node" style={{ color: intentColors[intent] }}>{node}</span>
                      {i < activeRoute.length - 1 && <span className="route-sep"> → </span>}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right: Event Ticker */}
          <div className="corner-panel event-panel">
            <div className="panel-bracket bottom-right" />
            <EventTicker />
          </div>
        </div>

        <div className="click-hint">CLICK SATELLITE TO SELECT SRC → DST</div>
      </div>
    </>
  );
}

export default App;
