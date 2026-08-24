import { create } from 'zustand';

export type Intent = 'CRITICAL_DISASTER' | 'EARTH_OBSERVATION' | 'SECURE_MISSION';

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

export const intentColors: Record<Intent, string> = {
  CRITICAL_DISASTER: '#ff6b35',
  EARTH_OBSERVATION: '#00b4d8',
  SECURE_MISSION: '#c77dff',
};

export const intentLabels: Record<Intent, string> = {
  CRITICAL_DISASTER: 'Critical Disaster',
  EARTH_OBSERVATION: 'Earth Observation',
  SECURE_MISSION: 'Secure Mission',
};
