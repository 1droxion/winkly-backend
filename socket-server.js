// === socket-server.js ===
const WebSocket = require("ws");

const PORT = 8080;
const wss = new WebSocket.Server({ port: PORT });

let clients = [];

wss.on("connection", (ws) => {
  console.log("🔌 New client connected");

  ws.on("message", (data) => {
    const msg = JSON.parse(data);

    if (msg.type === "join") {
      ws.userInfo = { id: Date.now(), gender: msg.gender, country: msg.country };
      clients.push(ws);
      tryMatch(ws);
    }

    if (msg.type === "signal") {
      const target = clients.find(c => c.userInfo && c.userInfo.id === msg.target);
      if (target && target.readyState === WebSocket.OPEN) {
        target.send(JSON.stringify({ type: "signal", data: msg.data, from: ws.userInfo.id }));
      }
    }
  });

  ws.on("close", () => {
    clients = clients.filter(c => c !== ws);
    console.log("❌ Client disconnected");
  });
});

function tryMatch(ws) {
  const available = clients.find(c =>
    c !== ws &&
    !c.userInfo.partner &&
    c.userInfo.gender !== ws.userInfo.gender && // optional match logic
    c.userInfo.country === ws.userInfo.country // match by country
  );

  if (available) {
    // Link partners
    ws.userInfo.partner = available.userInfo.id;
    available.userInfo.partner = ws.userInfo.id;

    // Notify both users
    ws.send(JSON.stringify({ type: "matched", partnerId: available.userInfo.id }));
    available.send(JSON.stringify({ type: "matched", partnerId: ws.userInfo.id }));

    console.log(`✅ Matched ${ws.userInfo.id} ↔ ${available.userInfo.id}`);
  }
}

console.log(`🚀 WebSocket Signaling Server running on ws://localhost:${PORT}`);
