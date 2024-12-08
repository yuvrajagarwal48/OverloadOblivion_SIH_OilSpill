import React from 'react';
import { Ship, Navigation, MapPin, Clock, Anchor, Flag, Box } from 'lucide-react';
import shipIm from '../assets/ship-img.png'

const StatusSection = ({ status }) => (
  <div className="bg-white/80 p-3 rounded-lg">
    <div className="flex justify-between items-center">
      <span className="font-semibold text-gray-800">Status</span>
      <span className={`px-2 py-1 rounded-full text-xs ${
        status === 'In Transit' 
          ? 'bg-green-900 text-green-400' 
          : 'bg-yellow-900 text-yellow-400'
      }`}>
        {status}
      </span>
    </div>
  </div>
);



const ShipDetail = ({ ship, onClose }) => {
  return (
    <div className="w-96 bg-sky-500 text-gray-700 overflow-y-auto">
      <div className="relative">
        {/* Ship Image Section */}
        <div className="relative h-48 overflow-hidden">
          <img 
            src={shipIm} 
            alt={ship.vesselName} 
            className="w-full h-full object-cover opacity-70"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-sky-500 to-transparent"></div>
          <h2 className="absolute bottom-4 left-4 text-xl font-bold text-white">
            {ship.vesselName}
          </h2>
          <button 
            className="absolute top-4 right-4 text-white hover:text-gray-300 text-2xl" 
            onClick={onClose}
          >
            ×
          </button>
        </div>

        {/* Details Sections */}
        <div className="p-6 space-y-6">
          <StatusSection status={ship.status} />
          
          <DetailSection 
            icon={<MapPin className="text-blue-400" />} 
            title="Position"
          >
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>Latitude: {ship.position.lat}°N</div>
              <div>Speed: {ship.speed} knots</div>
              <div>Longitude: {ship.position.lng}°W</div>
              <div>Course: {ship.course}°</div>
            </div>
          </DetailSection>

          <DetailSection 
            icon={<Ship className="text-green-400" />} 
            title="Vessel Details"
          >
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="flex items-center gap-2">
                <Anchor className="w-4 h-4 text-gray-400" />
                <span>{ship.type}</span>
              </div>
              <div className="flex items-center gap-2">
                <Flag className="w-4 h-4 text-gray-400" />
                <span>{ship.flag}</span>
              </div>
              <div>Length: {ship.length} m</div>
              <div>Draft: {ship.draft} m</div>
              <div>Status: {ship.status}</div>
              <div>Communication State: {ship.communicationState}</div>
            </div>
          </DetailSection>

          <DetailSection 
            icon={<Navigation className="text-purple-400" />} 
            title="Journey"
          >
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2">
                <MapPin className="w-4 h-4 text-gray-400" />
                <span>Last Update: {ship.lastUpdate}</span>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-gray-400" />
                <span>True Heading: {ship.trueHeading}</span>
              </div>
              <div className="flex items-center gap-2">
                <Box className="w-4 h-4 text-gray-400" />
                <span>Time Stamp: {ship.timestamp}</span>
              </div>
            </div>
          </DetailSection>
        </div>
      </div>
    </div>
  );
};

const DetailSection = ({ icon, title, children }) => (
  <div className="bg-white/80 rounded-lg p-4 space-y-3">
    <div className="flex items-center gap-3 mb-2">
      {icon}
      <h3 className="font-semibold text-gray-800">{title}</h3>
    </div>
    {children}
  </div>
);

export default ShipDetail;