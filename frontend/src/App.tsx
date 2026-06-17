import { Routes, Route, Navigate } from 'react-router-dom';

export function App() {
  return (
    <Routes>
      <Route path="/" element={<div>ACME Content Workflow</div>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
