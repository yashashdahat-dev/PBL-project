import { create } from 'zustand';

export type Intent = string;

export interface SatCoords {
  lat: number;   // degrees
  lon: number;   // degrees
  alt: number;   // km above Earth surface
}

export interface SimulationState {
  source: string;
  destination: string;
  intent: Intent;
  activeRoute: string[];
  satellites: { id: string; status: string }[];
  links: [string, string][];
  failedLinks: Set<string>;
  failedSatellites: Set<string>;
  events: { text: string; type: 'route' | 'failure' | 'recovery' | 'info'; ts: number }[];
  hoveredSatellite: string | null;
  // Live coordinate map — updated every frame for hovered/selected satellites
  satelliteCoords: Record<string, SatCoords>;

  setSource: (id: string) => void;
  setDestination: (id: string) => void;
  setIntent: (intent: Intent) => void;
  setActiveRoute: (route: string[]) => void;
  setSatellites: (sats: { id: string; status: string }[]) => void;
  setLinks: (links: [string, string][]) => void;
  addEvent: (text: string, type: 'route' | 'failure' | 'recovery' | 'info') => void;
  addFailedLink: (key: string) => void;
  removeFailedLink: (key: string) => void;
  addFailedSatellite: (id: string) => void;
  removeFailedSatellite: (id: string) => void;
  setHoveredSatellite: (id: string | null) => void;
  updateSatCoords: (id: string, coords: SatCoords) => void;
}

export const useSimulationStore = create<SimulationState>((set) => ({
  source: '',
  destination: '',
  intent: 'CRITICAL_DISASTER',
  activeRoute: [],
  satellites: [],
  links: [],
  failedLinks: new Set(),
  failedSatellites: new Set(),
  events: [],
  hoveredSatellite: null,
  satelliteCoords: {},

  setSource: (id) => set({ source: id }),
  setDestination: (id) => set({ destination: id }),
  setIntent: (intent) => set({ intent }),
  setActiveRoute: (activeRoute) => set({ activeRoute }),
  setSatellites: (satellites) => set({ satellites }),
  setLinks: (links) => set({ links }),
  addEvent: (text, type) =>
    set((state) => ({
      events: [{ text, type, ts: Date.now() }, ...state.events].slice(0, 10),
    })),
  addFailedLink: (key) =>
    set((state) => ({ failedLinks: new Set([...state.failedLinks, key]) })),
  removeFailedLink: (key) =>
    set((state) => {
      const s = new Set(state.failedLinks);
      s.delete(key);
      return { failedLinks: s };
    }),
  addFailedSatellite: (id) =>
    set((state) => ({ failedSatellites: new Set([...state.failedSatellites, id]) })),
  removeFailedSatellite: (id) =>
    set((state) => {
      const s = new Set(state.failedSatellites);
      s.delete(id);
      return { failedSatellites: s };
    }),
  setHoveredSatellite: (id) => set({ hoveredSatellite: id }),
  updateSatCoords: (id, coords) =>
    set((state) => ({ satelliteCoords: { ...state.satelliteCoords, [id]: coords } })),
}));

// I-MACSI: All 11 standard intents with distinct colors
export const intentColors: Record<string, string> = {
  LOW_LATENCY: '#00e5ff',
  CRITICAL_DISASTER: '#ff6b35',
  EARTH_OBSERVATION: '#00b4d8',
  SECURE_MISSION: '#c77dff',
  ENVIRONMENTAL_MONITORING: '#66bb6a',
  AUTONOMOUS_MARITIME: '#26c6da',
  MILITARY_RECONNAISSANCE: '#ef5350',
  GLOBAL_INTERNET: '#42a5f5',
  REMOTE_HEALTHCARE: '#ff7043',
  PRECISION_AGRI: '#9ccc65',
  INDUSTRIAL_IOT: '#ffa726',
};

export const intentLabels: Record<string, string> = {
  LOW_LATENCY: 'Low Latency',
  CRITICAL_DISASTER: 'Disaster',
  EARTH_OBSERVATION: 'Earth Obs',
  SECURE_MISSION: 'Secure',
  ENVIRONMENTAL_MONITORING: 'Env Monitor',
  AUTONOMOUS_MARITIME: 'Maritime',
  MILITARY_RECONNAISSANCE: 'Military',
  GLOBAL_INTERNET: 'Internet',
  REMOTE_HEALTHCARE: 'Healthcare',
  PRECISION_AGRI: 'Agriculture',
  INDUSTRIAL_IOT: 'IoT',
};
