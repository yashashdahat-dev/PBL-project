import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { satellitePositions } from '../store';
import { useSimulationStore } from '../hooks/useSimulationStore';

interface LinksProps {
  links: [string, string][];
}

export default function Links({ links }: LinksProps) {
  const normalLineRef = useRef<THREE.LineSegments>(null);
  const failedLineRef = useRef<THREE.LineSegments>(null);
  const timeRef = useRef(0);

  const failedLinks = useSimulationStore(s => s.failedLinks);

  // Pre-allocate position buffers — size based on total links
  const normalPositions = useMemo(() => new Float32Array(links.length * 6), [links]);
  const failedPositions = useMemo(() => new Float32Array(links.length * 6), [links]);

  // Separate link sets — recomputed only when links/failedLinks changes
  const { normalLinks, failedLinkPairs } = useMemo(() => {
    const normal: [string, string][] = [];
    const failed: [string, string][] = [];
    for (const [a, b] of links) {
      const key = [a, b].sort().join('-');
      failedLinks.has(key) ? failed.push([a, b]) : normal.push([a, b]);
    }
    return { normalLinks: normal, failedLinkPairs: failed };
  }, [links, failedLinks]);

  useFrame((_, delta) => {
    timeRef.current += delta;
    const pulse = Math.sin(timeRef.current * 1.8) * 0.5 + 0.5;

    if (normalLineRef.current) {
      let i = 0;
      for (const [src, dst] of normalLinks) {
        const p1 = satellitePositions.get(src);
        const p2 = satellitePositions.get(dst);
        if (p1 && p2) {
          normalPositions[i]   = p1.x; normalPositions[i+1] = p1.y; normalPositions[i+2] = p1.z;
          normalPositions[i+3] = p2.x; normalPositions[i+4] = p2.y; normalPositions[i+5] = p2.z;
        }
        i += 6;
      }
      normalLineRef.current.geometry.attributes.position.needsUpdate = true;
      (normalLineRef.current.material as THREE.LineBasicMaterial).opacity = 0.18 + pulse * 0.1;
    }

    if (failedLineRef.current && failedLinkPairs.length > 0) {
      let i = 0;
      for (const [src, dst] of failedLinkPairs) {
        const p1 = satellitePositions.get(src);
        const p2 = satellitePositions.get(dst);
        if (p1 && p2) {
          failedPositions[i]   = p1.x; failedPositions[i+1] = p1.y; failedPositions[i+2] = p1.z;
          failedPositions[i+3] = p2.x; failedPositions[i+4] = p2.y; failedPositions[i+5] = p2.z;
        }
        i += 6;
      }
      failedLineRef.current.geometry.attributes.position.needsUpdate = true;
      (failedLineRef.current.material as THREE.LineBasicMaterial).opacity = 0.4 + pulse * 0.4;
    }
  });

  return (
    <group>
      {/* Normal links */}
      <lineSegments ref={normalLineRef}>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" count={normalPositions.length / 3} array={normalPositions} itemSize={3} />
        </bufferGeometry>
        <lineBasicMaterial color="#4287f5" transparent opacity={0.2} depthWrite={false} blending={THREE.AdditiveBlending} />
      </lineSegments>

      {/* Failed links */}
      {failedLinkPairs.length > 0 && (
        <lineSegments ref={failedLineRef}>
          <bufferGeometry>
            <bufferAttribute attach="attributes-position" count={failedPositions.length / 3} array={failedPositions} itemSize={3} />
          </bufferGeometry>
          <lineBasicMaterial color="#ff2244" transparent opacity={0.6} depthWrite={false} blending={THREE.AdditiveBlending} />
        </lineSegments>
      )}
    </group>
  );
}
