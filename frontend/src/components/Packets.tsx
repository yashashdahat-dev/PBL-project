import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { satellitePositions } from '../store';
import { useSimulationStore } from '../hooks/useSimulationStore';

interface PacketsProps {
  route: string[];
}

const TRAIL_LENGTH = 4;   // reduced from 6
const NUM_PACKETS  = 6;   // reduced from 8

// Pre-allocate vectors to avoid GC in useFrame
const _p1 = new THREE.Vector3();
const _p2 = new THREE.Vector3();
const _lerpedPos = new THREE.Vector3();
const _dummy = new THREE.Object3D();

export default function Packets({ route }: PacketsProps) {
  const meshRef  = useRef<THREE.InstancedMesh>(null);
  const trailRef = useRef<THREE.InstancedMesh[]>([]);

  const intent     = useSimulationStore(s => s.intent);
  const packetColor = useMemo(() => {
    const map: Record<string, string> = {
      CRITICAL_DISASTER: '#ff6b35',
      EARTH_OBSERVATION: '#00b4d8',
      SECURE_MISSION:    '#c77dff',
    };
    return map[intent] || '#ffab00';
  }, [intent]);

  // Track progress per packet in a ref (not state) to avoid re-renders
  const progressRef = useRef<number[]>(
    Array.from({ length: NUM_PACKETS }, (_, i) => (i / NUM_PACKETS) * Math.max(1, route.length - 1))
  );

  // Reset progress when route changes
  useMemo(() => {
    progressRef.current = Array.from(
      { length: NUM_PACKETS },
      (_, i) => (i / NUM_PACKETS) * Math.max(1, route.length - 1)
    );
  }, [route]);

  useFrame((_, delta) => {
    if (!meshRef.current || route.length < 2) return;

    const speed = 1.6;
    const maxP  = route.length - 1;

    for (let i = 0; i < NUM_PACKETS; i++) {
      progressRef.current[i] = (progressRef.current[i] + speed * delta) % maxP;

      const prog    = progressRef.current[i];
      const hop     = Math.floor(prog);
      const nextHop = Math.min(hop + 1, route.length - 1);
      const alpha   = prog - hop;

      const rp1 = satellitePositions.get(route[hop]);
      const rp2 = satellitePositions.get(route[nextHop]);
      if (!rp1 || !rp2) continue;

      _p1.copy(rp1); _p2.copy(rp2);
      _lerpedPos.lerpVectors(_p1, _p2, alpha);

      // Head
      _dummy.position.copy(_lerpedPos);
      _dummy.scale.setScalar(0.042);
      _dummy.updateMatrix();
      meshRef.current.setMatrixAt(i, _dummy.matrix);

      // Trails
      for (let t = 0; t < TRAIL_LENGTH; t++) {
        const tm = trailRef.current[t];
        if (!tm) continue;

        const tp = prog - (t + 1) * 0.22;
        if (tp < 0) {
          _dummy.scale.setScalar(0);
          _dummy.updateMatrix();
          tm.setMatrixAt(i, _dummy.matrix);
          continue;
        }

        const tHop = Math.min(Math.floor(tp), route.length - 2);
        const tNext = Math.min(tHop + 1, route.length - 1);
        const ta = Math.min(1, tp - tHop);
        const tp1 = satellitePositions.get(route[tHop]);
        const tp2 = satellitePositions.get(route[tNext]);

        if (tp1 && tp2) {
          _dummy.position.lerpVectors(tp1, tp2, ta);
          _dummy.scale.setScalar(0.032 * (1 - (t + 1) / (TRAIL_LENGTH + 1)));
          _dummy.updateMatrix();
          tm.setMatrixAt(i, _dummy.matrix);
        }
      }
    }

    meshRef.current.instanceMatrix.needsUpdate = true;
    trailRef.current.forEach(m => { if (m) m.instanceMatrix.needsUpdate = true; });
  });

  if (route.length < 2) return null;

  return (
    <group>
      {Array.from({ length: TRAIL_LENGTH }).map((_, t) => (
        <instancedMesh
          key={t}
          ref={(el) => { if (el) trailRef.current[t] = el; }}
          args={[undefined, undefined, NUM_PACKETS]}
        >
          <sphereGeometry args={[1, 6, 6]} />
          <meshBasicMaterial
            color={packetColor}
            transparent
            opacity={0.45 * (1 - (t + 1) / (TRAIL_LENGTH + 1))}
            blending={THREE.AdditiveBlending}
            depthWrite={false}
          />
        </instancedMesh>
      ))}

      <instancedMesh ref={meshRef} args={[undefined, undefined, NUM_PACKETS]}>
        <sphereGeometry args={[1, 10, 10]} />
        <meshBasicMaterial color={packetColor} transparent opacity={0.95} blending={THREE.AdditiveBlending} depthWrite={false} />
      </instancedMesh>
    </group>
  );
}
