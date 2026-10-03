import React, { useState, useEffect } from 'react';
import axios from 'axios';

const QueuePanel = () => {
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch the current triage queue
    fetch('/queue')
      .then((res) => res.json())
      .then((data) => {
        setQueue(data.queue || []);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to fetch queue:', err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="p-4 text-sm text-gray-600">
        Loading queue...
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h2 className="font-semibold text-lg">Triage Queue</h2>
      {queue.length === 0 && (
        <p className="text-sm text-gray-500">No active calls</p>
      )}
      {queue.map((call, i) => (
        <div
          key={call.id}
          className="p-3 bg-white rounded border-l-4 border-emergency"
        >
          <div className="flex justify-between items-start">
            <div>
              <p className="font-medium">{call.type}</p>
              <p className="text-sm text-gray-500">Destination: {call.dst}</p>
            </div>
            <span 
              className="badge badge-danger"
            >
              Severity {call.severity}
            </span>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            ETA: {call.eta}s - {call.path?.length ? call.path.length + ' hops' : 'calculating...'}
          </p>
        </div>
      ))}
    </div>
  );
};

export default QueuePanel;