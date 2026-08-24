import { useRef, useMemo, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { satellitePositions } from '../store';
import { useSimulationStore, intentColors } from '../hooks/useSimulationStore';

interface ActiveRouteProps {
  route: string[];
}

// Pre-allocated vectors — never allocate in useFrame
const _p1  = new THREE.Vector3();
const _p2  = new THREE.Vector3();
const _end = new THREE.Vector3();

export default function ActiveRoute({ route }: ActiveRouteProps) {
  const lineRef     = useRef<THREE.LineSegments>(null);
  const glowLineRef = useRef<THREE.LineSegments>(null);
  const timeRef        = useRef(0);
  const drawProgressRef = useRef(0);
  const prevRouteKey   = useRef('');

  const intent = useSimulationStore(s => s.intent);
  const routeColor = intentColors[intent] ?? '#64ffda';

  const linkPairs = useMemo<[string, string][]>(() => {
    const pairs: [string, string][] = [];
    for (let i = 0; i < route.length - 1; i++) pairs.push([route[i], route[i + 1]]);
    return pairs;
  }, [route]);

  // Reset draw-in animation on new route
  const routeKey = route.join('-');
  if (routeKey !== prevRouteKey.current) {
    drawProgressRef.current = 0;
    prevRouteKey.current = routeKey;
  }

  // Pre-allocated buffers sized for max segments
  const positions     = useMemo(() => new Float32Array(linkPairs.length * 6), [linkPairs.length]);
  const glowPositions = useMemo(() => new Float32Array(linkPairs.length * 6), [linkPairs.length]);

  useFrame((_, delta) => {
    if (linkPairs.length === 0) return;
    timeRef.current += delta;

    // Animate draw-in: 3 hops per second
    drawProgressRef.current = Math.min(drawProgressRef.current + delta * 3.0, linkPairs.length);

    const visibleFull    = Math.floor(drawProgressRef.current);
    const partialFrac    = drawProgressRef.current - visibleFull;

    let i = 0;
    for (let idx = 0; idx < linkPairs.length; idx++) {
      const [src, dst] = linkPairs[idx];
      const p1 = satellitePositions.get(src);
      const p2 = satellitePositions.get(dst);

      if (p1 && p2) {
        _p1.copy(p1); _p2.copy(p2);

        if (idx < visibleFull) {
          _end.copy(_p2);
        } else if (idx === visibleFull) {
          _end.lerpVectors(_p1, _p2, partialFrac);
        } else {
          _end.copy(_p1); // zero-length, invisible
        }

        positions[i]   = _p1.x; positions[i+1] = _p1.y; positions[i+2] = _p1.z;
        positions[i+3] = _end.x; positions[i+4] = _end.y; positions[i+5] = _end.z;
        glowPositions[i]   = positions[i];   glowPositions[i+1] = positions[i+1]; glowPositions[i+2] = positions[i+2];
        glowPositions[i+3] = positions[i+3]; glowPositions[i+4] = positions[i+4]; glowPositions[i+5] = positions[i+5];
      }
      i += 6;
    }

    const pulse = Math.sin(timeRef.current * 3.5) * 0.25 + 0.75;

    if (lineRef.current) {
      lineRef.current.geometry.attributes.position.needsUpdate = true;
      (lineRef.current.material as THREE.LineBasicMaterial).opacity = pulse;
    }
    if (glowLineRef.current) {
      glowLineRef.current.geometry.attributes.position.needsUpdate = true;
      (glowLineRef.current.material as THREE.LineBasicMaterial).opacity = (1 - pulse) * 0.25;
    }
  });

  if (route.length < 2) return null;

  return (
    <group>
      {/* Outer glow */}
      <lineSegments ref={glowLineRef}>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" count={glowPositions.length / 3} array={glowPositions} itemSize={3} />
        </bufferGeometry>
        <lineBasicMaterial color={routeColor} transparent opacity={0.15} depthWrite={false} blending={THREE.AdditiveBlending} />
      </lineSegments>

      {/* Main beam */}
      <lineSegments ref={lineRef}>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" count={positions.length / 3} array={positions} itemSize={3} />
        </bufferGeometry>
        <lineBasicMaterial color={routeColor} transparent opacity={0.9} depthWrite={false} blending={THREE.AdditiveBlending} />
      </lineSegments>
    </group>
  );
}
