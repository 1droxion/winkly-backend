const WebSocket = require("ws");

const PORT = process.env.PORT || 8080;
const wss = new WebSocket.Server({ port: PORT }, () =>
  console.log(`✅ WebSocket Server running on port ${PORT}`)
);

let clients = [];

wss.on("connection", (ws) => {
  clients.push(ws);
  console.log("🔌 Client connected. Total:", clients.length);

  ws.on("message", (message) => {
    clients.forEach((client) => {
      if (client !== ws && client.readyState === WebSocket.OPEN) {
        client.send(message.toString());
      }
    });
  });

  ws.on("close", () => {
    clients = clients.filter((client) => client !== ws);
    console.log("❌ Client disconnected. Remaining:", clients.length);
  });
});
