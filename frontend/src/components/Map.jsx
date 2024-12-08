import React, { useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { Icon } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useShipData } from '../hooks/useShipData';

// Function to generate a consistent unique color for each ship
const generateUniqueColor = (seed) => {
  // Use a simple hash function to generate a consistent color
  let hash = 0;
  for (let i = 0; i < seed.length; i++) {
    hash = ((hash << 5) - hash) + seed.charCodeAt(i);
    hash = hash & hash; // Convert to 32-bit integer
  }

  // Convert hash to a color
  const r = (hash & 0xFF0000) >> 16;
  const g = (hash & 0x00FF00) >> 8;
  const b = hash & 0x0000FF;

  // Ensure the color is not too dark or too light
  return `rgb(${Math.max(r, 50)}, ${Math.max(g, 50)}, ${Math.max(b, 50)})`;
};

const Map = ({ selectedShip, onShipSelect }) => {
  const { ships, connectionStatus } = useShipData();

  // Dark theme tile layer URL for OpenStreetMap
  const darkTileLayerUrl = 'https://tiles.stadiamaps.com/tiles/outdoors/{z}/{x}/{y}{r}.png';

  const createShipIcon = (ship) => {
    const isSelected = selectedShip?.id === ship.id;
    const size = isSelected ? 60 : 50;
    
    // Generate a unique color for each ship based on its ID
    const shipColor = generateUniqueColor(ship.id);
    
    // Create an SVG icon with the unique color
    const svgIcon = `
      <svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 24 24">
        <defs>
          <linearGradient id="shipGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:${shipColor};stop-opacity:0.8" />
            <stop offset="100%" style="stop-color:${shipColor};stop-opacity:1" />
          </linearGradient>
        </defs>
        <path 
          d="M5.75002 6.99992H1.32702C1.23202 6.99988 1.13899 6.97278 1.05883 6.92178C0.978666 6.87078 0.914694 6.798 0.874402 6.71196C0.83411 6.62592 0.819166 6.53019 0.831319 6.43596C0.843472 6.34173 0.882219 6.25292 0.943024 6.17992L5.94302 0.179917C5.99896 0.112789 6.07151 0.0614918 6.15345 0.0311379C6.23539 0.000783881 6.32385 -0.00756703 6.41002 0.00691732C6.51538 -0.00581753 6.62224 0.0039515 6.72354 0.0355788C6.82484 0.0672062 6.91828 0.119972 6.99767 0.190388C7.07707 0.260805 7.14062 0.347269 7.18412 0.444068C7.22762 0.540866 7.25008 0.645794 7.25002 0.751917L7.24902 8.99992H13.499C13.5799 8.99992 13.6595 9.01951 13.7311 9.05703C13.8027 9.09454 13.8641 9.14885 13.9101 9.21531C13.9561 9.28177 13.9853 9.35839 13.9953 9.43861C14.0052 9.51883 13.9955 9.60026 13.967 9.67592L12.954 12.3779C12.7754 12.8543 12.4556 13.2647 12.0375 13.5546C11.6194 13.8444 11.1228 13.9998 10.614 13.9999H3.38602C2.87728 13.9998 2.38068 13.8444 1.96256 13.5546C1.54444 13.2647 1.2247 12.8543 1.04602 12.3779L0.0310239 9.67592C0.0025417 9.60018 -0.0071343 9.51866 0.00282668 9.43836C0.0127877 9.35806 0.042088 9.28138 0.0882121 9.2149C0.134336 9.14842 0.195906 9.09412 0.267635 9.05668C0.339364 9.01923 0.419109 8.99976 0.500024 8.99992H5.75002V6.99992ZM9.38102 2.19592C9.31736 2.11334 9.22948 2.05272 9.12967 2.02256C9.02986 1.99239 8.92312 1.99418 8.82437 2.02769C8.72563 2.06119 8.63984 2.12472 8.57899 2.20939C8.51814 2.29407 8.48529 2.39565 8.48502 2.49992V6.49992C8.48502 6.63253 8.5377 6.7597 8.63147 6.85347C8.72524 6.94724 8.85242 6.99992 8.98502 6.99992H12.055C12.1482 6.99974 12.2395 6.97351 12.3186 6.9242C12.3977 6.87489 12.4614 6.80445 12.5026 6.72084C12.5438 6.63723 12.5608 6.54378 12.5517 6.45103C12.5425 6.35827 12.5077 6.26991 12.451 6.19592L9.38102 2.19592Z" 
          fill="url(#shipGradient)" 
          stroke="black"
          stroke-width="0.6"
        />
      </svg>
    `;

    // Convert SVG to data URL
    const svgDataUrl = `data:image/svg+xml;base64,${btoa(svgIcon)}`;

    return new Icon({
      iconUrl: svgDataUrl,
      iconSize: [size, size],
      iconAnchor: [size / 2, size / 2],
      popupAnchor: [0, -size/2]
    });
  };

  // Coordinates for the Gulf of Mexico
  const centerPosition = [25.7617, -80.1918];

  return (
    <div className="flex-1 relative h-full z-0 bg-gray-900">
      <ConnectionStatus status={connectionStatus} shipCount={ships.length} />
      
      <MapContainer
        center={centerPosition}
        zoom={6}
        className="h-full w-full"
        style={{ background: '#1f2937' }} // Dark background
      >
        <TileLayer
          url={darkTileLayerUrl}
          attribution='&copy; <a href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a>'
        />
        {ships.map((ship) => {
          if (!ship.position || !ship.position.lat || !ship.position.lng) return null;

          return (
            <Marker
              key={ship.id}
              position={[ship.position.lat, ship.position.lng]}
              icon={createShipIcon(ship)}
              rotationAngle={ship.course || 0}
              eventHandlers={{
                click: () => onShipSelect(ship),
              }}
            >
              <Popup 
                className="custom-popup"
                closeButton={true}
                closeOnClick={false}
                autoPan={true}
              >
                <ShipPopupContent ship={ship} />
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
};

const ConnectionStatus = ({ status, shipCount }) => (
  <div className="absolute top-4 right-4 z-[1000] bg-sky-800/80 backdrop-blur-sm text-white p-3 rounded-lg shadow-2xl">
    <div className={`flex items-center gap-2 ${
      status === 'connected' ? 'text-green-400' : 
      status === 'error' ? 'text-red-400' : 
      'text-yellow-400'
    }`}>
      <div className={`w-3 h-3 rounded-full animate-pulse ${
        status === 'connected' ? 'bg-green-400' : 
        status === 'error' ? 'bg-red-400' : 
        'bg-yellow-400'
      }`} />
      <span className="text-sm font-medium capitalize">{status}</span>
    </div>
    <div className="text-xs text-gray-300 mt-1">Ships: {shipCount}</div>
  </div>
);

const ShipPopupContent = ({ ship }) => {

  return (
    <div className=" text-white rounded-2xl flex flex-col">
      <div className="items-center mb-3">
        <div className="flex-grow flex items-center space-x-4">
          <h3 className="text-xl font-bold text-sky-500">{ship.vesselName}</h3>
        </div>
        <div className={`px-3 py-1 text-center rounded-full text-xs font-semibold uppercase mt-2 
          ${ship.status === 'Active' ? 'bg-green-500/20 text-green-400' : 
            ship.status === 'Idle' ? 'bg-yellow-500/20 text-yellow-400' : 
            'bg-red-500/20 text-red-400'}`}>
          {ship.status}
        </div>
      </div>

      <div className="gap-2 text-lg flex-grow">
        <div className="flex rounded-lg">
          <span className="block text-gray-700">Latitude: </span>
          <span className="font-medium text-sky-500">{ship.position.lat} °N</span>
        </div>
        <div className="flex rounded-lg">
          <span className="block text-gray-700">Longitude: </span>
          <span className="font-medium text-sky-500 truncate">{ship.position.lat} °N</span>
        </div>
        <div className="flex rounded-lg">
          <span className="block text-gray-700">Destination: </span>
          <span className="font-medium text-sky-500 truncate">{ship.destination} °N</span>
        </div>
      </div>

      <div className="mt-3 text-xs text-gray-500 text-center">
        Last Updated: {new Date(ship.lastUpdateTime).toLocaleString()}
      </div>
    </div>
  );
};

export default Map;

const globalStyles = `
  .leaflet-popup-content-wrapper {
    background: black !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
    border-radius: 1rem !important;
    border: 1px solid rgba(255,255,255,0.1);
    padding: 0 !important;
  }
  .leaflet-popup-content {
    margin: 0 !important;
  }
  .leaflet-popup-close-button {
    color: white !important;
    opacity: 0.7;
    top: 10px !important;
    right: 10px !important;
  }
`;