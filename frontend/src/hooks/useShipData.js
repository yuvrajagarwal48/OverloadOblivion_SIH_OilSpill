import { useState, useEffect, useCallback, useRef } from 'react';

export const useShipData = () => {
  const [ships, setShips] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const shipCache = useRef(new Map());
  const wsRef = useRef(null);

  const transformShipData = useCallback((mmsi, data, type) => {
    const existingShip = shipCache.current.get(mmsi) || {};

    try {
      if (type === 'PositionReport') {
        return {
          id: mmsi,
          position: {
            lat: data.Latitude,
            lng: data.Longitude
          },
          speed: data.SOG,
          vesselName: data.ShipName || `Unknown Vessel (${mmsi})`,
          destination: data.Destination || 'Unknown',
          status: data.NavigationalStatus === 1 ? 'Anchored' : 'In Transit',
          course: data.COG,
          communicationState: data.CommunicationState,
          positionAccuracy: data.PositionAccuracy,
          raim: data.Raim,
          rateOfTurn: data.RateOfTurn,
          repeatIndicator: data.RepeatIndicator,
          sog: data.SOG,
          spare: data.Spare,
          specialManoeuvreIndicator: data.SpecialManoeuvreIndicator,
          timestamp: data.Timestamp,
          trueHeading: data.TrueHeading,
          valid: data.Valid,
          lastUpdate: Date.now()
        };
      } else if (type === 'StaticData') {
        return {
          id: mmsi,
          vesselName: data.ShipName || `Unknown Vessel (${mmsi})`,
          destination: data.Destination || 'Unknown',
          eta: data.ETA || 'N/A',
          type: data.ShipType || 'Unknown',
          length: data.Length ? `${data.Length}m` : 'N/A',
          flag: data.Flag || 'Unknown',
          draft: data.Draught ? `${data.Draught}m` : 'N/A',
          cargo: data.Cargo || 'Unknown',
          lastStaticUpdate: Date.now()
        };
      }
    } catch (error) {
      console.error(`Error transforming ${type} data for MMSI ${mmsi}:`, error);
      return null;
    }
  }, []);

  const updateShipData = useCallback((newShipData) => {
    if (!newShipData || !newShipData.id) return;

    shipCache.current.set(newShipData.id, {
      ...shipCache.current.get(newShipData.id),
      ...newShipData
    });

    const thirtyMinutesAgo = Date.now() - 30 * 60 * 1000;
    const activeShips = Array.from(shipCache.current.values())
      .filter(ship => 
        ship.lastUpdate > thirtyMinutesAgo && 
        ship.position && 
        ship.position.lat && 
        ship.position.lng
      );

    setShips(activeShips);
  }, []);

  useEffect(() => {
    const connectWebSocket = () => {
      wsRef.current = new WebSocket('ws://localhost:3001');

      wsRef.current.onopen = () => {
        console.log('WebSocket Connected');
        setConnectionStatus('connected');
      };

      wsRef.current.onmessage = async (event) => {
        try {
          const jsonData = JSON.parse(event.data instanceof Blob ? await event.data.text() : event.data);
          
          const mmsi = jsonData.Message?.PositionReport?.UserID?.toString() || 
                       jsonData.Message?.ShipStatic?.UserID?.toString();

          if (!mmsi) {
            console.warn('No MMSI found:', jsonData);
            return;
          }

          console.log('Received Message:', jsonData); // Log entire message
          console.log('Message Type:', jsonData.MessageType); // Log message type

          const shipData = transformShipData(
            mmsi, 
            jsonData.MessageType === 'PositionReport' 
              ? jsonData.Message.PositionReport 
              : jsonData.Message.ShipStatic,
            jsonData.MessageType
          );

          if (shipData) {
            updateShipData(shipData);
          }
          
        } catch (error) {
          console.error('WebSocket message processing error:', error);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket Error:', error);
        setConnectionStatus('error');
      };

      wsRef.current.onclose = () => {
        setConnectionStatus('disconnected');
        setTimeout(connectWebSocket, 5000);
      };
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, [transformShipData, updateShipData]);

  return { ships, connectionStatus };
};