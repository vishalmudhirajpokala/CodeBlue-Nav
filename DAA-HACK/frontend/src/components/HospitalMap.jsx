import React, { useState, useEffect } from 'react';

const HospitalMap = ({ onEdgeClick }) => {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [blockedEdges, setBlockedEdges] = useState(new Set());
  const [nodeRefs, setNodeRefs] = useState({});
  const mapRef = useRef(null);

  useEffect(() => {
    // Fetch graph data from backend
    fetch('/graph')
      .then((res) => res.json())
      .then((data) => {
        setNodes(data.nodes);
        setEdges(data.edges);
      })
      .catch((err) => {
        console.error('Failed to fetch graph:', err);
      });
  }, []);

  // Update blocked edges from parent
  useEffect(() => {
    setBlockedEdges(onEdgeClick ? new Set() : new Set());
  }, [onEdgeClick]);

  const handleEdgeClick = (edgeId) => {
    if (onEdgeClick) {
      onEdgeClick(edgeId);
    }
  };

  // Compute node colors based on type
  const nodeColors = {
    start: '#6366f1',      // blue for start
    er: '#f87171',         // red for ER/ICU
    ward: '#22c55e',       // green for ward
    junction: '#eab308',   // yellow for junction
  };

  if (!nodes.length || !edges.length) {
    return (
      <div className="h-64 border-2 border-dashed border-gray-300 rounded flex items-center justify-center">
        Loading map...
      </div>
    );
  }

  return (
    <div 
      ref={mapRef}
      className="relative h-96 w-full rounded-lg overflow-background bg-gray-100"
      style={{ width: '1000px', height: '600px' }}
    >
      {/* Edges - lines */}
      {edges.map((edge) => {
        const a = nodes.find((n) => n.id === edge.node_a);
        const b = nodes.find((n) => n.id === edge.node_b);
        if (!a || !b) return null;

        const isBlocked = blockedEdges.has(edge.id);
        const stroke = isBlocked ? '#ff0000' : '#64748b';
        const strokeWidth = isBlocked ? '3' : '1';

        return (
          <line
            key={edge.id}
            x1={a.x}
            y1={a.y}
            x2={b.x}
            y2={b.y}
            stroke={stroke}
            strokeWidth={strokeWidth}
            className="cursor-pointer"
            onClick={() => handleEdgeClick(edge.id)}
          />
        );
      })}

      {/* Nodes - circles with labels */}
      {nodes.map((node) => {
        const color = nodeColors[node.type] || '#64748b';
        const isBlocked = blockedEdges.some(
          (e) => e.node_a === node.id || e.node_b === node.id
        );

        return (
          <circle
            key={node.id}
            cx={node.x}
            cy={node.y}
            r={8}
            fill={color}
            className="cursor-pointer select-none"
            style={isBlocked ? { opacity: '0.5' } : {}}
          />
        );
      })}

      {/* Node labels */}
      {nodes.map((node) => {
        return (
          <text
            key={node.id}
            x={node.x}
            y={node.y - 10}
            textAnchor="middle"
            fontSize="10"
            fill={nodeColors[node.type] || '#64748b'}
            className="select-none"
          >
            {node.label}
          </text>
        );
      })}

      {/* Legend */}
      <div className="absolute bottom-left m-2 p-2 bg-white rounded shadow text-xs">
        <div className="mb-1">
          <span className="well-sm rounded-full bg-emergency mr-1 inline-block" />
          <span>ER/ICU</span>
        </div>
        <div className="mb-1">
          <span className="w-well-sm rounded-full bg-ward mr-1 inline-block" />
          <span>Ward</span>
        </div>
        <div>
          <span className="w-well-sm rounded-full bg-junction mr-1 inline-block" />
          <span>Junction</span>
        </div>
      </div>
    </div>
  );
};

export default HospitalMap;