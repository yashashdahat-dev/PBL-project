import * as THREE from 'three';

// Mutable store to hold real-time positions of satellites without triggering React re-renders.
export const satellitePositions = new Map<string, THREE.Vector3>();
