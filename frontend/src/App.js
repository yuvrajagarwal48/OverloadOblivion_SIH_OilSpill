import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ShipTrackingDashboard from './components/ShipTrackingDashboard';
import Home from './components/Homepage';
import ReportsPage from './components/Reports'
import Sidebar from './components/Sidebar';

const App = () => {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <Sidebar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/tracking" element={<ShipTrackingDashboard />} />
          <Route path="/reports" element={<ReportsPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
};

export default App;