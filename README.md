# SunSpec Gateway

A production-grade, brand-agnostic gateway for communicating with SunSpec-compliant solar inverters. Built using the official pySunSpec2 library and designed to work seamlessly with inverters from major manufacturers including Sungrow, Fronius, SMA, Huawei, ABB, and others.

## Features

### 🔌 **Brand Agnostic**
- Works with any SunSpec-compliant inverter
- Automatic model discovery and adaptation
- Uses official SunSpec Alliance reference models

### 🌐 **Multiple Connection Types**
- **Modbus TCP**: Ethernet/WiFi connections
- **Modbus RTU**: Serial (RS-485) connections  
- Automatic connection management and retry logic

### 📊 **Real-time Data Collection**
- Configurable polling intervals
- Automatic background data collection
- Caching for improved performance
- Support for all standard SunSpec models

### 🔧 **Control Capabilities**
- Read inverter status and measurements
- Write control parameters (where supported)
- Comprehensive error handling

### 🚀 **Production Ready**
- RESTful API with FastAPI
- Comprehensive logging
- Graceful startup/shutdown
- Health monitoring endpoints
- Docker-ready configuration

### 📈 **Monitoring & Integration**
- JSON-based data exchange
- Easy integration with monitoring systems
- Real-time and cached data endpoints
- Detailed device information

## Supported Inverters

This gateway works with any SunSpec-compliant inverter, including but not limited to:

- **Sungrow**: SH series, SG series (your current setup!)
- **Fronius**: Primo, Symo, Eco series
- **SMA**: Sunny Boy, Sunny Tripower series
- **Huawei**: SUN2000 series
- **ABB**: PVS, TRIO, UNO series
- **Solaredge**: SE series (with SunSpec enabled)
- **And many others...**

## 🌟 Live Demo

**Experience the dashboard in action**: https://sunspec-gateway-2025.oa.r.appspot.com

This live instance connects to a real Sungrow inverter via direct network connection, demonstrating:
- ⚡ Real-time power generation data
- 📊 Live inverter measurements  
- 🔄 Automatic 10-second updates
- 📱 Mobile-responsive design

*Note: The live demo connects to a local gateway running on a private network. For your own deployment, follow the setup instructions below.*

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configure Your Inverter

Edit `config.yaml` to match your setup:

```yaml
# For TCP connection (most common)
inverter:
  connection_type: "tcp"
  tcp:
    host: "192.168.1.100"  # Your inverter's IP address
    port: 502
    slave_id: 1

# For serial/RTU connection
inverter:
  connection_type: "rtu"
  rtu:
    port: "COM1"  # Windows: COM1, Linux: /dev/ttyUSB0
    baudrate: 19200
    slave_id: 1
```

### 3. Run the Gateway

```bash
python main.py
```

The gateway will start on `http://localhost:8080` by default.

### 4. Test the Connection

```bash
# Check if gateway is running
curl http://localhost:8080/

# Connect to your inverter
curl -X POST http://localhost:8080/connect

# Get device information
curl http://localhost:8080/device/info

# Get live data
curl http://localhost:8080/data/live
```

## API Endpoints

### Device Management
- `GET /` - Gateway status and information
- `GET /health` - Health check
- `POST /connect` - Connect to inverter
- `POST /disconnect` - Disconnect from inverter
- `GET /device/info` - Get inverter information
- `GET /device/models` - List available SunSpec models

### Data Access
- `GET /data` - Get latest cached data
- `GET /data/live` - Get fresh data from inverter
- `GET /data/live?models=1,103` - Get specific models
- `GET /data/model/{model_id}` - Get data from specific model

### Control
- `POST /write` - Write value to inverter point
```json
{
  "model_id": 103,
  "point_name": "WMaxLimPct",
  "value": 80.0
}
```

### Polling Management
- `GET /polling/status` - Get polling status
- `POST /polling/start` - Start automatic polling
- `POST /polling/stop` - Stop automatic polling

## Configuration

### Complete Configuration Example

