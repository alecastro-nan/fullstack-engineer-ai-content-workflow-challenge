import { Navigate, Route, Routes } from 'react-router-dom';
import { ErrorBoundary } from './components/ErrorBoundary';
import { CampaignDashboard } from './pages/CampaignDashboard';
import { CampaignDetail } from './pages/CampaignDetail';

export function App() {
  return (
    <ErrorBoundary>
      <Routes>
        <Route path="/" element={<CampaignDashboard />} />
        <Route path="/campaigns/:id" element={<CampaignDetail />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </ErrorBoundary>
  );
}
