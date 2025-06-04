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

---

**Built with ❤️ for the solar energy community** 