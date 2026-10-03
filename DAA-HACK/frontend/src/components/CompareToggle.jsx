import React, { useState } from 'react';
import axios from 'axios';

const CompareToggle = () => {
  const [stats, setStats] = useState({});
  const [showDijkstra, setShowDijkstra] = useState(true);
  const [pathD, setPathD] = useState([]);
  const [pathB, setPathB] = useState([]);
  const [costD, setCostD] = useState(0);
  const [costB, setCostB] = useState(0);

  const computeComparison = async (dst) => {
    if (!dst) return;

    // Run Dijkstra
    try {
      const r1 = await axios.post('/route', {
        src: 'N01',
        dst: dst,
        algo: 'dijkstra',
      });
      setPathD(r1.data.path);
      setCostD(r1.data.cost);
      setStats({ ...stats, nodesD: r1.data.stats.nodes_settled, edgesD: r1.data.stats.edges_relaxed });
    } catch (e) {
      setPathD([]);
      setCostD(0);
    }

    // Run BFS
    try {
      const r2 = await axios.post('/route', {
        src: 'N01',
        dst: dst,
        algo: 'bfs',
      });
      setPathB(r2.data.path);
      setCostB(r2.data.cost);
      setStats({ ...stats, nodesB: r2.data.stats.nodes_settled, edgesB: r2.data.stats.edges_relaxed });
    } catch (e) {
      setPathB([]);
      setCostB(0);
    }
  };

  return (
    <div className="p-4 bg-white rounded border border-gray-200">
      <h2 className="font-semibold text-sm mb-3">Dijkstra vs BFS Comparison</h2>
      
      <div className="mb-3">
        <label className="mr-2">
          <input
            type="radio"
            checked={showDijkstra}
            onChange={() => setShowDijkstra(true)}
            className="radio-emergency"
          />
          Dijkstra
        </label>
        <label className="mr-2 ml-4">
          <input
            type="radio"
            checked={!showDijkstra}
            onChange={() => setShowDijkstra(false)}
            className="radio-emergency"
          />
          BFS
        </label>
      </div>

      {showDijkstra ? (
        <div className="mb-3">
          <p className="font-medium text-emergency">Dijkstra Path:</p>
          <p className="monospace mt-1">{pathD.join(' → ') || 'No path'}</p>
          <p className="mt-1">Cost: {costD}s</p>
          <p className="text-sm text-gray-500">Nodes settled: {stats.nodesD || '-'}</p>
          <p className="text-sm text-gray-500">Edges relaxed: {stats.edgesD || '-'}</p>
        </div>
      ) : (
        <div className="mb-3">
          <p className="font-medium text-emergency">BFS Path:</p>
          <p className="monospace mt-1">{pathB.join(' → ') || 'No path'}</p>
          <p className="mt-1">Hops: {costB}</p>
          <p className="text-sm text-gray-500">Nodes settled: {stats.nodesB || '-'}</p>
          <p className="text-sm text-gray-500">Edges relaxed: {stats.edgesB || '-'}</p>
        </div>
      )}

      <div>
        <p className="font-medium mt-2">Takeaway:</p>
        <p className="mt-1 text-sm text-gray-600">
          {pathD.length && pathB.length
            ? 'Dijkstra finds minimum-total-weight path; BFS finds minimum-hop path. Weights vary across corridors.'
            : 'Select a destination to compare'}
        </p>
      </div>
    </div>
  );
};

export default CompareToggle;