import { useMemo } from 'react';
import * as THREE from 'three';
import { memo } from 'react';
import Satellite from './Satellite';
import Links from './Links';
import ActiveRoute from './ActiveRoute';
import Packets from './Packets';
import { useSimulationStore } from '../hooks/useSimulationStore';

// Memo so Constellation only re-renders if its own props change
const Constellation = memo(function Constellation() {
  const activeRoute = useSimulationStore(s => s.activeRoute);
  const links       = useSimulationStore(s => s.links);

  const numPlanes    = 4;
  const satsPerPlane = 4;
  const orbitRadius  = 4.2;

  const satelliteData = useMemo(() => {
    const data = [];
    for (let p = 0; p < numPlanes; p++) {
      for (let s = 0; s < satsPerPlane; s++) {
        data.push({ id: `P${p}_S${s}`, planeId: p, satIndex: s });
      }
    }
    return data;
  }, []);

  // Orbital ring geometry — shared across all planes (same torus, different rotation)
  const ringGeo = useMemo(() => new THREE.TorusGeometry(orbitRadius, 0.005, 8, 80), []);
  const ringMat = useMemo(() => new THREE.MeshBasicMaterial({
    color: '#64ffda',
    transparent: true,
    opacity: 0.06,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  }), []);

  return (
    <group>
      {satelliteData.map((sat) => (
        <Satellite
          key={sat.id}
          id={sat.id}
          planeId={sat.planeId}
          satIndex={sat.satIndex}
          numPlanes={numPlanes}
          satsPerPlane={satsPerPlane}
          orbitRadius={orbitRadius}
        />
      ))}

      {/* Shared geometry orbital rings — one draw call per ring */}
      {Array.from({ length: numPlanes }).map((_, p) => {
        const lon = (2 * Math.PI / numPlanes) * p;
        return (
          <mesh key={`ring-${p}`} geometry={ringGeo} material={ringMat} rotation={[Math.PI / 2, lon, 0]} />
        );
      })}

      <Links links={links} />
      <ActiveRoute route={activeRoute} />
      <Packets route={activeRoute} />
    </group>
  );
});

export default Constellation;
