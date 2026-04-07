# DDoS Lab - Quick Start Script for Windows
# Run as: powershell -ExecutionPolicy Bypass -File lab.ps1

Write-Host "=================================="
Write-Host "DDoS Botnet Lab - Quick Start (Windows)" -ForegroundColor Cyan
Write-Host "=================================="
Write-Host ""

# Check for Docker
try {
    docker --version | Out-Null
} catch {
    Write-Host "ERROR: Docker is not installed." -ForegroundColor Red
    exit 1
}

# Check for Docker Compose
try {
    docker-compose --version | Out-Null
} catch {
    Write-Host "ERROR: Docker Compose is not installed." -ForegroundColor Red
    exit 1
}

Write-Host "✓ Docker and Docker Compose found" -ForegroundColor Green
Write-Host ""

while ($true) {
    Write-Host "Select an option:" -ForegroundColor Cyan
    Write-Host "1) Start the lab"
    Write-Host "2) Stop the lab"
    Write-Host "3) View server metrics"
    Write-Host "4) Connect to C&C console"
    Write-Host "5) View logs"
    Write-Host "6) Clean up (remove all containers)"
    Write-Host "7) Exit"
    Write-Host ""
    $choice = Read-Host "Enter your choice (1-7)"
    
    switch ($choice) {
        "1" {
            Write-Host "Starting DDoS Lab..." -ForegroundColor Cyan
            docker-compose up -d
            Start-Sleep -Seconds 3
            Write-Host ""
            Write-Host "✓ Lab started!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Services:"
            docker-compose ps
            Write-Host ""
            Write-Host "Next steps:"
            Write-Host "  1. Connect to C&C: docker exec -it cnc python cnc.py"
            Write-Host "  2. View metrics: curl http://localhost:3000/metrics"
            Write-Host "  3. View logs: docker logs -f server"
        }
        
        "2" {
            Write-Host "Stopping DDoS Lab..." -ForegroundColor Cyan
            docker-compose down
            Write-Host "✓ Lab stopped" -ForegroundColor Green
        }
        
        "3" {
            Write-Host "Fetching server metrics..." -ForegroundColor Cyan
            Write-Host ""
            curl.exe -s http://localhost:3000/metrics | ConvertFrom-Json | ConvertTo-Json
        }
        
        "4" {
            Write-Host "Connecting to C&C console..." -ForegroundColor Cyan
            Write-Host "Type 'HELP' for available commands"
            Write-Host ""
            docker exec -it cnc python cnc.py
        }
        
        "5" {
            Write-Host "Bot and Server Logs:" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "=== Bot 1 ===" -ForegroundColor Yellow
            docker logs bot_1 | Select-Object -Last 15
            Write-Host ""
            Write-Host "=== Bot 2 ===" -ForegroundColor Yellow
            docker logs bot_2 | Select-Object -Last 15
            Write-Host ""
            Write-Host "=== Bot 3 ===" -ForegroundColor Yellow
            docker logs bot_3 | Select-Object -Last 15
            Write-Host ""
            Write-Host "=== Server ===" -ForegroundColor Yellow
            docker logs server | Select-Object -Last 15
        }
        
        "6" {
            Write-Host "WARNING: This will remove all containers!" -ForegroundColor Yellow
            $confirm = Read-Host "Type 'yes' to confirm"
            if ($confirm -eq "yes") {
                docker-compose down -v
                Write-Host "✓ All cleaned up" -ForegroundColor Green
            } else {
                Write-Host "Cancelled"
            }
        }
        
        "7" {
            Write-Host "Goodbye!"
            exit 0
        }
        
        default {
            Write-Host "Invalid choice" -ForegroundColor Red
        }
    }
    
    Write-Host ""
    Read-Host "Press Enter to continue"
    Clear-Host
}
