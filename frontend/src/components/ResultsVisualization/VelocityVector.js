/**
 * 速度向量圖組件
 */
import React from 'react';
import Plot from 'react-plotly.js';

function VelocityVector({ results }) {
  if (!results) return null;

  // 插值速度場到網格中心點
  const ny = results.pressure.length;
  const nx = results.pressure[0].length;

  // 建立網格座標
  const X = [];
  const Y = [];
  const U = [];
  const V = [];

  // 降採樣以提高性能 (每 3 個點取一個)
  const skip = 3;

  for (let j = 0; j < ny; j += skip) {
    for (let i = 0; i < nx; i += skip) {
      X.push(results.x_coords[i]);
      Y.push(results.y_coords[j]);

      // u 速度插值
      let u_val = 0;
      if (i > 0 && i < nx - 1) {
        u_val = (results.velocity_u[j][i - 1] + results.velocity_u[j][i]) / 2;
      }
      U.push(u_val);

      // v 速度插值
      let v_val = 0;
      if (j > 0 && j < ny - 1) {
        v_val = (results.velocity_v[j - 1][i] + results.velocity_v[j][i]) / 2;
      }
      V.push(v_val);
    }
  }

  const data = [
    {
      type: 'cone',
      x: X,
      y: Y,
      z: Array(X.length).fill(0),
      u: U,
      v: V,
      w: Array(X.length).fill(0),
      sizemode: 'absolute',
      sizeref: 0.5,
      colorscale: 'Portland',
      showscale: true,
      colorbar: {
        title: '速度大小',
      },
    },
  ];

  const layout = {
    title: '速度向量圖',
    scene: {
      xaxis: { title: 'X' },
      yaxis: { title: 'Y' },
      zaxis: { title: '', range: [-0.1, 0.1] },
      camera: {
        eye: { x: 0, y: 0, z: 2.5 },
      },
    },
    width: 600,
    height: 500,
  };

  return <Plot data={data} layout={layout} />;
}

export default VelocityVector;