```yaml
# Gateway information
gateway:
  name: "SunSpec Gateway"
  version: "1.0.0"
  description: "Production-grade brand-agnostic SunSpec inverter gateway"

# Web server settings
server:
  host: "0.0.0.0"
  port: 8080
  log_level: "INFO"

# Inverter connection
inverter:
  connection_type: "tcp"  # or "rtu"
  
  tcp:
    host: "192.168.1.100"
    port: 502
    slave_id: 1
    timeout: 10
  
  rtu:
    port: "/dev/ttyUSB0"
    baudrate: 19200
    bytesize: 8
    parity: "N"
    stopbits: 1
    slave_id: 1
    timeout: 10

# Data collection settings
data_collection:
  poll_interval: 30  # seconds
  models_to_read:
    - 1    # Common model (device info)
    - 103  # Inverter (three phase)
    - 160  # Multiple MPPT Extension
    - 113  # Inverter (single phase)
  max_retries: 3
  retry_delay: 5

# Logging
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "gateway.log"
  max_file_size: "10MB"
  backup_count: 5
```

## SunSpec Models

Common SunSpec models you'll encounter:

| Model ID | Name | Description |
|----------|------|-------------|
| 1 | Common | Basic device information |
| 103 | Inverter (3-phase) | Three-phase inverter measurements |
| 113 | Inverter (1-phase) | Single-phase inverter measurements |
| 120 | Nameplate | Inverter nameplate ratings |
| 121 | Basic Settings | Basic configuration settings |
| 122 | Measurements | Extended measurements |
| 123 | Immediate Controls | Direct control points |
| 124 | Storage | Battery/storage information |
| 160 | Multiple MPPT | MPPT string information |

## Example Data Output

```json
{
  "data": {
    "model_1": {
      "model_id": 1,
      "model_name": "Common",
      "points": {
        "Mn": "Sungrow",
        "Md": "SH10RT",
        "Vr": "1.0.0",
        "SN": "B2133ABC123",
        "DA": 1
      },
      "timestamp": "2025-01-06T10:30:00"
    },
    "model_103": {
      "model_id": 103,
      "model_name": "Inverter",
      "points": {
        "A": 15.2,
        "PhVphA": 239.1,
        "PhVphB": 240.2,
        "PhVphC": 238.9,
        "W": 3250.0,
        "Hz": 50.0,
        "WH": 12450000
      },
      "timestamp": "2025-01-06T10:30:00"
    }
  },
  "last_read_time": "2025-01-06T10:30:00",
  "available_models": {
    "1": "Common",
    "103": "Inverter",
    "160": "Multiple MPPT Inverter Extension"
  }
}
```

## Integration Examples

### Python Integration
```python
import requests

# Get live data
response = requests.get('http://localhost:8080/data/live')
data = response.json()

# Extract power production
power = data['model_103']['points']['W']
print(f"Current power: {power} W")

# Control power limit (if supported)
requests.post('http://localhost:8080/write', json={
    'model_id': 123,
    'point_name': 'WMaxLimPct',
    'value': 80.0
})
```

### Home Assistant Integration
```yaml
# configuration.yaml
sensor:
  - platform: rest
    resource: http://localhost:8080/data
    name: "Inverter Power"
    value_template: "{{ value_json.data.model_103.points.W }}"
    unit_of_measurement: "W"
    scan_interval: 30
```

## Deployment

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8080

CMD ["python", "main.py"]
```

### ✅ Proven GCP App Engine Deployment

**Working Example**: The live demo above uses this exact setup!

```yaml
# app.yaml (proven configuration)
runtime: python39

handlers:
  - url: /
    static_files: web/index.html
    upload: web/index.html
  
  - url: /(.+)
    static_files: web/\1
    upload: web/.*

automatic_scaling:
  min_instances: 0
  max_instances: 1
```

**Deploy Commands (tested):**
```bash
# 1. Set up GCP project with billing
gcloud projects create your-solar-project
gcloud config set project your-solar-project

# 2. Enable required APIs
gcloud services enable cloudbuild.googleapis.com appengine.googleapis.com

# 3. Create App Engine app
gcloud app create --region=europe-west6

# 4. Deploy (takes 2-3 minutes)
gcloud app deploy app.yaml --quiet

# 5. Your dashboard is live!
gcloud app browse
```

### Systemd Service
```ini
# /etc/systemd/system/sunspec-gateway.service
[Unit]
Description=SunSpec Gateway
After=network.target

[Service]
Type=simple
User=sunspec
WorkingDirectory=/opt/sunspec-gateway
ExecStart=/opt/sunspec-gateway/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Troubleshooting

### Connection Issues
1. **Check network connectivity**: `ping <inverter_ip>`
2. **Verify Modbus is enabled** on your inverter
3. **Check firewall settings** (port 502 for TCP)
4. **Confirm slave ID** matches inverter configuration

