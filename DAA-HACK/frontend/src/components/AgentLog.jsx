import React, { useState, useEffect } from 'react';

const AgentLog = () => {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    // Fetch the event stream from the backend
    const evtSource = new EventSource('/event_stream');
    
    evtSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setEvents((prev) => {
        // Keep last 50 events, add to top
        const newEvents = [{ timestamp: new Date().toLocaleTimeString(), ...data }];
        return [...newEvents, ...prev].slice(0, 50);
      });
    };

    evtSource.onerror = (e) => {
      console.error('Event source error', e);
      // Fallback: poll every 2 seconds
      const interval = setInterval(() => {
        fetch('/agent_log')
          .then((res) => res.json())
          .then((data) => {
            setEvents((prev) => {
              const newEvents = [{ timestamp: new Date().toLocaleTimeString(), ...data }];
              return [...newEvents, ...prev].slice(0, 50);
            });
          });
      }, 2000);
      return () => clearInterval(interval);
    };

    return () => evtSource.close();
  }, []);

  // Sort events by time, latest first
  const sortedEvents = events.sort((a, b) => b.timestamp.localeCompare(a.timestamp));

  return (
    <div className="space-y-1 max-h-80 overflow-auto">
      {sortedEvents.map((event, i) => (
        <div
          key={i}
          className="p-2 rounded text-xs monospace bg-gray-900 text-white"
        >
          [{event.timestamp}] {event.message}
        </div>
      ))}
      {/* Auto-scroll to bottom */}
      <script
        dangerouslySetInnerHTML={{
          __html: `
            const container = document.querySelector('div[class*="overflow-auto"]');
            if (container) {
              container.scrollTop = container.scrollHeight;
            }
          `,
        }}
      />
    </div>
  );
};

export default AgentLog;