// src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { App } from './App';
// @ts-expect-error CSS is loaded by the bundler; TypeScript has no declaration for it.
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);