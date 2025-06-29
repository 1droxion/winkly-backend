const WebSocket = require("ws");

const PORT = process.env.PORT || 8080;
const wss = new WebSocket.Server({ port: PORT });

let clients = [];

wss.on("connection", (ws) => {
  console.log("✅ New user connected");

  clients.push(ws);

  ws.on("message", (msg) => {
    // Broadcast to all except sender
    clients.forEach((client) => {
      if (client !== ws && client.readyState === WebSocket.OPEN) {
        client.send(msg);
      }
    });
  });

  ws.on("close", () => {
    console.log("❌ User disconnected");
    clients = clients.filter((client) => client !== ws);
  });
});
