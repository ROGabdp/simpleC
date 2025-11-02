/**
 * 壓力等高線圖組件
 */
import React from 'react';
import Plot from 'react-plotly.js';

function PressureContour({ results }) {
  if (!results) return null;

  const data = [
    {
      type: 'contour',
      z: results.pressure,
      x: results.x_coords,
      y: results.y_coords,
      colorscale: 'Viridis',
      colorbar: {
        title: '壓力',
      },
      contours: {
        coloring: 'heatmap',
      },
    },
  ];

  const layout = {
    title: '壓力等高線圖',
    xaxis: {
      title: 'X',
    },
    yaxis: {
      title: 'Y',
      scaleanchor: 'x',
      scaleratio: 1,
    },
    width: 600,
    height: 500,
  };

  return <Plot data={data} layout={layout} />;
}

export default PressureContour;
