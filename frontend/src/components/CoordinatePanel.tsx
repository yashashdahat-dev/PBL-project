import React from 'react';
import { useSimulationStore } from '../hooks/useSimulationStore';

export default function CoordinatePanel() {
  const source           = useSimulationStore(s => s.source);
  const destination      = useSimulationStore(s => s.destination);
  const hoveredSatellite = useSimulationStore(s => s.hoveredSatellite);
  const satelliteCoords  = useSimulationStore(s => s.satelliteCoords);

  return (
    <>
      {[
        { id: source, label: 'SRC', color: '#00ff88' },
        { id: destination, label: 'DST', color: '#ffaa00' },
      ]
        .filter(s => s.id)
        .map(({ id, label, color }) => {
          const c = satelliteCoords[id];
          return (
            <div key={id} className="sat-coord-row" style={{ borderColor: color }}>
              <span className="sat-coord-label" style={{ color }}>{label} {id}</span>
              {c ? (
                <div className="sat-coord-vals">
                  <span className="sat-coord-val">LAT {c.lat >= 0 ? '+' : ''}{c.lat.toFixed(2)}°</span>
                  <span className="sat-coord-val">LON {c.lon >= 0 ? '+' : ''}{c.lon.toFixed(2)}°</span>
                  <span className="sat-coord-val">ALT {c.alt} km</span>
                </div>
              ) : (
                <span className="sat-coord-val sat-coord-waiting">Acquiring lock...</span>
              )}
            </div>
          );
        })}
      {hoveredSatellite && hoveredSatellite !== source && hoveredSatellite !== destination && (() => {
        const c = satelliteCoords[hoveredSatellite];
        return (
          <div className="sat-coord-row sat-coord-hover" style={{ borderColor: '#ffffff55' }}>
            <span className="sat-coord-label" style={{ color: '#e0e0e0' }}>HOV {hoveredSatellite}</span>
            {c ? (
              <div className="sat-coord-vals">
                <span className="sat-coord-val">LAT {c.lat >= 0 ? '+' : ''}{c.lat.toFixed(2)}°</span>
                <span className="sat-coord-val">LON {c.lon >= 0 ? '+' : ''}{c.lon.toFixed(2)}°</span>
                <span className="sat-coord-val">ALT {c.alt} km</span>
              </div>
            ) : (
              <span className="sat-coord-val sat-coord-waiting">Acquiring lock...</span>
            )}
          </div>
        );
      })()}
    </>
  );
}
