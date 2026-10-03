import React, { useState } from 'react';

const EmergencyModal = ({ setShowModal }) => {
  const [type, setType] = useState('');
  const [dst, setDst] = useState('');

  const emergencyCalls = [
    { value: 'Stroke Alert', label: 'Stroke Alert' },
    { value: 'Cardiac Arrest', label: 'Cardiac Arrest' },
    { value: 'Trauma Alert', label: 'Trauma Alert' },
    { value: 'Respiratory Distress', label: 'Respiratory Distress' },
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!type || !dst) return;

    try {
      const response = await fetch('/call', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type, dst }),
      });
      const data = await response.json();
      console.log('Call created:', data);
      // Queue will update automatically
    } catch (err) {
      console.error('Failed to create call:', err);
    } finally {
      setShowModal(false);
      setType('');
      setDst('');
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg p-6 w-full max-w-md shadow-2xl">
        <h2 className="text-2xl font-bold text-emergency mb-4">New Emergency Call</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Call Type</label>
            <select
              value={type}
              onChange={(e) => setType(e.target.value)}
              className="shadow appearance-none rounded border-2 border-emergency py-2 px-3 text-emergency"
            >
              <option value="">Select call type</option>
              {emergencyCalls.map((c) => (
                <option key={c.value} value={c.value}>
                  {c.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Destination</label>
            <select
              value={dst}
              onChange={(e) => setDst(e.target.value)}
              className="shadow appearance-none rounded border-2 border-emergency py-2 px-3 text-emergency"
            >
              <option value="">Select destination</option>
              <option value="N02">ER</option>
              <option value="N03">ICU</option>
              <option value="N04">Ward 4A</option>
              <option value="N05">Ward 4B</option>
              <option value="N06">Imaging</option>
              <option value="N07">Pharmacy</option>
              <option value="N10">OR Block</option>
              <option value="N11">Lab</option>
              <option value="N12">Radiology</option>
              <option value="N13">Lobby</option>
              <option value="N14">Corridor C</option>
            </select>
          </div>

          <button
            type="submit"
            className="w-full py-2.5 bg-emergency text-white font-medium rounded-lg hover:bg-red-600"
          >
            Dispatch
          </button>
        </form>
      </div>
    </div>
  );
};

export default EmergencyModal;