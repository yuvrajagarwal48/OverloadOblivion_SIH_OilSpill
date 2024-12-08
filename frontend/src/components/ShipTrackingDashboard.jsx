import React, { useState } from 'react';
import { Search, Ship, Anchor } from 'lucide-react';
import Map from './Map';
import ShipDetail from './ShipDetail';
import { useShipData } from '../hooks/useShipData';
import { Link } from 'react-router-dom';

const Header = ({ searchTerm, setSearchTerm }) => (
  <header className="bg-sky-500 text-gray-800 p-4 pl-20 flex items-center justify-between font-poppins z-50">
    <div className="flex items-center space-x-4">
      <Anchor className="h-8 w-8 text-white" />
      <h1 className="text-xl font-bold text-white">Ship Sentinel</h1>
    </div>
    <div className="relative flex-grow max-w-md mx-4">
      <input
        type="text"
        placeholder="Search ships..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="w-full pl-10 pr-4 py-2 rounded-full bg-gray-100 text-gray-800 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <Link to="/" className="absolute top-1/4 -left-20 hover:text-blue-300 transition-colors text-lg text-white">Home</Link>
      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-800" />
    </div>
  </header>
);

const ShipTrackingDashboard = () => {
  const { ships = [] } = useShipData(); // Provide a default empty array
  const [selectedShip, setSelectedShip] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Filter ships with additional null/undefined checks
  const filteredShips = ships.filter(ship => 
    ship && 
    ship.vesselName && 
    typeof ship.vesselName === 'string' &&
    ship.vesselName.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="h-screen flex flex-col font-poppins">
      <Header searchTerm={searchTerm} setSearchTerm={setSearchTerm} />
      <div className="flex-1 flex">
        <Map 
          ships={filteredShips} 
          selectedShip={selectedShip}
          onShipSelect={setSelectedShip}
        />
        {selectedShip && (
          <ShipDetail 
            ship={selectedShip} 
            onClose={() => setSelectedShip(null)} 
          />
        )}
      </div>
    </div>
  );
};

export default ShipTrackingDashboard;