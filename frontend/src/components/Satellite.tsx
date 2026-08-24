import { useRef, useMemo, useCallback } from 'react';
import { useFrame } from '@react-three/fiber';
import type { ThreeEvent } from '@react-three/fiber';
import * as THREE from 'three';
import { satellitePositions } from '../store';
import { useSimulationStore, intentColors } from '../hooks/useSimulationStore';

// Earth radius in scene units — MUST match Earth.tsx sphereGeometry radius (3.0)
const EARTH_RADIUS_SCENE = 3.0;
// Real Earth radius in km
const EARTH_RADIUS_KM = 6371;
// LEO orbital altitude in km
const ORBIT_ALT_KM = 550;

/** Convert 3D scene position to geographic lat/lon/alt */
function sceneToGeo(x: number, y: number, z: number, orbitRadius: number) {
  const r = Math.sqrt(x * x + y * y + z * z);
  // Scale: orbitRadius scene units == EARTH_RADIUS_KM + ORBIT_ALT_KM km
  const sceneToKm = (EARTH_RADIUS_KM + ORBIT_ALT_KM) / orbitRadius;
  const altKm = (r - EARTH_RADIUS_SCENE) * sceneToKm;

  // lat/lon from Cartesian (Three.js: Y is up-ish but we use Z as polar axis since we set z = orbitRadius * sin(a))
  // Our orbit: x = R*cos(a)*cos(lon), y = R*cos(a)*sin(lon), z = R*sin(a)
  const lat = Math.asin(z / r) * (180 / Math.PI);
  const lon = Math.atan2(y, x) * (180 / Math.PI);
  return { lat, lon, alt: Math.round(altKm) };
}

interface SatelliteProps {
  id: string;
  planeId: number;
  satIndex: number;
  numPlanes: number;
  satsPerPlane: number;
  orbitRadius: number;
}

// Pre-allocate reusable color objects — NEVER create inside useFrame
const _targetColor = new THREE.Color();

