import React, { useRef, useEffect, useState } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Sky, useGLTF, Environment } from "@react-three/drei";
import * as THREE from "three";
import { Water } from "three/examples/jsm/objects/Water";
import { Search, Anchor, Globe, BarChart, Shield, FileText, Mail, AlertTriangle, Waves, Leaf, EarthLock, Network } from 'lucide-react';

// Feature images (you'll need to import these)
import trackingImage from "../assets/map.png";
import analyticsImage from "../assets/map2.png";
import coverageImage from "../assets/marine.jpg";
import dashboardImage from "../assets/new.jpg";
import newImage from "../assets/ship-img.png";

function Ocean() {
  const waterRef = useRef();
  const waterGeometry = new THREE.PlaneGeometry(1000, 1000);

  useEffect(() => {
    if (waterRef.current) {
      const water = new Water(waterGeometry, {
        textureWidth: 512,
        textureHeight: 512,
        waterNormals: new THREE.TextureLoader().load(
          "https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/textures/waternormals.jpg",
          (texture) => {
            texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
          }
        ),
        sunDirection: new THREE.Vector3(1, 1, 0),
        sunColor: 0xffffff,
        waterColor: 0x1e90ff,
        distortionScale: 3.7,
        fog: true,
      });

      water.rotation.x = -Math.PI / 2;
      waterRef.current.add(water);
    }
  }, [waterGeometry]);

  return <group ref={waterRef} />;
}

function Ship() {
  const shipRef = useRef();
  const { scene } = useGLTF("/cargo_ship_02.glb");

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    if (shipRef.current) {
      shipRef.current.rotation.z = Math.sin(t) * 0.03;
      shipRef.current.position.y = Math.sin(t * 2) * 0.1 + 1.5;
    }
  });

  return <primitive ref={shipRef} object={scene} scale={[1.5, 1.5, 1.5]} position={[4, 0.8, 7]}/>;
}


function Navbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-20 text-white p-4 bg-sky-500 backdrop-blur-md border-b border-white/[0.08]">
      <div className="container mx-auto flex justify-between items-center">
        <div className="flex items-center space-x-3">
          <Anchor className="h-8 w-8 text-white" />
          <span className="text-2xl font-bold tracking-wide text-white">Ship Sentinel</span>
        </div>
        <div className="space-x-8 text-xl">
          <a href="#home" className="text-white hover:text-sky-300 font-medium">Home</a>
          <a href="#features" className="text-white hover:text-sky-300 font-medium">About Us</a>
          <a href="#features" className="text-white hover:text-sky-300 font-medium">Resources</a>
          <a href="#community" className="text-white hover:text-sky-300 font-medium">Contact Us</a>
          <a href="#contact" className="text-gray-800 rounded-full bg-white px-6 py-2 hover:bg-sky-600 transition-colors font-medium">Log In</a>
        </div>
      </div>
    </nav>
  );
}

