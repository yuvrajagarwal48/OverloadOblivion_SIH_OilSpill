import React, { useState } from 'react';
import { MapPin, Compass, ArrowUp, Target, Ship, FileText } from 'lucide-react';
import map2 from '../assets/map2.png';
import { Search, Anchor } from 'lucide-react';
import { Link } from 'react-router-dom';

const Header = () => {
    return (
      <header className="bg-sky-500 text-gray-800 p-4 pl-20 flex items-center justify-between font-poppins z-50">
      <div className="flex items-center space-x-4">
        <Anchor className="h-8 w-8 text-white" />
        <h1 className="text-xl font-bold text-white">Ship Sentinel</h1>
      </div>
      <div className="flex flex-grow max-w-md mx-4 text-lg gap-8">
        <Link to='/' className="text-white hover:text-sky-100 font-medium">Home</Link>
        <a href="#features" className="text-white hover:text-sky-100 font-medium">About Us</a>
            <a href="#features" className="text-white hover:text-sky-100 font-medium">Resources</a>
            <a href="#community" className="text-white hover:text-sky-100 font-medium">Contact Us</a>
      </div>
    </header>
  
    );
  };

// Sample PDF data
const samplePDFs = [
  {
    id: 1,
    name: "Titanic Voyage Report",
    mmsi: "123456789",
    position: { lat: "22.5726", lng: "88.3639" },
    speed: "15 knots",
    vesselName: "Titanic",
    destination: "New York",
    status: "In Transit",
    course: "90°",
    trueHeading: "North"
  },
  {
    id: 2,
    name: "Ocean Voyager Log",
    mmsi: "987654321",
    position: { lat: "25.7617", lng: "-80.1918" },
    speed: "12 knots",
    vesselName: "Ocean Explorer",
    destination: "Miami",
    status: "Docked",
    course: "0°",
    trueHeading: "South"
  },
  {
    id: 3,
    name: "Maritime Expedition Report",
    mmsi: "456789123",
    position: { lat: "40.7128", lng: "-74.0060" },
    speed: "18 knots",
    vesselName: "Maritime Pioneer",
    destination: "Boston",
    status: "Underway",
    course: "45°",
    trueHeading: "Northeast"
  }
];

const ShipInformationPage = () => {
  const [selectedPDF, setSelectedPDF] = useState(samplePDFs[0]);

  const downloadPDF = (data) => {
    const pdfContent = `
      Ship Information
      --------------------
      PDF Name: ${data.name}
      MMSI: ${data.mmsi}
      Position: Latitude ${data.position.lat}, Longitude ${data.position.lng}
      Speed: ${data.speed}
      Vessel Name: ${data.vesselName}
      Destination: ${data.destination}
      Status: ${data.status}
      Course: ${data.course}
      True Heading: ${data.trueHeading}
      Downloaded on: ${new Date().toLocaleString()}
    `;

    const blob = new Blob([pdfContent], { type: "application/pdf" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `${data.name.replace(/\s+/g, '_')}.pdf`;
    link.click();
  };

  return (
    <div>
        <Header />
    <div className="flex h-screen bg-sky-100 ml-16">

      {/* Center - Ship Details */}
      <div className="w-2/4 p-8 overflow-y-auto">
        <h1 className="text-3xl font-bold mb-6 text-sky-800">{selectedPDF.name}</h1>
        <div className="space-y-4">
          {[
            { icon: <Ship className="inline w-5 h-5 mr-2 text-sky-500" />, label: "ID (MMSI)", value: selectedPDF.mmsi },
            { icon: <MapPin className="inline w-5 h-5 mr-2 text-sky-500" />, label: "Position", value: `Lat ${selectedPDF.position.lat}, Lng ${selectedPDF.position.lng}` },
            { icon: <MapPin className="inline w-5 h-5 mr-2 text-sky-500" />, label: "Speed", value: selectedPDF.speed },
            { icon: <Ship className="inline w-5 h-5 mr-2 text-sky-500" />, label: "Vessel Name", value: selectedPDF.vesselName },
            { icon: <MapPin className="inline w-5 h-5 mr-2 text-sky-500" />, label: "Destination", value: selectedPDF.destination },
            { icon: <Target className="inline w-5 h-5 mr-2 text-sky-500" />, label: "Status", value: selectedPDF.status },
            { icon: <Compass className="inline w-5 h-5 mr-2 text-sky-500" />, label: "Course", value: selectedPDF.course },
            { icon: <ArrowUp className="inline w-5 h-5 mr-2 text-sky-500" />, label: "True Heading", value: selectedPDF.trueHeading }
          ].map((item, index) => (
            <div 
              key={index} 
              className="flex justify-between items-center p-4 bg-sky-50 rounded-lg hover:bg-sky-100 transition-colors"
            >
              <div className="flex items-center">
                {item.icon}
                <span className="font-semibold text-sky-800 text-md">{item.label}:</span>
              </div>
              <span className="text-gray-700 text-md">{item.value}</span>
            </div>
          ))}
        </div>
        
        <div className="mt-6">
          <button
            className="w-full bg-sky-500 text-white px-6 py-3 rounded-lg hover:bg-sky-600 transition-colors duration-300 shadow-md text-xl"
            onClick={() => downloadPDF(selectedPDF)}
          >
            Download PDF
          </button>
        </div>
      </div>

      {/* Right Side - Map */}
      <div className="w-1/2">
        <img
          src={map2}
          alt="Ship Visualization"
          className="w-full h-full object-cover"
        />
      </div>
    </div>
    </div>
  );
};

export default ShipInformationPage;