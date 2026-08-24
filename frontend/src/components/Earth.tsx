import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

// Pre-bake the Earth texture on a canvas so the shader only runs ONCE
// instead of executing per-pixel per-frame on the GPU.
function generateEarthTexture(size = 512): THREE.CanvasTexture {
  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d')!;

  // Seeded pseudo-random
  const hash = (x: number, y: number): number => {
    const n = Math.sin(x * 127.1 + y * 311.7) * 43758.5453;
    return n - Math.floor(n);
  };
  const noise = (x: number, y: number): number => {
    const ix = Math.floor(x), iy = Math.floor(y);
    const fx = x - ix, fy = y - iy;
    const ux = fx * fx * (3 - 2 * fx);
    const uy = fy * fy * (3 - 2 * fy);
    const a = hash(ix, iy), b = hash(ix + 1, iy);
    const c = hash(ix, iy + 1), d = hash(ix + 1, iy + 1);
    return a + (b - a) * ux + (c - a) * uy + (d - a + a - b - c + b + c - d) * ux * uy;
  };
  const fbm = (x: number, y: number, octaves = 4): number => {
    let v = 0, a = 0.5;
    let px = x, py = y;
    for (let i = 0; i < octaves; i++) {
      v += a * noise(px, py);
      px = px * 2.1 + 1.7; py = py * 2.1 + 9.2;
      a *= 0.5;
    }
    return v;
  };

  const img = ctx.createImageData(size, size);
  const data = img.data;

  for (let py = 0; py < size; py++) {
    for (let px = 0; px < size; px++) {
      const u = px / size;
      const v = py / size;

      // Latitude from UV
      const lat = (v - 0.5) * Math.PI;
      const latAbs = Math.abs(Math.sin(lat));

      const land = fbm(u * 6 + 2.3, v * 6 + 1.7);
      const isLand = land > 0.47;
      const isIce = latAbs > 0.88;

      let r, g, b;
      if (isIce) {
        r = 210; g = 228; b = 248;
      } else if (isLand) {
        const desert = fbm(u * 8 + 5.1, v * 8 + 3.3);
        if (desert > 0.54) {
          r = 155; g = 118; b = 60;  // desert
        } else {
          r = 34; g = 85; b = 25;    // forest
        }
      } else {
        const shallow = fbm(u * 12, v * 12) * 0.5;
        r = Math.round(8 + shallow * 10);
        g = Math.round(40 + shallow * 20);
        b = Math.round(100 + shallow * 40);
      }

      const idx = (py * size + px) * 4;
      data[idx] = r; data[idx + 1] = g; data[idx + 2] = b; data[idx + 3] = 255;
    }
  }
  ctx.putImageData(img, 0, 0);

  const tex = new THREE.CanvasTexture(canvas);
  tex.needsUpdate = true;
  return tex;
}

function generateCityLightsTexture(size = 512): THREE.CanvasTexture {
  const canvas = document.createElement('canvas');
  canvas.width = size; canvas.height = size;
  const ctx = canvas.getContext('2d')!;
  ctx.fillStyle = 'black';
  ctx.fillRect(0, 0, size, size);

  const hash = (x: number, y: number) => {
    const n = Math.sin(x * 127.1 + y * 311.7) * 43758.5453;
    return n - Math.floor(n);
  };
  const noise = (x: number, y: number) => {
    const ix = Math.floor(x), iy = Math.floor(y);
    const fx = x - ix, fy = y - iy;
    const ux = fx * fx * (3 - 2 * fx), uy = fy * fy * (3 - 2 * fy);
    const a = hash(ix, iy), b = hash(ix+1, iy), c = hash(ix, iy+1), d = hash(ix+1, iy+1);
    return a + (b-a)*ux + (c-a)*uy + (d-a+a-b-c+b+c-d)*ux*uy;
  };
  const fbm = (x: number, y: number) => {
    let v = 0, a = 0.5, px = x, py = y;
    for (let i = 0; i < 3; i++) { v += a*noise(px, py); px=px*2.1+1.7; py=py*2.1+9.2; a*=0.5; }
    return v;
  };

  const img = ctx.createImageData(size, size);
  const data = img.data;
  for (let py = 0; py < size; py++) {
    for (let px = 0; px < size; px++) {
      const u = px / size, v = py / size;
      const land = fbm(u * 6 + 2.3, v * 6 + 1.7);
      const city = Math.pow(Math.max(0, fbm(u * 18 + 8.8, v * 18 + 4.2) - 0.35) * 3, 2) * (land > 0.47 ? 1 : 0);
      const idx = (py * size + px) * 4;
      data[idx] = Math.round(city * 255);
      data[idx+1] = Math.round(city * 210);
      data[idx+2] = Math.round(city * 120);
      data[idx+3] = Math.round(city * 255);
    }
  }
  ctx.putImageData(img, 0, 0);
  const tex = new THREE.CanvasTexture(canvas);
  tex.needsUpdate = true;
  return tex;
}

