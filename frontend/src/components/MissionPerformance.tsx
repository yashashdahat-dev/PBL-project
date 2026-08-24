import React, { useEffect, useState } from 'react';

const API = 'http://localhost:8000';

interface MetricsData {
  average_latency_ms: number;
  throughput_bps: number;
  packet_delivery_ratio: number;
  spectral_efficiency: number;
  energy_consumption_j: number;
  bandwidth_utilization: number;
  fairness_index: number;
  mission_completion_ratio: number;
  mission_satisfaction_index: number;
  intent_prediction_accuracy: number;
  resource_allocation_efficiency: number;
  mission_priority_preservation: number;
  service_continuity: number;
  dynamic_resilience: number;
  swarm_coordination_efficiency: number;
  learning_convergence_speed: number;
}

const MissionPerformance: React.FC = () => {
  const [metrics, setMetrics] = useState<MetricsData | null>(null);

  // Poll the backend metrics every 2 seconds
  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await fetch(`${API}/metrics`);
        if (res.ok) {
          const data = await res.json();
          setMetrics(data);
        }
      } catch (err) {
        console.error('Failed to fetch metrics', err);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 2000);
    return () => clearInterval(interval);
  }, []);

  if (!metrics) {
    return (
      <div className="corner-panel event-panel" style={{ marginTop: '20px', pointerEvents: 'auto' }}>
        <div className="panel-bracket bottom-right" />
        <div className="panel-title">MISSION PERFORMANCE</div>
        <div style={{ color: '#00e676', fontSize: '14px', fontFamily: 'monospace' }}>AWAITING TELEMETRY...</div>
      </div>
    );
  }

  const formatValue = (val: number | undefined, dec: number = 1) => {
    return (val ?? 0).toFixed(dec);
  };

  return (
    <div className="corner-panel event-panel" style={{ marginTop: '20px', pointerEvents: 'auto' }}>
      <div className="panel-bracket bottom-right" />
      <div className="panel-title">MISSION PERFORMANCE</div>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', rowGap: '4px', columnGap: '20px', fontFamily: 'monospace', fontSize: '12px', color: '#00e676', borderBottom: '1px solid rgba(0,230,118,0.2)', paddingBottom: '8px', marginBottom: '8px' }}>
        <span>LATENCY</span>
        <span style={{ textAlign: 'right' }}>{formatValue(metrics.average_latency_ms)} ms</span>
        
        <span>THROUGHPUT</span>
        <span style={{ textAlign: 'right' }}>{formatValue(metrics.throughput_bps / 1000000)} Mbps</span>
        
        <span>PDR</span>
        <span style={{ textAlign: 'right' }}>{formatValue(metrics.packet_delivery_ratio)} %</span>
        
        <span>SPECTRAL EFFICIENCY</span>
        <span style={{ textAlign: 'right' }}>{formatValue(metrics.spectral_efficiency, 3)} b/s/Hz</span>
        
        <span>ENERGY</span>
        <span style={{ textAlign: 'right' }}>{formatValue(metrics.energy_consumption_j)} J</span>
        
        <span>BANDWIDTH</span>
        <span style={{ textAlign: 'right' }}>{formatValue(metrics.bandwidth_utilization)} %</span>
        
        <span>FAIRNESS</span>
        <span style={{ textAlign: 'right' }}>{formatValue(metrics.fairness_index, 3)}</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', rowGap: '4px', columnGap: '20px', fontFamily: 'monospace', fontSize: '12px', color: '#00b0ff' }}>
        <span>MISSION COMPLETION</span>
        <span style={{ textAlign: 'right' }}>{formatValue(metrics.mission_completion_ratio)} %</span>
        
        <span>SATISFACTION</span>
        <span style={{ textAlign: 'right' }}>{formatValue(metrics.mission_satisfaction_index * 100)} %</span>
        
        <span>INTENT ACCURACY</span>
        <span style={{ textAlign: 'right' }}>{formatValue(metrics.intent_prediction_accuracy)} %</span>
        
        <span>RESOURCE EFFICIENCY</span>
        <span style={{ textAlign: 'right' }}>{formatValue(metrics.resource_allocation_efficiency)} %</span>
        
        <span>PRIORITY PRESERV.</span>
        <span style={{ textAlign: 'right' }}>{formatValue(metrics.mission_priority_preservation)} %</span>
        
        <span>SERVICE CONTINUITY</span>
        <span style={{ textAlign: 'right' }}>{formatValue(metrics.service_continuity)} %</span>
        
        <span>RESILIENCE</span>
        <span style={{ textAlign: 'right' }}>{formatValue(metrics.dynamic_resilience)} %</span>
        
        <span>SWARM COORDINATION</span>
        <span style={{ textAlign: 'right' }}>{formatValue(metrics.swarm_coordination_efficiency)} %</span>
        
        <span>CONVERGENCE</span>
        <span style={{ textAlign: 'right' }}>{metrics.learning_convergence_speed ?? 0} steps</span>
      </div>
    </div>
  );
};

export default MissionPerformance;
