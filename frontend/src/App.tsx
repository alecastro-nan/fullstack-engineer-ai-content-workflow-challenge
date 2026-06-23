import { Navigate, Route, Routes } from 'react-router-dom';
import { CampaignDashboard } from './pages/CampaignDashboard';

export function App() {
  return (
    <Routes>
      <Route path="/" element={<CampaignDashboard />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
