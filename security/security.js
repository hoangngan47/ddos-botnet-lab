const os = require("os");

// ===== CONFIG =====
const MAX_CONN = 50;          // 🔥 giới hạn connection (cực quan trọng)
const GLOBAL_LIMIT = 80;      // request / giây
const CPU_THRESHOLD = 0.6;    // 60%

// ===== STATE =====
let globalCount = 0;
let currentConn = 0;

// reset mỗi giây (rất nhẹ)
setInterval(() => {
    globalCount = 0;
}, 1000);

// ===== CPU CHECK (nhẹ nhất có thể) =====
function isHighCPU() {
    const load = os.loadavg()[0];
    const cores = os.cpus().length;
    return (load / cores) > CPU_THRESHOLD;
}

// ===== REQUEST LEVEL (CHẶN SỚM) =====
function securityCheck(req, res) {

    // 🔥 1. GLOBAL LIMIT (ưu tiên cao nhất)
    globalCount++;
    if (globalCount > GLOBAL_LIMIT) {
        res.statusCode = 503;
        res.end();
        return false;
    }

    // 🔥 2. CPU PROTECTION
    if (isHighCPU()) {
        res.statusCode = 503;
        res.end();
        return false;
    }

    // 🔥 3. BOT FILTER SIÊU NHẸ
    const ua = req.headers["user-agent"];
    if (!ua || ua[0] === "p") {
        res.statusCode = 403;
        res.end();
        return false;
    }

    return true;
}

// ===== SOCKET LEVEL (GIẢM CPU MẠNH NHẤT) =====
function attachConnectionLimiter(server) {

    server.maxConnections = MAX_CONN;

    server.on("connection", (socket) => {
        currentConn++;

        // 🔥 QUÁ CONNECTION → KILL NGAY
        if (currentConn > MAX_CONN) {
            socket.destroy();
            return;
        }

        socket.on("close", () => {
            currentConn--;
        });
    });
}

module.exports = {
    securityCheck,
    attachConnectionLimiter
};