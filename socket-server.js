// socket-server.js
const WebSocket = require("ws");

const PORT = process.env.PORT || 8080;
const wss = new WebSocket.Server({ port: PORT }, () =>
  console.log(`✅ WebSocket Server running on port ${PORT}`)
);

let clients = [];

wss.on("connection", (ws) => {
  clients.push(ws);
  console.log("🔌 New client connected. Total:", clients.length);

  ws.on("message", (message) => {
    console.log("💬 Received:", message.toString());
    for (let client of clients) {
      if (client !== ws && client.readyState === WebSocket.OPEN) {
        client.send(message.toString());
      }
    }
  });

  ws.on("close", () => {
    clients = clients.filter((client) => client !== ws);
    console.log("❌ Client disconnected. Remaining:", clients.length);
  });
});