### Common Error Messages
- `Device not connected`: Run `POST /connect` first
- `Model X not available`: Check which models your inverter supports
- `Timeout errors`: Increase timeout in configuration
- `Permission denied`: Check serial port permissions (RTU)

### Debug Mode
Set logging level to `DEBUG` in config.yaml for verbose output.

## Making the Gateway Accessible Online

The gateway runs locally by default (`localhost:8080`), but you can make it accessible from anywhere with several deployment options:

### 🚀 Successful GCP Deployment Example

**Live Instance**: https://sunspec-gateway-2025.oa.r.appspot.com

This project includes a **production deployment** on Google Cloud Platform that demonstrates the complete setup:

**Architecture:**
- **Web Dashboard**: Hosted on GCP App Engine (accessible globally)
- **Gateway Service**: Running locally on `192.168.1.7:8080`
- **Sungrow Inverter**: Connected via direct Ethernet cable to local computer
- **Data Flow**: Web Browser → GCP → Local Gateway → Inverter

**Key Benefits:**
- 🌍 **Global Access**: Dashboard accessible from anywhere
- 🔒 **Secure**: Local gateway remains on private network
- 📱 **Mobile Ready**: Responsive design works on all devices
- ⚡ **Real-time**: Live data with 10-second refresh
- 💰 **Cost Effective**: Static hosting is nearly free on GCP

**Setup Used:**
```bash
# 1. Modified web/dashboard.js to connect to local gateway
CONFIG.API_BASE_URL = 'http://192.168.1.7:8080'

# 2. Deployed to GCP App Engine
gcloud app deploy app.yaml --quiet

# 3. Local gateway runs with CORS enabled
python main.py  # On local computer
```

This proves the concept works perfectly for **production solar monitoring**!

### 1. Local Network Access

**Make it accessible to devices on your local network:**

Edit your `config.yaml`:
```yaml
server:
  host: "0.0.0.0"  # Listen on all interfaces instead of localhost
  port: 8080
```

Now devices on your network can access it at `http://YOUR_COMPUTER_IP:8080`

**Find your computer's IP address:**
```bash
# Windows
ipconfig

# Linux/Mac
ip addr show  # or ifconfig
```

### 2. Cloud Hosting (Recommended for Production)

#### Option A: DigitalOcean/Linode/AWS EC2

**Deploy to a VPS:**
```bash
# 1. Create a VPS instance (Ubuntu 22.04 recommended)
# 2. SSH into your server
ssh root@your-server-ip

# 3. Install dependencies
apt update && apt install python3 python3-pip git -y

# 4. Clone your project
git clone https://github.com/yourusername/inverter-logging.git
cd inverter-logging

# 5. Install Python requirements
pip3 install -r requirements.txt

# 6. Configure for production
cp config.yaml config_production.yaml
# Edit config_production.yaml with your inverter's IP

# 7. Run with systemd service (see systemd section above)
```

#### Option B: Docker Container Hosting

**Deploy with Docker on any cloud provider:**

```yaml
# docker-compose.yml
version: '3.8'
services:
  sunspec-gateway:
    build: .
    ports:
      - "80:8080"
    volumes:
      - ./config_production.yaml:/app/config.yaml
    restart: unless-stopped
    environment:
      - CONFIG_FILE=config.yaml
```

**Deploy to cloud:**
```bash
# Build and push to registry
docker build -t your-registry/sunspec-gateway .
docker push your-registry/sunspec-gateway

# Deploy on your cloud platform
docker-compose up -d
```

### 3. Home Network with Port Forwarding

**Access from anywhere via your home router:**

1. **Configure router port forwarding:**
   - Login to your router (usually `192.168.1.1`)
   - Find "Port Forwarding" or "NAT" settings
   - Forward external port `8080` to your computer's IP port `8080`

2. **Find your public IP:**
   ```bash
   curl https://ipinfo.io/ip
   ```

3. **Access from anywhere:**
   `http://YOUR_PUBLIC_IP:8080`

**⚠️ Security Warning**: This exposes your gateway to the internet. See security section below.

### 4. Secure Tunnel Services

