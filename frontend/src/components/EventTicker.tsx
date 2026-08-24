import React, { useEffect, useRef } from 'react';
import { useSimulationStore } from '../hooks/useSimulationStore';

const typeIcons: Record<string, string> = {
  route: '⟶',
  failure: '✕',
  recovery: '↺',
  info: '◆',
};

const typeColors: Record<string, string> = {
  route: '#64ffda',
  failure: '#ff5252',
  recovery: '#00e676',
  info: '#ffab40',
};

export default function EventTicker() {
  const { events } = useSimulationStore();
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = 0;
    }
  }, [events]);

  return (
    <div className="event-ticker">
      <div className="ticker-header">
        <span className="ticker-dot" />
        LIVE EVENT STREAM
      </div>
      <div className="ticker-list" ref={listRef}>
        {events.length === 0 ? (
          <div className="ticker-empty">Awaiting events…</div>
        ) : (
          events.map((ev, i) => (
            <div
              key={ev.ts}
              className="ticker-item"
              style={{
                color: typeColors[ev.type],
                opacity: Math.max(0.3, 1 - i * 0.08),
                animationDelay: `${i * 0.05}s`,
              }}
            >
              <span className="ticker-icon">{typeIcons[ev.type]}</span>
              <span className="ticker-text">{ev.text}</span>
              <span className="ticker-time">{new Date(ev.ts).toLocaleTimeString()}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
