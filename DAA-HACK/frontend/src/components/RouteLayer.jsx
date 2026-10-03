import React, { useState, useEffect } from 'react';

const RouteLayer = ({ path, eta, onEdgeClick }) => {
  if (!path || path.length < 2) {
    return null;
  }

  // Compute the path points from nodes
  const nodeMap = new Map();
  // We'll set this from outside or fetch

  return (
    <div className="relative h-64 w-full rounded-lg overflow-[hidden] bg-gray-100">
      {/* Animated glowing polyline for the path */}
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 1000 600">
        <polyline
          points={path.map((id) => {
            // We need node positions - this is a simplification
            // In a full implementation, we'd have a node position map
            return '500,300'; // placeholder
          })}
          fill="none"
          stroke="#10b981"
          strokeWidth="4"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="animate-pulse"
        />
      </svg>

      {/* ETA readout */}
      <div className="absolute bottom-2 left-1/2 -translate-x-1/2 bg-white/80 backdrop-blur rounded px-4 py-2 text-lg font-medium text-gray-900">
        {eta > 0 ? (
          <div>
            {Math.floor(eta / 60)}m {eta % 60}s
          </div>
        ) : (
          'No route'
        )}
      </div>
    </div>
  );
};

export default RouteLayer;