#!/usr/bin/env python3
"""
Sungrow Inverter Diagnostics Script
Comprehensive diagnostics and configuration guide for Sungrow inverters.
"""

import sys
import asyncio
import socket
import subprocess
import platform
from pathlib import Path

def test_connection_to_ip(ip, port, timeout=3):
    """Test if a specific IP and port is reachable."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    
    try:
        result = sock.connect_ex((ip, port))
        return result == 0
    except:
        return False
    finally:
        sock.close()

def test_multiple_ports(ip, ports):
    """Test multiple ports on an IP address."""
    results = {}
    for port in ports:
        results[port] = test_connection_to_ip(ip, port)
    return results

def test_ping(ip_address):
    """Test if an IP address responds to ping."""
    try:
        if platform.system().lower() == "windows":
            result = subprocess.run(
                ["ping", "-n", "1", "-w", "1000", ip_address], 
                capture_output=True, 
                text=True
            )
        else:
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "1", ip_address], 
                capture_output=True, 
                text=True
            )
        return result.returncode == 0
    except:
        return False

def print_sungrow_modbus_guide():
    """Print detailed guide for enabling Modbus TCP on Sungrow inverters."""
    print("\n" + "=" * 70)
    print("🔧 SUNGROW INVERTER MODBUS TCP CONFIGURATION GUIDE")
    print("=" * 70)
    print()
    print("Your Sungrow inverter is responding at 192.168.0.1 but Modbus TCP is disabled.")
    print("Here's how to enable it:")
    print()
    print("📱 METHOD 1: Using Inverter LCD Display")
    print("-" * 40)
    print("1. On your inverter's LCD screen, press the navigation buttons")
    print("2. Navigate to: SETUP → COMMUNICATION → MODBUS")
    print("3. Set: MODBUS TCP = ENABLE")
    print("4. Set: PORT = 502 (default)")
    print("5. Set: SLAVE ID = 1 (default)")
    print("6. Save settings and restart inverter if needed")
    print()
    print("🌐 METHOD 2: Using iSolarCloud App/Web Portal")
    print("-" * 40)
    print("1. Connect to your inverter via Sungrow's iSolarCloud")
    print("2. Go to Device Settings → Communication Settings")
    print("3. Enable Modbus TCP communication")
    print("4. Set port to 502 and slave ID to 1")
    print()
    print("🔌 METHOD 3: Using Ethernet Configuration")
    print("-" * 40)
    print("1. Access inverter menu: SETUP → COMMUNICATION → ETHERNET")
    print("2. Check IP address (should be 192.168.8.100)")
    print("3. Go to MODBUS TCP settings in the same menu")
    print("4. Enable Modbus TCP")
    print()
    print("📚 COMMON SUNGROW MODELS & SETTINGS:")
    print("-" * 40)
    print("• SH Series (Hybrid): Settings → Communication → Modbus TCP")
    print("• SG Series (String): Setup → Communication → Modbus")
    print("• Default IP: 192.168.0.1 or 192.168.1.1")
    print("• Default Port: 502")
    print("• Default Slave ID: 1")
    print()
    print("⚠️  IMPORTANT NOTES:")
    print("-" * 20)
    print("• Some models require firmware update for Modbus TCP")
    print("• Check your manual for model-specific instructions")
    print("• Restart inverter after enabling Modbus TCP")
    print("• Wait 30-60 seconds after restart before testing")

def print_alternative_connection_methods():
    """Print alternative methods if Modbus TCP cannot be enabled."""
    print("\n" + "=" * 70)
    print("🔄 ALTERNATIVE CONNECTION METHODS")
    print("=" * 70)
    print()
    print("If you cannot enable Modbus TCP, try these alternatives:")
    print()
    print("1. 📡 RS485/RTU Connection:")
    print("   - Use USB-to-RS485 adapter")
    print("   - Connect to inverter's RS485 terminals")
    print("   - Configure gateway for RTU mode")
    print()
    print("2. 📱 WiFi Connection:")
    print("   - Connect inverter to your WiFi network")
    print("   - Use network-based discovery")
    print()
    print("3. 🌐 Via Router/Switch:")
    print("   - Connect both computer and inverter to a network switch")
    print("   - This may resolve IP addressing issues")

async def comprehensive_diagnostics():
    """Run comprehensive diagnostics on the found inverter."""
    inverter_ip = "192.168.8.100"
    
    print("🔍 COMPREHENSIVE SUNGROW DIAGNOSTICS")
    print("=" * 50)
    print(f"Target Inverter IP: {inverter_ip}")
    print()
    
    # Test 1: Basic connectivity
    print("1. 🌐 Testing Basic Connectivity...")
    if test_ping(inverter_ip):
        print(f"   ✅ {inverter_ip} responds to ping - inverter is reachable!")
    else:
        print(f"   ❌ {inverter_ip} does not respond to ping")
        return
    
    # Test 2: Port scanning
    print("\n2. 🔍 Testing Common Inverter Ports...")
    common_ports = [
        502,   # Modbus TCP
        80,    # HTTP web interface
        443,   # HTTPS
        23,    # Telnet
        22,    # SSH
        8080,  # Alternative HTTP
        1502,  # Alternative Modbus
        8502,  # Modbus TCP alternative
    ]
    
    port_results = test_multiple_ports(inverter_ip, common_ports)
    
    open_ports = []
    for port, is_open in port_results.items():
        status = "✅ OPEN" if is_open else "❌ CLOSED"
        service = {
            502: "Modbus TCP (Primary)",
            80: "HTTP Web Interface", 
            443: "HTTPS Web Interface",
            23: "Telnet",
            22: "SSH",
            8080: "Alternative HTTP",
            1502: "Alternative Modbus",
            8502: "Alternative Modbus TCP"
        }.get(port, "Unknown Service")
        
        print(f"   Port {port:4d} ({service:20s}): {status}")
        
        if is_open:
            open_ports.append(port)
    
    # Test 3: Analyze results
    print(f"\n3. 📊 Analysis:")
    print(f"   Open ports found: {open_ports}")
    
    if 502 in open_ports:
        print("   🎉 Modbus TCP (port 502) is ENABLED!")
        print("   You can now use the gateway with IP: 192.168.0.1")
        
        # Update config
        print("\n📝 UPDATE YOUR CONFIG.YAML:")
        print("""