export default function Earth() {
  const earthRef = useRef<THREE.Mesh>(null);
  const atmosRef = useRef<THREE.Mesh>(null);

  // Generate textures ONCE (CPU, at startup) — never runs on GPU per-frame
  const { earthTex, cityTex } = useMemo(() => ({
    earthTex: generateEarthTexture(512),
    cityTex: generateCityLightsTexture(512),
  }), []);

  // Shader to blend day + city-lights based on sun direction
  const earthMaterial = useMemo(() => new THREE.ShaderMaterial({
    uniforms: {
      uDayTex:  { value: earthTex },
      uCityTex: { value: cityTex },
      uSunDir:  { value: new THREE.Vector3(5, 3, 5).normalize() },
      uRotY:    { value: 0 },
    },
    vertexShader: `
      varying vec3 vNormal;
      varying vec2 vUv;
      void main() {
        vNormal = normalize(normalMatrix * normal);
        vUv = uv;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform sampler2D uDayTex;
      uniform sampler2D uCityTex;
      uniform vec3 uSunDir;
      varying vec3 vNormal;
      varying vec2 vUv;
      void main() {
        float diff = dot(vNormal, uSunDir);
        float daySide = smoothstep(-0.2, 0.3, diff);
        vec4 dayColor  = texture2D(uDayTex,  vUv);
        vec4 cityColor = texture2D(uCityTex, vUv);
        // Apply basic diffuse + ambient to day side
        vec3 lit = dayColor.rgb * (0.08 + 0.92 * max(0.0, diff));
        // Ocean specular
        float spec = pow(max(0.0, diff), 24.0) * 0.12;
        lit += spec * vec3(0.6, 0.8, 1.0);
        // Blend in city lights on night side
        vec3 night = cityColor.rgb * (1.0 - daySide) * 1.8;
        gl_FragColor = vec4(lit * daySide + night, 1.0);
      }
    `,
  }), [earthTex, cityTex]);

  // Atmosphere rim — simple, cheap
  const atmosMaterial = useMemo(() => new THREE.ShaderMaterial({
    uniforms: { uSunDir: { value: new THREE.Vector3(5, 3, 5).normalize() } },
    vertexShader: `
      varying vec3 vNormal; varying vec3 vViewDir;
      void main() {
        vNormal = normalize(normalMatrix * normal);
        vViewDir = normalize(-(modelViewMatrix * vec4(position,1.0)).xyz);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0);
      }
    `,
    fragmentShader: `
      uniform vec3 uSunDir;
      varying vec3 vNormal; varying vec3 vViewDir;
      void main() {
        float rim = 1.0 - max(0.0, dot(vViewDir, vNormal));
        rim = pow(rim, 3.0);
        float sun = dot(vNormal, uSunDir) * 0.5 + 0.5;
        vec3 col = mix(vec3(0.1,0.3,0.9), vec3(0.4,0.8,1.0), sun);
        gl_FragColor = vec4(col, rim * 0.65);
      }
    `,
    transparent: true,
    side: THREE.BackSide,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  }), []);

  useFrame((_, delta) => {
    // Make rotation speed visible and frame-rate independent
    if (earthRef.current) earthRef.current.rotation.y += delta * 0.025;
  });

  return (
    <group>
      <mesh ref={earthRef} material={earthMaterial}>
        <sphereGeometry args={[3, 64, 64]} />
      </mesh>
      <mesh ref={atmosRef} material={atmosMaterial}>
        <sphereGeometry args={[3.15, 32, 32]} />
      </mesh>
    </group>
  );
}
