const http = require("http");
const fs = require("fs");

const { securityCheck, attachConnectionLimiter } = require("./security");


// Server metrics
const metrics = {
    totalRequests: 0,
    successfulRequests: 0,
    failedRequests: 0,
    startTime: Date.now()
};

// Rate limiting configuration
const RATE_LIMIT_ENABLED = process.env.RATE_LIMIT === 'true' || false;
const MAX_REQUESTS_PER_IP_PER_SEC = 100;
const clientRequestCounts = new Map();

// Reset client request counts every second
setInterval(() => {
    clientRequestCounts.clear();
}, 1000);

function isRateLimited(clientIP) {
    if (!RATE_LIMIT_ENABLED) return false;
    
    const count = clientRequestCounts.get(clientIP) || 0;
    
    if (count >= MAX_REQUESTS_PER_IP_PER_SEC) {
        return true;
    }
    
    clientRequestCounts.set(clientIP, count + 1);
    return false;
}

const server = http.createServer((req, res) => {
    if (!securityCheck(req, res)) {
        metrics.failedRequests++;
        return;
    }

    const clientIP = req.socket.remoteAddress || "unknown";
    
    // Handle metrics endpoint - NO counting, NO rate limiting
    if (req.url === "/metrics" && req.method === "GET") {
        const uptime = (Date.now() - metrics.startTime) / 1000;
        const rps = metrics.totalRequests / uptime;
        
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify({
            totalRequests: metrics.totalRequests,
            successfulRequests: metrics.successfulRequests,
            failedRequests: metrics.failedRequests,
            requests_per_second: rps.toFixed(2),
            uptime_seconds: uptime.toFixed(2)
        }, null, 2));
        return;
    }
    
    // Ignore favicon and other non-main requests
    if (req.url !== "/" && req.url !== "") {
        res.statusCode = 404;
        res.end("Not Found");
        return;
    }
    
    // Rate limiting check - ONLY for main "/" requests
    if (isRateLimited(clientIP)) {
        metrics.failedRequests++;
        res.statusCode = 429;
        res.end(JSON.stringify({
            error: "Too Many Requests",
            code: 429
        }));
        return;
    }
    
    // Count ONLY main "/" server requests (not /metrics, /favicon.ico, etc)
    metrics.totalRequests++;
    metrics.successfulRequests++;
    
    res.writeHead(200, { "Content-Type": "text/plain" });
    res.end("Hello from Docker server");
    
    // Log every 50th request
    if (metrics.totalRequests % 50 === 0) {
        const uptime = (Date.now() - metrics.startTime) / 1000;
        const rps = metrics.totalRequests / uptime;
        console.log(`[Server] Total: ${metrics.totalRequests} | RPS: ${rps.toFixed(2)} | Uptime: ${uptime.toFixed(1)}s`);
    }
});
attachConnectionLimiter(server);

server.listen(3000, () => {
    console.log("Server running at http://localhost:3000");
    console.log("View metrics at http://localhost:3000/metrics");
    console.log(`Rate limiting: ${RATE_LIMIT_ENABLED ? 'ENABLED' : 'DISABLED'}`);
    console.log("Waiting for requests...\n");
});
 