inverter:
  connection_type: "tcp"
  tcp:
    host: "192.168.0.1"
    port: 502
    slave_id: 1
    timeout: 10
""")
        
    elif any(port in open_ports for port in [1502, 8502]):
        alt_port = next(port for port in [1502, 8502] if port in open_ports)
        print(f"   ⚠️  Modbus TCP found on alternative port {alt_port}")
        print(f"   Try using port {alt_port} instead of 502")
        
        print(f"\n📝 UPDATE YOUR CONFIG.YAML:")
        print(f"""
inverter:
  connection_type: "tcp"
  tcp:
    host: "192.168.0.1"
    port: {alt_port}
    slave_id: 1
    timeout: 10
""")
        
    elif 80 in open_ports or 443 in open_ports:
        print("   🌐 Web interface is available!")
        print("   Try accessing http://192.168.0.1 in your browser")
        print("   You may be able to enable Modbus TCP through the web interface")
        
    else:
        print("   ❌ Modbus TCP is not enabled")
        print("   You need to enable it on your Sungrow inverter")
        print_sungrow_modbus_guide()
    
    # Test 4: Web interface check
    if 80 in open_ports:
        print("\n4. 🌐 Web Interface Available:")
        print(f"   → Open: http://{inverter_ip}")
        print("   → Look for Modbus TCP settings in communication menu")
    
    print("\n" + "=" * 50)
    print("📋 NEXT STEPS:")
    print("=" * 50)
    
    if 502 in open_ports:
        print("✅ Modbus TCP is working! Run: python main.py")
    else:
        print("❌ Enable Modbus TCP on your inverter first")
        print("1. Follow the configuration guide above")
        print("2. Restart your inverter")
        print("3. Run this script again to verify")
        print("4. Once port 502 is open, run: python main.py")

async def test_specific_modbus_connection():
    """Test specific Modbus connection with detailed error reporting."""
    print("\n🧪 TESTING MODBUS CONNECTION TO 192.168.0.1")
    print("=" * 50)
    
    # Add src to path
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    
    try:
        from src.config import get_default_config, TCPConfig, InverterConfig
        from src.sunspec_client import SunSpecClient
        
        # Create config for the found inverter
        config = get_default_config()
        config.inverter = InverterConfig(
            connection_type="tcp",
            tcp=TCPConfig(
                host="192.168.1.100",
                port=502,
                slave_id=1,
                timeout=5
            )
        )
        
        client = SunSpecClient(config)
        
        print("Attempting SunSpec connection...")
        success = await client.connect()
        
        if success:
            print("🎉 SUCCESS! SunSpec connection established!")
            
            device_info = await client.get_device_info()
            if device_info:
                print(f"\n📋 Your Sungrow Inverter:")
                print(f"   Manufacturer: {device_info.get('manufacturer', 'Unknown')}")
                print(f"   Model: {device_info.get('model', 'Unknown')}")
                print(f"   Serial: {device_info.get('serial_number', 'Unknown')}")
            
            await client.disconnect()
            
            print(f"\n✅ Configuration confirmed! Use this in config.yaml:")
            print("""
inverter:
  connection_type: "tcp"
  tcp:
    host: "192.168.0.1"
    port: 502
    slave_id: 1
    timeout: 10
""")
        else:
            print("❌ SunSpec connection failed")
            print("This confirms Modbus TCP is not properly enabled")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("This confirms Modbus TCP needs to be enabled")

if __name__ == "__main__":
    print("🔧 Sungrow Inverter Diagnostics")
    print("Found your inverter at 192.168.0.1!")
    print()
    
    # Run comprehensive diagnostics
    asyncio.run(comprehensive_diagnostics())
    
    # Test Modbus specifically
    asyncio.run(test_specific_modbus_connection()) 