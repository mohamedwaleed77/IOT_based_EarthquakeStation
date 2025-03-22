import express from 'express';
import cors from 'cors';
import { WebSocketServer } from 'ws'; // Missing WebSocket import
import { addEvent } from './stationsModule/controller.js';
import stationRouter from './stationsModule/routes.js';
 

const app = express();
const port = 3001;

app.use(cors());
app.use(express.json());
app.use(stationRouter);

// Start HTTP Server
const server = app.listen(port, () => console.log(`Server running on port ${port}`));
 
// Create WebSocket Server
const wss = new WebSocketServer({ server });

wss.on("connection", (ws) => {
    ws.on("message", (message) => {
        try {
            addEvent(ws,wss, message); // Directly call addEvent on message receive
        } catch (error) {
            console.error("Error processing WebSocket message:", error);
            ws.send(JSON.stringify({ error: "Invalid WebSocket message format" }));
        }
    });
});
