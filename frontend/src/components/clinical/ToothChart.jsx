import React, { useState } from 'react';
import './ToothChart.css';

/**
 * ToothChart Component
 * 
 * Interactive dental chart showing all 32 teeth with FDI notation
 * Supports marking conditions, treatments, and AI recommendations
 */
const ToothChart = ({ conditions = {}, onToothClick, readOnly = false }) => {
  const [selectedTooth, setSelectedTooth] = useState(null);
  const [hoveredTooth, setHoveredTooth] = useState(null);

  // FDI Tooth Numbering System (International)
  // Quadrant 1 (Upper Right): 11-18
  // Quadrant 2 (Upper Left): 21-28
  // Quadrant 3 (Lower Left): 31-38
  // Quadrant 4 (Lower Right): 41-48
  
  const teeth = {
    upperRight: [18, 17, 16, 15, 14, 13, 12, 11],
    upperLeft: [21, 22, 23, 24, 25, 26, 27, 28],
    lowerLeft: [38, 37, 36, 35, 34, 33, 32, 31],
    lowerRight: [41, 42, 43, 44, 45, 46, 47, 48],
  };

  const toothTypes = {
    // Molars
    18: 'molar', 17: 'molar', 16: 'molar',
    28: 'molar', 27: 'molar', 26: 'molar',
    38: 'molar', 37: 'molar', 36: 'molar',
    48: 'molar', 47: 'molar', 46: 'molar',
    // Premolars
    15: 'premolar', 14: 'premolar',
    25: 'premolar', 24: 'premolar',
    35: 'premolar', 34: 'premolar',
    45: 'premolar', 44: 'premolar',
    // Canines
    13: 'canine', 23: 'canine', 33: 'canine', 43: 'canine',
    // Incisors
    12: 'incisor', 11: 'incisor',
    22: 'incisor', 21: 'incisor',
    32: 'incisor', 31: 'incisor',
    42: 'incisor', 41: 'incisor',
  };

  const getToothCondition = (toothNumber) => {
    return conditions[toothNumber] || null;
  };

  const getToothColor = (toothNumber) => {
    const condition = getToothCondition(toothNumber);
    if (!condition) return '#ffffff';
    
    const colorMap = {
      'healthy': '#4ade80',
      'cavity': '#fbbf24',
      'root_canal': '#f87171',
      'crown': '#60a5fa',
      'filling': '#a78bfa',
      'extraction': '#9ca3af',
      'missing': '#e5e7eb',
      'ai_flagged': '#fb923c',
    };
    
    return colorMap[condition.status] || '#ffffff';
  };

  const handleToothClick = (toothNumber) => {
    if (readOnly) return;
    setSelectedTooth(toothNumber);
    if (onToothClick) {
      onToothClick(toothNumber, getToothCondition(toothNumber));
    }
  };

  const ToothSVG = ({ number, type, x, y }) => {
    const condition = getToothCondition(number);
    const isSelected = selectedTooth === number;
    const isHovered = hoveredTooth === number;
    const fillColor = getToothColor(number);
    
    // Different shapes for different tooth types
    const shapes = {
      molar: (
        <rect
          x={x}
          y={y}
          width="40"
          height="50"
          rx="8"
          fill={fillColor}
          stroke={isSelected ? '#667eea' : (isHovered ? '#764ba2' : '#d1d5db')}
          strokeWidth={isSelected ? '3' : (isHovered ? '2' : '1')}
        />
      ),
      premolar: (
        <rect
          x={x}
          y={y}
          width="35"
          height="45"
          rx="6"
          fill={fillColor}
          stroke={isSelected ? '#667eea' : (isHovered ? '#764ba2' : '#d1d5db')}
          strokeWidth={isSelected ? '3' : (isHovered ? '2' : '1')}
        />
      ),
      canine: (
        <path
          d={`M ${x} ${y + 45} L ${x + 17.5} ${y} L ${x + 35} ${y + 45} Z`}
          fill={fillColor}
          stroke={isSelected ? '#667eea' : (isHovered ? '#764ba2' : '#d1d5db')}
          strokeWidth={isSelected ? '3' : (isHovered ? '2' : '1')}
        />
      ),
      incisor: (
        <rect
          x={x}
          y={y}
          width="30"
          height="40"
          rx="4"
          fill={fillColor}
          stroke={isSelected ? '#667eea' : (isHovered ? '#764ba2' : '#d1d5db')}
          strokeWidth={isSelected ? '3' : (isHovered ? '2' : '1')}
        />
      ),
    };

    return (
      <g
        className={`tooth ${readOnly ? '' : 'interactive'}`}
        onClick={() => handleToothClick(number)}
        onMouseEnter={() => setHoveredTooth(number)}
        onMouseLeave={() => setHoveredTooth(null)}
        style={{ cursor: readOnly ? 'default' : 'pointer' }}
      >
        {shapes[type]}
        <text
          x={x + (type === 'incisor' ? 15 : type === 'premolar' ? 17.5 : 20)}
          y={y + (type === 'canine' ? 30 : 28)}
          textAnchor="middle"
          fontSize="12"
          fontWeight="600"
          fill="#374151"
        >
          {number}
        </text>
        {condition?.aiRecommended && (
          <circle
            cx={x + (type === 'incisor' ? 25 : type === 'premolar' ? 30 : 35)}
            cy={y + 5}
            r="4"
            fill="#fb923c"
          />
        )}
      </g>
    );
  };

  return (
    <div className="tooth-chart-container">
      <div className="tooth-chart-header">
        <h3>🦷 Dental Chart</h3>
        <div className="chart-legend">
          <div className="legend-item">
            <span className="legend-color" style={{ background: '#4ade80' }}></span>
            <span>Healthy</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ background: '#fbbf24' }}></span>
            <span>Cavity</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ background: '#f87171' }}></span>
            <span>Root Canal</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ background: '#60a5fa' }}></span>
            <span>Crown</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ background: '#fb923c' }}></span>
            <span className="ai-badge-small">AI</span>
            <span>AI Flagged</span>
          </div>
        </div>
      </div>

      <svg
        className="tooth-chart-svg"
        viewBox="0 0 800 500"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Upper Jaw */}
        <g className="upper-jaw">
          {/* Upper Right Quadrant */}
          <g className="quadrant upper-right">
            {teeth.upperRight.map((tooth, index) => (
              <ToothSVG
                key={tooth}
                number={tooth}
                type={toothTypes[tooth]}
                x={50 + index * 50}
                y={50}
              />
            ))}
          </g>
          
          {/* Upper Left Quadrant */}
          <g className="quadrant upper-left">
            {teeth.upperLeft.map((tooth, index) => (
              <ToothSVG
                key={tooth}
                number={tooth}
                type={toothTypes[tooth]}
                x={450 + index * 50}
                y={50}
              />
            ))}
          </g>
        </g>

        {/* Center Line */}
        <line
          x1="400"
          y1="30"
          x2="400"
          y2="470"
          stroke="#d1d5db"
          strokeWidth="2"
          strokeDasharray="5,5"
        />

        {/* Lower Jaw */}
        <g className="lower-jaw">
          {/* Lower Left Quadrant */}
          <g className="quadrant lower-left">
            {teeth.lowerLeft.map((tooth, index) => (
              <ToothSVG
                key={tooth}
                number={tooth}
                type={toothTypes[tooth]}
                x={450 + index * 50}
                y={300}
              />
            ))}
          </g>
          
          {/* Lower Right Quadrant */}
          <g className="quadrant lower-right">
            {teeth.lowerRight.map((tooth, index) => (
              <ToothSVG
                key={tooth}
                number={tooth}
                type={toothTypes[tooth]}
                x={50 + index * 50}
                y={300}
              />
            ))}
          </g>
        </g>

        {/* Labels */}
        <text x="225" y="30" textAnchor="middle" fontSize="14" fontWeight="600" fill="#6b7280">
          Upper Right
        </text>
        <text x="625" y="30" textAnchor="middle" fontSize="14" fontWeight="600" fill="#6b7280">
          Upper Left
        </text>
        <text x="625" y="490" textAnchor="middle" fontSize="14" fontWeight="600" fill="#6b7280">
          Lower Left
        </text>
        <text x="225" y="490" textAnchor="middle" fontSize="14" fontWeight="600" fill="#6b7280">
          Lower Right
        </text>
      </svg>

      {/* Tooth Details Panel */}
      {selectedTooth && (
        <div className="tooth-details-panel">
          <div className="tooth-details-header">
            <h4>Tooth #{selectedTooth}</h4>
            <button onClick={() => setSelectedTooth(null)}>✕</button>
          </div>
          <div className="tooth-details-content">
            {getToothCondition(selectedTooth) ? (
              <>
                <div className="detail-row">
                  <span className="detail-label">Status:</span>
                  <span className="detail-value">{getToothCondition(selectedTooth).status}</span>
                </div>
                {getToothCondition(selectedTooth).notes && (
                  <div className="detail-row">
                    <span className="detail-label">Notes:</span>
                    <span className="detail-value">{getToothCondition(selectedTooth).notes}</span>
                  </div>
                )}
                {getToothCondition(selectedTooth).aiRecommended && (
                  <div className="ai-recommendation">
                    <span className="ai-badge">🤖 AI Recommendation</span>
                    <p>{getToothCondition(selectedTooth).aiRecommendation}</p>
                  </div>
                )}
              </>
            ) : (
              <p className="no-condition">No conditions recorded for this tooth.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ToothChart;

