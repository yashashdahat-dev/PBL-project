import React from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';
import * as THREE from 'three';
import Earth from './Earth';
import Constellation from './Constellation';

export default function Scene() {
  return (
    <Canvas
      // Cap DPR at 1.5 to halve pixel fill on HiDPI/Retina screens
      dpr={[1, 1.5]}
      camera={{ position: [0, 3, 12], fov: 45 }}
      gl={{
        antialias: true,
        toneMapping: THREE.ACESFilmicToneMapping,
        toneMappingExposure: 1.1,
        powerPreference: 'high-performance',
      }}
      // Only re-render when something changes — but keep always-on for animation
      frameloop="always"
      performance={{ min: 0.5 }}  // allow Three.js to auto-lower DPR if FPS drops
    >
      <color attach="background" args={['#000205']} />

      {/* Minimal lighting — fewer lights = fewer GPU passes */}
      <ambientLight intensity={0.2} />
      <directionalLight position={[5, 3, 5]} intensity={1.8} color="#fff5e0" />
      <directionalLight position={[-8, -3, -8]} intensity={0.15} color="#2040ff" />

      {/* Stars — reduced count for performance */}
      <Stars radius={120} depth={50} count={1000} factor={4} saturation={0.2} fade speed={0.4} />

      <Earth />
      <Constellation />

      <OrbitControls
        enablePan={false}
        enableZoom={true}
        enableRotate={true}
        minDistance={5}
        maxDistance={22}
        autoRotate={true}
        autoRotateSpeed={0.12}
        enableDamping={true}
        dampingFactor={0.06}
        // Throttle camera update events
        regress={true}
      />
    </Canvas>
  );
}

