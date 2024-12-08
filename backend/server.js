const express = require('express');
const WebSocket = require('ws');
const http = require('http');
require('dotenv').config();

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

const connectToAISStream = (clientWs) => {
  const aisWs = new WebSocket('wss://stream.aisstream.io/v0/stream');

  aisWs.on('open', () => {
    console.log('AIS Stream Connected Successfully');
    
    const subscriptionMessage = {
      APIKey: process.env.AIS_STREAM_API_KEY,
      BoundingBoxes: [
        [[18, -98], [31, -81]]
      ],
      FilterMessageTypes: ["PositionReport"] // Remove StaticData
    };

    aisWs.send(JSON.stringify(subscriptionMessage));
  });

  aisWs.on('message', (data) => {
    try {
      const messageStr = data instanceof Buffer ? data.toString() : data;
      console.log('Raw Received Message:', messageStr);

      // Handle error messages or parse JSON
      const message = JSON.parse(messageStr);
      
      // Log full message details for debugging
      console.log('Parsed Message:', JSON.stringify(message, null, 2));

      // Forward only valid Position Reports
      if (message.MessageType === 'PositionReport' && 
          message.Message && 
          message.Message.PositionReport) {
        if (clientWs.readyState === WebSocket.OPEN) {
          clientWs.send(JSON.stringify(message));
        }
      }
    } catch (error) {
      console.error('Message processing error:', error);
      console.error('Raw message:', messageStr);
    }
  });

  aisWs.on('error', (error) => {
    console.error('AIS Stream Connection Error:', error);
  });

  aisWs.on('close', (code, reason) => {
    console.log(`AIS Stream Disconnected. Code: ${code}, Reason: ${reason}`);
  });

  return aisWs;
};

wss.on('connection', (ws) => {
  console.log('Client WebSocket Connected');
  const aisWs = connectToAISStream(ws);

  ws.on('close', () => {
    console.log('Client Disconnected');
    if (aisWs) aisWs.close();
  });
});

const PORT = process.env.PORT || 3001;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});