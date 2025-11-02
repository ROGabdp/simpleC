/**
 * 中心線速度分佈圖組件
 */
import React from 'react';
import Plot from 'react-plotly.js';

function CenterlineProfile({ results }) {
  if (!results) return null;

  const ny = results.pressure.length;
  const nx = results.pressure[0].length;

  // 垂直中心線的 u 速度
  const centerX = Math.floor(nx / 2);
  const uVertical = [];
  for (let j = 0; j < ny; j++) {
    let u_val = 0;
    if (centerX > 0 && centerX < results.velocity_u[0].length) {
      u_val = (results.velocity_u[j][centerX - 1] + results.velocity_u[j][centerX]) / 2;
    }
    uVertical.push(u_val);
  }

  // 水平中心線的 v 速度
  const centerY = Math.floor(ny / 2);
  const vHorizontal = [];
  for (let i = 0; i < nx; i++) {
    let v_val = 0;
    if (centerY > 0 && centerY < results.velocity_v.length) {
      v_val = (results.velocity_v[centerY - 1][i] + results.velocity_v[centerY][i]) / 2;
    }
    vHorizontal.push(v_val);
  }

  const data = [
    {
      type: 'scatter',
      x: uVertical,
      y: results.y_coords,
      mode: 'lines+markers',
      name: 'U 速度 (x=0.5)',
      line: { color: 'blue' },
      marker: { size: 4 },
    },
  ];

  const data2 = [
    {
      type: 'scatter',
      x: results.x_coords,
      y: vHorizontal,
      mode: 'lines+markers',
      name: 'V 速度 (y=0.5)',
      line: { color: 'red' },
      marker: { size: 4 },
    },
  ];

  const layout1 = {
    title: 'U 速度沿垂直中心線分佈',
    xaxis: { title: 'U 速度' },
    yaxis: { title: 'Y' },
    width: 600,
    height: 400,
  };

  const layout2 = {
    title: 'V 速度沿水平中心線分佈',
    xaxis: { title: 'X' },
    yaxis: { title: 'V 速度' },
    width: 600,
    height: 400,
  };

  return (
    <div>
      <Plot data={data} layout={layout1} />
      <Plot data={data2} layout={layout2} />
    </div>
  );
}

export default CenterlineProfile;
