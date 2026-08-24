import React, { useEffect, useRef } from 'react';
import { useSimulationStore } from '../hooks/useSimulationStore';

export default function HUDMetrics() {
  const { satellites, links, activeRoute, failedLinks, failedSatellites } = useSimulationStore();

  const hopCount = Math.max(0, activeRoute.length - 1);
  const networkHealth = failedSatellites.size > 0 || failedLinks.size > 0 ? 'DEGRADED' : 'NOMINAL';
  const healthPct = Math.max(0, 100 - failedLinks.size * 12 - failedSatellites.size * 8);

  return (
    <div className="hud-metrics">
      <MetricCard label="SATELLITES" value={satellites.length} unit="" color="#29b6f6" />
      <MetricCard label="ACTIVE LINKS" value={links.length - failedLinks.size} unit={`/${links.length}`} color="#64ffda" />
      <MetricCard label="ROUTE HOPS" value={hopCount} unit="" color="#c77dff" />
      <MetricCard
        label="NET HEALTH"
        value={healthPct}
        unit="%"
        color={networkHealth === 'NOMINAL' ? '#00e676' : '#ff5252'}
      />
    </div>
  );
}

function MetricCard({ label, value, unit, color }: { label: string; value: number; unit: string; color: string }) {
  const displayRef = useRef<HTMLSpanElement>(null);
  const animValueRef = useRef(0);

  useEffect(() => {
    let frame: number;
    const target = value;
    const animate = () => {
      animValueRef.current += (target - animValueRef.current) * 0.12;
      if (displayRef.current) {
        displayRef.current.textContent = Math.round(animValueRef.current).toString();
      }
      if (Math.abs(animValueRef.current - target) > 0.5) {
        frame = requestAnimationFrame(animate);
      } else {
        if (displayRef.current) displayRef.current.textContent = target.toString();
      }
    };
    frame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frame);
  }, [value]);

  return (
    <div className="metric-card" style={{ borderColor: color + '44' }}>
      <div className="metric-label">{label}</div>
      <div className="metric-value" style={{ color }}>
        <span ref={displayRef}>{value}</span>
        <span className="metric-unit">{unit}</span>
      </div>
    </div>
  );
}
