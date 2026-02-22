import React from 'react';
import { View } from 'react-native';
import Svg, {
  Polygon,
  Circle,
  Line,
  Text as SvgText,
  G,
  Defs,
  RadialGradient,
  Stop
} from 'react-native-svg';

export default function RadarChart({ 
  data, 
  size = 250, 
  maxValue = 10,
  strokeColor = '#4CAF50',
  fillColor = '#4CAF50',
  gridColor = '#333'
}) {
  const center = size / 2;
  const radius = center - 40; // Leave margin for labels
  
  // Convert data object to array with labels
  const dataPoints = Object.entries(data).map(([key, value]) => ({
    label: key.charAt(0).toUpperCase() + key.slice(1),
    value: value,
    shortLabel: getShortLabel(key)
  }));
  
  const numberOfSides = dataPoints.length;
  const angleStep = (2 * Math.PI) / numberOfSides;
  
  // Generate grid polygons (concentric)
  const gridLevels = [2, 4, 6, 8, 10];
  const gridPolygons = gridLevels.map(level => {
    const points = [];
    for (let i = 0; i < numberOfSides; i++) {
      const angle = i * angleStep - Math.PI / 2; // Start from top
      const x = center + (radius * (level / maxValue)) * Math.cos(angle);
      const y = center + (radius * (level / maxValue)) * Math.sin(angle);
      points.push(`${x},${y}`);
    }
    return points.join(' ');
  });
  
  // Generate data polygon
  const dataPolygonPoints = [];
  const labelPositions = [];
  
  for (let i = 0; i < numberOfSides; i++) {
    const angle = i * angleStep - Math.PI / 2;
    const value = dataPoints[i].value;
    const x = center + (radius * (value / maxValue)) * Math.cos(angle);
    const y = center + (radius * (value / maxValue)) * Math.sin(angle);
    dataPolygonPoints.push(`${x},${y}`);
    
    // Calculate label positions (outside the chart)
    const labelRadius = radius + 25;
    const labelX = center + labelRadius * Math.cos(angle);
    const labelY = center + labelRadius * Math.sin(angle);
    
    labelPositions.push({
      x: labelX,
      y: labelY,
      label: dataPoints[i].shortLabel,
      value: dataPoints[i].value,
      angle
    });
  }
  
  const dataPolygon = dataPolygonPoints.join(' ');
  
  // Generate grid lines (from center to vertices)
  const gridLines = [];
  for (let i = 0; i < numberOfSides; i++) {
    const angle = i * angleStep - Math.PI / 2;
    const x = center + radius * Math.cos(angle);
    const y = center + radius * Math.sin(angle);
    gridLines.push({
      x1: center,
      y1: center,
      x2: x,
      y2: y
    });
  }
  
  function getShortLabel(key) {
    const shortcuts = {
      'centering': 'CTR',
      'surface': 'SRF',
      'edges': 'EDG',
      'corners': 'CRN'
    };
    return shortcuts[key.toLowerCase()] || key.slice(0, 3).toUpperCase();
  }
  
  function getGradeColor(value) {
    if (value >= 9) return '#4CAF50';
    if (value >= 8) return '#8BC34A';
    if (value >= 7) return '#FFC107';
    if (value >= 6) return '#FF9800';
    return '#F44336';
  }
  
  return (
    <View style={{ alignItems: 'center' }}>
      <Svg width={size} height={size}>
        <Defs>
          <RadialGradient id="dataFill" cx="50%" cy="50%" r="50%">
            <Stop offset="0%" stopColor={fillColor} stopOpacity="0.3" />
            <Stop offset="100%" stopColor={fillColor} stopOpacity="0.1" />
          </RadialGradient>
        </Defs>
        
        {/* Background Grid Polygons */}
        {gridPolygons.map((points, index) => (
          <Polygon
            key={index}
            points={points}
            fill="none"
            stroke={gridColor}
            strokeWidth="1"
            opacity={0.3}
          />
        ))}
        
        {/* Grid Lines */}
        {gridLines.map((line, index) => (
          <Line
            key={index}
            x1={line.x1}
            y1={line.y1}
            x2={line.x2}
            y2={line.y2}
            stroke={gridColor}
            strokeWidth="1"
            opacity={0.2}
          />
        ))}
        
        {/* Grade Level Labels */}
        {[2, 4, 6, 8, 10].map(level => {
          const labelRadius = (radius * (level / maxValue));
          return (
            <SvgText
              key={level}
              x={center + labelRadius + 5}
              y={center - 3}
              fontSize="10"
              fill="#666"
              opacity={0.7}
            >
              {level}
            </SvgText>
          );
        })}
        
        {/* Data Polygon */}
        <Polygon
          points={dataPolygon}
          fill="url(#dataFill)"
          stroke={strokeColor}
          strokeWidth="2"
        />
        
        {/* Data Points */}
        {dataPolygonPoints.map((point, index) => {
          const [x, y] = point.split(',').map(Number);
          const value = dataPoints[index].value;
          return (
            <Circle
              key={index}
              cx={x}
              cy={y}
              r="4"
              fill={getGradeColor(value)}
              stroke="#ffffff"
              strokeWidth="2"
            />
          );
        })}
        
        {/* Labels and Values */}
        {labelPositions.map((pos, index) => {
          const textAnchor = pos.angle > Math.PI / 2 && pos.angle < (3 * Math.PI) / 2 
            ? 'end' 
            : pos.angle === Math.PI / 2 || pos.angle === (3 * Math.PI) / 2 
              ? 'middle' 
              : 'start';
          
          return (
            <G key={index}>
              {/* Label */}
              <SvgText
                x={pos.x}
                y={pos.y - 5}
                fontSize="12"
                fill="#ffffff"
                textAnchor={textAnchor}
                fontWeight="bold"
              >
                {pos.label}
              </SvgText>
              {/* Value */}
              <SvgText
                x={pos.x}
                y={pos.y + 10}
                fontSize="14"
                fill={getGradeColor(pos.value)}
                textAnchor={textAnchor}
                fontWeight="bold"
              >
                {pos.value}
              </SvgText>
            </G>
          );
        })}
        
        {/* Center Point */}
        <Circle
          cx={center}
          cy={center}
          r="3"
          fill={gridColor}
        />
      </Svg>
    </View>
  );
}