#### Option A: Cloudflare Tunnel (Free)
```bash
# Install cloudflared
# Download from: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/

# Create tunnel
cloudflared tunnel create sunspec-gateway

# Configure tunnel
cat > config.yml << EOF
tunnel: your-tunnel-id
credentials-file: /path/to/your-tunnel-credentials.json
ingress:
  - hostname: sunspec.yourdomain.com
    service: http://localhost:8080
  - service: http_status:404
EOF

# Run tunnel
cloudflared tunnel run
```

#### Option B: ngrok (Quick Testing)
```bash
# Install ngrok from https://ngrok.com/
# Run your gateway first
python main.py

# In another terminal
ngrok http 8080
# Access via the provided ngrok URL
```

### 5. Production Deployment with Reverse Proxy

**Complete production setup with Nginx + SSL:**

```nginx
# /etc/nginx/sites-available/sunspec-gateway
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Add SSL with Let's Encrypt:**
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Your site will now be available at https://your-domain.com
```

### 6. Mobile App Access

**Access from mobile devices using any of the above methods:**

- **Local network**: `http://YOUR_COMPUTER_IP:8080`
- **Cloud hosting**: `https://your-domain.com`
- **Tunnel services**: Use the provided URLs

**Create mobile shortcuts:**
1. Open the gateway URL in your mobile browser
2. Add to home screen for app-like experience

### 7. API Integration from Remote Systems

**Access your gateway from other applications:**

```python
# From anywhere on the internet
import requests

# Use your deployed URL
GATEWAY_URL = "https://your-domain.com"  # or your chosen URL

# Get real-time data
response = requests.get(f"{GATEWAY_URL}/data/live")
inverter_data = response.json()

# Monitor power production
power = inverter_data['data']['model_103']['points']['W']
print(f"Solar power: {power}W")
```

### Security Considerations

**When making your gateway accessible online:**

1. **Authentication (Recommended):**
   ```python
   # Add to your FastAPI app
   from fastapi.security import HTTPBasic, HTTPBasicCredentials
   
   security = HTTPBasic()
   
   @app.middleware("http")
   async def basic_auth(request: Request, call_next):
       # Add authentication logic
   ```

2. **IP Whitelisting:**
   ```yaml
   # In config.yaml
   security:
     allowed_ips:
       - "192.168.1.0/24"  # Local network
       - "YOUR_OFFICE_IP"   # Your office
   ```

3. **SSL/HTTPS Only:**
   - Always use HTTPS in production
   - Use Let's Encrypt for free SSL certificates

4. **Firewall Configuration:**
   ```bash
   # Ubuntu UFW example
   sudo ufw allow ssh
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw --force enable
   ```

5. **Read-Only Access:**
   ```yaml
   # Disable write operations in production
   security:
     read_only: true
   ```

### Monitoring Your Online Gateway

**Set up monitoring for your deployed gateway:**

```python
# Simple uptime monitoring script
import requests
import time

def check_gateway():
    try:
        response = requests.get("https://your-domain.com/health", timeout=10)
        if response.status_code == 200:
            print("✅ Gateway is online")
        else:
            print(f"⚠️ Gateway returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Gateway is offline: {e}")

# Run every 5 minutes
while True:
    check_gateway()
    time.sleep(300)
```

**Use external monitoring services:**
- **UptimeRobot**: Free website monitoring
- **Pingdom**: Professional monitoring
- **StatusCake**: Free tier available

### Cost Estimates

**Monthly hosting costs (approximate):**

- **DigitalOcean Droplet**: $5-10/month
- **AWS EC2 t3.micro**: $8-12/month
- **Linode Nanode**: $5/month
- **Cloudflare Tunnel**: Free
- **ngrok**: Free (basic) / $8/month (pro)
- **Home hosting**: Just electricity + internet

**Recommended for beginners**: Start with Cloudflare Tunnel (free) or a $5 VPS.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   REST API      │    │  SunSpec Client │    │    Inverter     │
│   (FastAPI)     │◄──►│   (pySunSpec2)  │◄──►│   (Modbus)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   Config Mgmt   │    │   Data Cache    │
│   (YAML/Pydantic│    │   (In-Memory)   │
└─────────────────┘    └─────────────────┘
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- **Issues**: Report bugs and request features on GitHub
- **Documentation**: See inline code documentation
- **SunSpec Alliance**: https://sunspec.org for protocol specifications
- **Live Demo**: https://sunspec-gateway-2025.oa.r.appspot.com

---

**Built with ❤️ for the solar energy community**

*Successfully deployed and monitoring real Sungrow inverter data in production!* ⚡🌞 