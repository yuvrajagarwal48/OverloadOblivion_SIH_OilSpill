import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Waves, MapPin, BarChart, Compass, Ship } from 'lucide-react';

const Sidebar = () => {
  const navigate = useNavigate();

  const handleReportClick = () => {
    navigate('/reports');
  };

  const handleShipTrackingClick = () => {
    navigate('/tracking');
  };

  const handleLocationClick = () => {
    navigate('/location');
  };

  return (
    <div className="fixed top-0 left-0 z-40 h-full w-[65px] flex flex-col items-center py-4 space-y-11 bg-white/[0.09] backdrop-blur-md">
      {/* Sidebar Icons */}
      <div className="group relative" onClick={handleShipTrackingClick}>
        <Waves className="h-8 w-8 text-gray-800 cursor-pointer hover:text-blue-400 mt-20" />
        <span className="absolute left-[85px] top-2 hidden group-hover:inline-block bg-gray-900 text-white px-2 py-1 rounded text-sm shadow">
          Ship Tracking
        </span>
      </div>
      <div className="group relative" onClick={handleReportClick}>
        <BarChart className="h-8 w-8 text-gray-800 cursor-pointer hover:text-blue-400" />
        <span className="absolute left-[85px] top-2 hidden group-hover:inline-block bg-gray-900 text-white px-2 py-1 rounded text-sm shadow">
          Report View
        </span>
      </div>
      <div className="group relative" onClick={handleLocationClick}>
        <MapPin className="h-8 w-8 text-gray-800 cursor-pointer hover:text-blue-400" />
        <span className="absolute left-[85px] top-2 hidden group-hover:inline-block bg-gray-900 text-white px-2 py-1 rounded text-sm shadow">
          Location
        </span>
      </div>
      <div className="group relative" onClick={handleLocationClick}>
        <Compass className="h-8 w-8 text-gray-800 cursor-pointer hover:text-blue-400" />
        <span className="absolute left-[85px] top-2 hidden group-hover:inline-block bg-gray-900 text-white px-2 py-1 rounded text-sm shadow">
          Location
        </span>
      </div>
      <div className="group relative" onClick={handleLocationClick}>
        <Ship className="h-8 w-8 text-gray-800 cursor-pointer hover:text-blue-400" />
        <span className="absolute left-[85px] top-2 hidden group-hover:inline-block bg-gray-900 text-white px-2 py-1 rounded text-sm shadow">
          Location
        </span>
      </div>
    </div>
  );
};

export default Sidebar;