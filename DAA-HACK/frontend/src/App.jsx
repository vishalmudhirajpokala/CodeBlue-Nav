import React, { useState, useEffect, useRef } from 'react';
import HospitalMap from './components/HospitalMap';
import RouteLayer from './components/RouteLayer';
import QueuePanel from './components/QueuePanel';
import CompareToggle from './components/CompareToggle';
import EmergencyModal from './components/EmergencyModal';
import AgentLog from './components/AgentLog';

const App = () => {
  const [showModal, setShowModal] = useState(false);
  const [agentLog, setAgentLog] = useState([]);

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <header className="bg-white border-b border-gray-200 p-4">
        <h1 className="text-2xl font-bold">CodeBlue Nav - Hospital Emergency Route Engine</h1>
      </header>

      <main className="p-4 flex gap-4">
        {/* Left panel: Map and route rendering */}
        <div className="w-3/4 flex flex-col gap-4">
          <HospitalMap />
          <RouteLayer />
          <EmergencyModal setShowModal={setShowModal} />
        </div>

        {/* Right panel: Agent log and queue */}
        <div className="w-1/4 flex flex-col gap-4">
          <AgentLog />
          <QueuePanel />
          <CompareToggle />
        </div>
      </main>

      {/* Global agent log panel */}
      <div className="fixed bottom-4 right-4 w-80 bg-gray-800 text-white p-4 rounded shadow max-h-80 overflow-auto text-sm">
        <h3 className="font-bold mb-2">Agent Decision Log</h3>
        <div className="space-y-2 max-h-64 overflow-auto">
          {agentLog.map((entry, i) => (
            <div key={i} className="p-2 rounded bg-gray-900 mb-1">
              {entry}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default App;