export default function Satellite({ id, planeId, satIndex, numPlanes, satsPerPlane, orbitRadius }: SatelliteProps) {
  const meshRef    = useRef<THREE.Mesh>(null);
  const glowRef    = useRef<THREE.Mesh>(null);
  const haloRef    = useRef<THREE.Mesh>(null);
  const lightRef   = useRef<THREE.PointLight>(null);
  const timeRef    = useRef(Math.random() * Math.PI * 2);
  const anomalyRef = useRef((2 * Math.PI / satsPerPlane) * satIndex);

  const lon        = useMemo(() => (2 * Math.PI / numPlanes) * planeId, [numPlanes, planeId]);
  const orbitSpeed = useMemo(() => 0.15 + planeId * 0.008, [planeId]);

  // Read only the specific slice of state needed to minimize re-renders
  const source          = useSimulationStore(s => s.source);
  const destination     = useSimulationStore(s => s.destination);
  const intent          = useSimulationStore(s => s.intent);
  const activeRoute     = useSimulationStore(s => s.activeRoute);
  const failedSatellites = useSimulationStore(s => s.failedSatellites);
  const hoveredSatellite = useSimulationStore(s => s.hoveredSatellite);
  const setSource       = useSimulationStore(s => s.setSource);
  const setDestination  = useSimulationStore(s => s.setDestination);
  const setHoveredSatellite = useSimulationStore(s => s.setHoveredSatellite);
  const updateSatCoords = useSimulationStore(s => s.updateSatCoords);

  // Throttle coordinate pushes to ~10 Hz
  const coordTimerRef = useRef(0);

  const isOnRoute  = activeRoute.includes(id);
  const isSource   = source === id;
  const isDest     = destination === id;
  const isFailed   = failedSatellites.has(id);
  const isHovered  = hoveredSatellite === id;
  const isSpecial  = isSource || isDest || isOnRoute || isHovered;

  // Determine color hex string — computed in render, not useFrame
  const satColorHex = useMemo(() => {
    if (isFailed)   return '#ff2244';
    if (isSource)   return '#00ff88';
    if (isDest)     return '#ffaa00';
    if (isOnRoute)  return intentColors[intent];
    return '#29b6f6';
  }, [isFailed, isSource, isDest, isOnRoute, intent]);

  const handleClick = useCallback((e: ThreeEvent<MouseEvent>) => {
    e.stopPropagation();
    if (!source || isSource) { setSource(id); }
    else { setDestination(id); }
  }, [id, source, isSource, setSource, setDestination]);

  const handlePointerEnter = useCallback((e: ThreeEvent<PointerEvent>) => {
    e.stopPropagation();
    setHoveredSatellite(id);
    document.body.style.cursor = 'pointer';
  }, [id, setHoveredSatellite]);

  const handlePointerLeave = useCallback(() => {
    setHoveredSatellite(null);
    document.body.style.cursor = '';
  }, [setHoveredSatellite]);

  useFrame((state, delta) => {
    if (!meshRef.current) return;
    timeRef.current += delta;
    anomalyRef.current += orbitSpeed * delta;

    const a = anomalyRef.current;
    const x = orbitRadius * Math.cos(a) * Math.cos(lon);
    const y = orbitRadius * Math.cos(a) * Math.sin(lon);
    const z = orbitRadius * Math.sin(a);

    meshRef.current.position.set(x, y, z);

    // Update shared position store
    let pos = satellitePositions.get(id);
    if (!pos) { pos = new THREE.Vector3(); satellitePositions.set(id, pos); }
    pos.set(x, y, z);

    // Push geo coordinates to store — throttled, only for visible/special sats
    if (isSource || isDest || isHovered) {
      coordTimerRef.current += delta;
      if (coordTimerRef.current > 0.1) {
        coordTimerRef.current = 0;
        updateSatCoords(id, sceneToGeo(x, y, z, orbitRadius));
      }
    }

    // Only compute expensive visuals for special satellites
    const pulse = isSpecial
      ? Math.sin(timeRef.current * 3.0) * 0.5 + 0.5
      : 0.5;

    // Color lerp — reuse pre-allocated object
    _targetColor.set(satColorHex);
    const mat = meshRef.current.material as THREE.MeshStandardMaterial;
    mat.color.lerp(_targetColor, 0.15);
    mat.emissive.lerp(_targetColor, 0.15);
    mat.emissiveIntensity = isSpecial ? 0.7 + pulse * 0.5 : 0.25;

    // Glow
    if (glowRef.current) {
      glowRef.current.position.set(x, y, z);
      const gm = glowRef.current.material as THREE.MeshBasicMaterial;
      gm.opacity = isSpecial ? 0.2 + pulse * 0.2 : 0.05;
      glowRef.current.scale.setScalar(isSpecial ? 2.2 + pulse * 0.3 : 1.6);
    }

    // Halo ring — only for special sats
    if (haloRef.current) {
      haloRef.current.visible = isSpecial;
      if (isSpecial) {
        haloRef.current.position.set(x, y, z);
        haloRef.current.lookAt(state.camera.position);
        (haloRef.current.material as THREE.MeshBasicMaterial).opacity = 0.4 + pulse * 0.45;
        haloRef.current.scale.setScalar(1 + pulse * 0.12);
      }
    }

    // Point light — only emit for special sats to save GPU
    if (lightRef.current) {
      lightRef.current.position.set(x, y, z);
      lightRef.current.intensity = isSpecial ? 0.35 + pulse * 0.25 : 0;
    }
  });

  return (
    <group>
      <mesh
        ref={meshRef}
        onClick={handleClick}
        onPointerEnter={handlePointerEnter}
        onPointerLeave={handlePointerLeave}
      >
        <sphereGeometry args={[0.09, 10, 10]} />
        <meshStandardMaterial color={satColorHex} emissive={satColorHex} emissiveIntensity={0.3} metalness={0.2} roughness={0.5} />
      </mesh>

      {/* Glow — lower segment count */}
      <mesh ref={glowRef}>
        <sphereGeometry args={[0.09, 8, 8]} />
        <meshBasicMaterial color={satColorHex} transparent opacity={0.05} blending={THREE.AdditiveBlending} depthWrite={false} />
      </mesh>

      {/* Halo ring — only rendered for special satellites */}
      <mesh ref={haloRef} visible={false}>
        <ringGeometry args={[0.16, 0.22, 24]} />
        <meshBasicMaterial color={satColorHex} transparent opacity={0.4} blending={THREE.AdditiveBlending} depthWrite={false} side={THREE.DoubleSide} />
      </mesh>

      {/* Point light — zero cost when intensity=0 */}
      <pointLight ref={lightRef} color={satColorHex} distance={2} decay={2} intensity={0} />

      {/* Label — only for hovered/src/dst, not all route nodes */}
      {(isSource || isDest || isHovered) && (
        <group position={[0, 0, 0]}>
          {/* We use a simple sprite-based label instead of heavy Text component */}
        </group>
      )}
    </group>
  );
}
