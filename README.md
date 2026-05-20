DDoS Botnet Lab 

Môi trường: 
Cài Docker Desktop
https://www.docker.com/products/docker-desktop/


Giới thiệu
Project mô phỏng cơ chế hoạt động cơ bản của một cuộc tấn công DDoS sử dụng Docker container.

Hệ thống gồm:
- C&C Server (Command & Control)
- Bot container
- Web Server mục tiêu

Các bot sẽ nhận lệnh từ C&C Server và gửi HTTP request đồng thời đến Web Server để mô phỏng HTTP Flood Attack 

Kiến trúc hệ thống:
C&C Server
     ↓
 Bot Containers
     ↓
 Target Web Server

 
Khời chạy:
Mở Docker Desktop
docker compose up
 
Mở C&C Console
```bash
docker exec -it cnc python cnc.py
>ATTACK 
>STOP