function FeatureSection() {
  const features = [
    {
      number: '01',
      title: 'Real-Time Vessel Tracking',
      description: 'Comprehensive monitoring of maritime vessels with precise geolocation.',
      image: trackingImage
    },
    {
      number: '02',
      title: 'Oil Spill Detection',
      description: 'Advanced detection of oil spills and maritime ecological threats.',
      image: analyticsImage
    },
    {
      number: '03',
      title: 'Ecological Impact Assessment',
      description: 'Detailed environmental impact reports and carbon footprint analysis.',
      image: coverageImage
    },
    {
      number: '04',
      title: 'Interactive Environmental Report',
      description: 'Comprehensive marine ecosystem health, vessel emissions, and conservation metrics.',
      image: dashboardImage
    }
  ];

  const [activeFeature, setActiveFeature] = useState(0);

  return (
    <div className="bg-sky-500 text-white">
      <div className="container mx-auto px-4 py-16 lg:py-24">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Feature List */}
          <div className="space-y-6">
            {features.map((feature, index) => (
              <div 
                key={index}
                onClick={() => setActiveFeature(index)}
                className={`
                  cursor-pointer p-6 rounded-xl transition-all duration-300 ease-in-out
                  ${activeFeature === index 
                    ? 'bg-white bg-opacity-20 shadow-lg' 
                    : 'hover:bg-white hover:bg-opacity-10'}
                `}
              >
                <div className="flex items-center space-x-4">
                  {/* Numbered Badge */}
                  <div className={`
                    w-12 h-12 flex items-center justify-center 
                    rounded-full font-bold text-xl
                    transition-colors
                    ${activeFeature === index 
                      ? 'bg-white text-sky-600' 
                      : 'bg-white bg-opacity-20 text-white'}
                  `}>
                    {feature.number}
                  </div>
                  
                  {/* Text Content */}
                  <div>
                    <h3 className="text-xl font-semibold mb-2">
                      {feature.title}
                    </h3>
                    <p className="text-white text-opacity-80 text-md">
                      {feature.description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Active Feature Image */}
          <div className="hidden lg:block">
            <div className="relative overflow-hidden rounded-xl shadow-2xl">
              <img 
                src={features[activeFeature].image} 
                alt={features[activeFeature].title}
                className="w-full h-96 object-cover transition-transform duration-500 hover:scale-105"
              />
              <div className="absolute inset-0 bg-white bg-opacity-10 hover:bg-opacity-5 transition-all duration-300"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}


function Footer() {
  return (
    <footer className="bg-sky-700 text-white py-16 px-8">
      <div className="container mx-auto grid md:grid-cols-4 gap-8">
        <div>
          <div className="flex items-center space-x-3 mb-6">
            <Anchor className="h-8 w-8 text-white" />
            <span className="text-2xl font-bold">Ship Sentinel</span>
          </div>
          <p className="text-sky-200">Global maritime intelligence platform transforming shipping insights.</p>
        </div>
        <div>
          <h4 className="text-xl font-semibold mb-4">Quick Links</h4>
          <ul className="space-y-2">
            <li><a href="#home" className="hover:text-sky-300">Home</a></li>
            <li><a href="#features" className="hover:text-sky-300">Features</a></li>
            <li><a href="#about" className="hover:text-sky-300">About</a></li>
            <li><a href="#contact" className="hover:text-sky-300">Contact</a></li>
          </ul>
        </div>
        <div>
          <h4 className="text-xl font-semibold mb-4">Resources</h4>
          <ul className="space-y-2">
            <li><a href="#" className="hover:text-sky-300">Maritime Reports</a></li>
            <li><a href="#" className="hover:text-sky-300">Industry Insights</a></li>
            <li><a href="#" className="hover:text-sky-300">Case Studies</a></li>
            <li><a href="#" className="hover:text-sky-300">API Documentation</a></li>
          </ul>
        </div>
        <div>
          <h4 className="text-xl font-semibold mb-4">Contact Us</h4>
          <div className="space-y-2">
            <p><Mail className="inline mr-2 w-5 h-5 text-sky-500" />info@shipsentinel.com</p>
            <div className="flex space-x-4 mt-4">
              <a href="#" className="text-sky-300 hover:text-white"><Globe className="w-6 h-6" /></a>
              <a href="#" className="text-sky-300 hover:text-white"><Anchor className="w-6 h-6" /></a>
            </div>
          </div>
        </div>
      </div>
      {/* <div className="border-t border-sky-700 mt-8 pt-6 text-center">
        <p className="text-sky-300">© 2024 Ship Sentinel. All Rights Reserved.</p>
      </div> */}
    </footer>
  );
}

export default function Homepage() {
  return (
    <div className="font-montserrat">
      <Navbar />
      <div className="relative w-screen overflow-hidden h-[100vh]">
        <div className="absolute top-[50vh] left-[32vw] transform -translate-x-1/2 -translate-y-1/2 z-10 text-left">
          <h1 className="text-7xl font-bold mb-6 text-gray-900 drop-shadow-lg">
          Safeguarding Oceans
          </h1>
          <h2 className="text-2xl mb-5 text-gray-900 p-3 w-[30vw] font-medium">
          Real-Time Vessel and Oil Spill Detection
          </h2>
          <p className="text-lg text-gray-700 max-w-2xl mb-10 leading-relaxed">
          Our solution uses real-time satellite data and anomaly detection to identify oil spills and vessel threats, enabling quick responses and enhancing marine safety. By combining AIS data with satellite imagery, we help protect oceans and shipping routes from environmental risks.
          </p>
          <div className="space-x-4 text-lg">
            <button className="bg-sky-500 text-white px-8 py-3 rounded-full hover:bg-sky-600 transition-colors">
              Get Started
            </button>
          </div>
        </div>
        
        <Canvas 
          className="absolute inset-0 "
          camera={{ position: [-9, 3, 12], fov: 45 }}
          gl={{ preserveDrawingBuffer: true }}
          onClick={(e) => e.preventDefault()}
          onWheel={(e) => e.preventDefault()}
        >
            <Environment preset="sunset" />
            {/* <MarineSparkles /> */}
          {/* Lighting */}
          <ambientLight intensity={0.5} />
          <directionalLight position={[10, 10, 10]} intensity={1.5} castShadow />

          {/* Sky */}
          <Sky
            sunPosition={[100, 20, 100]}
            turbidity={10}
            rayleigh={2}
            mieCoefficient={0.005}
            mieDirectionalG={0.8}
            color="#87CEEB" 
          />

          {/* Ocean */}
          <Ocean />

          {/* Ship */}
          <Ship />

          {/* Controls - limited to mouse drag only */}
          <OrbitControls 
            enableZoom={false} 
            enablePan={false}
            enableRotate={true}
            autoRotate autoRotateSpeed={0.2}
          />
        </Canvas>
      </div>
      <FeatureSection/>
      <Footer/>
    </div>
  );
}