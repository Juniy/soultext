import React, { useRef, useEffect, useState, useCallback } from "react";

const NODE_COLORS = {
  character: "#8080ff",
  location: "#50c878",
  scene: "#ff8c42",
  chapter: "#ff6b6b",
  event: "#ffd700",
  world_item: "#c084fc",
  timeline_era: "#f472b6",
};

const NODE_SIZES = {
  character: 18,
  location: 14,
  scene: 12,
  chapter: 10,
  event: 16,
  world_item: 12,
  timeline_era: 10,
};

export default function GraphView({ nodes = {}, edges = [], width = 700, height = 500 }) {
  const canvasRef = useRef(null);
  const animRef = useRef(null);
  const [hoveredNode, setHoveredNode] = useState(null);
  const [draggedNode, setDraggedNode] = useState(null);

  const nodeList = useCallback(() => {
    return Object.entries(nodes).map(([id, data]) => ({
      id,
      label: data.name || data.title || id,
      type: data.node_type || "character",
      x: Math.random() * width * 0.6 + width * 0.2,
      y: Math.random() * height * 0.6 + height * 0.2,
      vx: 0,
      vy: 0,
    }));
  }, [nodes, width, height]);

  const [positions, setPositions] = useState([]);

  useEffect(() => {
    setPositions(nodeList());
  }, [nodeList]);

  useEffect(() => {
    if (positions.length === 0) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let running = true;

    const simulate = () => {
      if (!running) return;
      const nodeMap = {};
      const list = positions.map((n) => {
        nodeMap[n.id] = n;
        return { ...n };
      });

      for (let i = 0; i < list.length; i++) {
        for (let j = i + 1; j < list.length; j++) {
          const a = list[i];
          const b = list[j];
          const dx = b.x - a.x;
          const dy = b.y - a.y;
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;

          const repulsion = 5000 / (dist * dist);
          const rfx = (dx / dist) * repulsion;
          const rfy = (dy / dist) * repulsion;
          a.vx -= rfx;
          a.vy -= rfy;
          b.vx += rfx;
          b.vy += rfy;
        }
      }

      for (const edge of edges) {
        const s = nodeMap[edge.source];
        const t = nodeMap[edge.target];
        if (!s || !t) continue;
        const dx = t.x - s.x;
        const dy = t.y - s.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const attraction = dist * 0.005;
        const afx = (dx / dist) * attraction;
        const afy = (dy / dist) * attraction;
        s.vx += afx;
        s.vy += afy;
        t.vx -= afx;
        t.vy -= afy;
      }

      const centerX = width / 2;
      const centerY = height / 2;
      for (const n of list) {
        n.vx += (centerX - n.x) * 0.001;
        n.vy += (centerY - n.y) * 0.001;
        n.vx *= 0.95;
        n.vy *= 0.95;
        n.x += n.vx;
        n.y += n.vy;
        n.x = Math.max(30, Math.min(width - 30, n.x));
        n.y = Math.max(30, Math.min(height - 30, n.y));
      }

      setPositions(list);
      animRef.current = requestAnimationFrame(simulate);
    };

    animRef.current = requestAnimationFrame(simulate);
    return () => {
      running = false;
      if (animRef.current) cancelAnimationFrame(animRef.current);
    };
  }, [positions.length, edges, width, height]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || positions.length === 0) return;
    const ctx = canvas.getContext("2d");

    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = "rgba(17, 17, 34, 0.95)";
    ctx.fillRect(0, 0, width, height);

    const nodeMap = {};
    for (const n of positions) nodeMap[n.id] = n;

    for (const edge of edges) {
      const s = nodeMap[edge.source];
      const t = nodeMap[edge.target];
      if (!s || !t) continue;
      ctx.beginPath();
      ctx.moveTo(s.x, s.y);
      ctx.lineTo(t.x, t.y);
      ctx.strokeStyle = "rgba(100, 100, 200, 0.25)";
      ctx.lineWidth = 1;
      ctx.stroke();

      const midX = (s.x + t.x) / 2;
      const midY = (s.y + t.y) / 2;
      ctx.fillStyle = "rgba(150, 150, 200, 0.5)";
      ctx.font = "9px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(edge.type || "", midX, midY - 4);
    }

    for (const n of positions) {
      const color = NODE_COLORS[n.type] || "#888";
      const size = NODE_SIZES[n.type] || 10;
      const isHovered = hoveredNode === n.id;

      ctx.beginPath();
      ctx.arc(n.x, n.y, isHovered ? size + 4 : size, 0, Math.PI * 2);
      ctx.fillStyle = isHovered ? color : color + "cc";
      ctx.fill();
      if (isHovered) {
        ctx.strokeStyle = "#fff";
        ctx.lineWidth = 2;
        ctx.stroke();
      }

      ctx.fillStyle = "#e0e0e0";
      ctx.font = "11px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(n.label, n.x, n.y + size + 14);
    }

    if (hoveredNode && nodeMap[hoveredNode]) {
      const n = nodeMap[hoveredNode];
      ctx.fillStyle = "rgba(0, 0, 0, 0.75)";
      ctx.fillRect(10, 10, 200, 60);
      ctx.fillStyle = "#fff";
      ctx.font = "12px sans-serif";
      ctx.textAlign = "left";
      ctx.fillText("名称: " + n.label, 18, 28);
      ctx.fillText("类型: " + n.type, 18, 44);
      ctx.fillText("ID: " + n.id, 18, 60);
    }

    ctx.fillStyle = "rgba(100, 100, 150, 0.3)";
    ctx.font = "11px sans-serif";
    ctx.textAlign = "left";
    ctx.fillText(`??: ${positions.length}  ??: ${edges.length}`, 10, height - 10);
  }, [positions, edges, hoveredNode, width, height]);

  const getMousePos = (e) => {
    const rect = canvasRef.current.getBoundingClientRect();
    return {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    };
  };

  const handleMouseMove = (e) => {
    const pos = getMousePos(e);
    let found = null;
    for (const n of positions) {
      const dx = pos.x - n.x;
      const dy = pos.y - n.y;
      if (dx * dx + dy * dy < 400) {
        found = n.id;
        break;
      }
    }
    setHoveredNode(found);
  };

  return (
    <div className="relative rounded-lg overflow-hidden border border-gray-800">
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        onMouseMove={handleMouseMove}
        onMouseLeave={() => setHoveredNode(null)}
        className="w-full cursor-pointer"
      />
      <div className="absolute top-3 right-3 flex flex-wrap gap-2">
        {Object.entries(NODE_COLORS).map(([type, color]) => (
          <div key={type} className="flex items-center gap-1 text-xs text-gray-400">
            <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }} />
            <span>{type}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
