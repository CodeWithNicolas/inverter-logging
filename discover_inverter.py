#!/usr/bin/env python3
"""
Inverter Discovery Script for SunSpec Gateway.
Helps discover and test connection to SunSpec-compliant inverters.
"""

import sys
import asyncio
import socket
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import get_default_config, TCPConfig, InverterConfig
from src.sunspec_client import SunSpecClient


def scan_network_for_modbus(network_base="192.168.1", start_ip=1, end_ip=254):
    """Scan network for devices listening on Modbus port 502."""
    print(f"🔍 Scanning {network_base}.{start_ip}-{end_ip} for Modbus devices (port 502)...")
    found_devices = []
    
    for i in range(start_ip, end_ip + 1):
        ip = f"{network_base}.{i}"
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)  # 500ms timeout
        
        try:
            result = sock.connect_ex((ip, 502))
            if result == 0:
                print(f"   ✅ Found device at {ip}:502")
                found_devices.append(ip)
        except:
            pass
        finally:
            sock.close()
    
    return found_devices


async def test_sunspec_connection(ip_address, slave_id=1, timeout=10):
    """Test SunSpec connection to a specific IP address."""
    print(f"\n🧪 Testing SunSpec connection to {ip_address}...")
    
    # Create temporary config
    config = get_default_config()
    config.inverter = InverterConfig(
        connection_type="tcp",
        tcp=TCPConfig(
            host=ip_address,
            port=502,
            slave_id=slave_id,
            timeout=timeout
        )
    )
    
    client = SunSpecClient(config)
    
    try:
        # Attempt connection
        success = await client.connect()
        
        if success:
            print(f"   ✅ Successfully connected to SunSpec device!")
            
            # Get device information
            device_info = await client.get_device_info()
            if device_info:
                print(f"   📋 Device Information:")
                print(f"      Manufacturer: {device_info.get('manufacturer', 'Unknown')}")
                print(f"      Model: {device_info.get('model', 'Unknown')}")
                print(f"      Version: {device_info.get('version', 'Unknown')}")
                print(f"      Serial Number: {device_info.get('serial_number', 'Unknown')}")
            
            # List available models
            print(f"   📊 Available SunSpec Models:")
            for model_id, model_name in client.available_models.items():
                print(f"      Model {model_id}: {model_name}")
            
            # Test reading some basic data
            try:
                data = await client.read_data([1, 103, 113, 160])  # Common models
                if data:
                    print(f"   📈 Sample Data Reading Successful:")
                    for model_key, model_data in data.items():
                        if model_data and 'points' in model_data:
                            points = model_data['points']
                            if points:
                                print(f"      {model_data.get('model_name', model_key)}: {len(points)} data points")
                                # Show a few key points if available
                                for key in ['W', 'A', 'Hz', 'Mn', 'Md']:
                                    if key in points:
                                        print(f"        {key}: {points[key]}")
            except Exception as e:
                print(f"   ⚠️  Could not read data: {e}")
            
            await client.disconnect()
            return True
            
        else:
            print(f"   ❌ Failed to connect to SunSpec device")
            return False
            
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False


async def discover_inverters():
    """Main discovery function."""
    print("🚀 SunSpec Inverter Discovery Tool")
    print("=" * 50)
    
    # Step 1: Try to find your local network range
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"💻 Your computer's IP: {local_ip}")
        
        # Extract network base (assuming /24 subnet)
        network_parts = local_ip.split('.')
        network_base = '.'.join(network_parts[:3])
        print(f"🌐 Scanning network: {network_base}.x")
        
    except Exception as e:
        print(f"⚠️  Could not determine local IP: {e}")
        network_base = "192.168.1"  # Default assumption
        print(f"🌐 Using default network: {network_base}.x")
    
    # Step 2: Scan for Modbus devices
    print()
    modbus_devices = scan_network_for_modbus(network_base)
    
    if not modbus_devices:
        print("❌ No Modbus devices found on the network.")
        print("\nTroubleshooting tips:")
        print("1. Ensure your inverter is connected to the same network")
        print("2. Check if Modbus TCP is enabled on your inverter")
        print("3. Try a different network range if needed")
        print("4. Check inverter manual for network configuration")
        return
    
    print(f"\n📋 Found {len(modbus_devices)} device(s) with Modbus port open")
    
    # Step 3: Test each device for SunSpec compatibility
    sunspec_devices = []
    
    for ip in modbus_devices:
        result = await test_sunspec_connection(ip)
        if result:
            sunspec_devices.append(ip)
    
    # Step 4: Summary and configuration
    print("\n" + "=" * 50)
    
    if sunspec_devices:
        print(f"🎉 Found {len(sunspec_devices)} SunSpec-compatible device(s)!")
        print("\n📝 To use your inverter, update config.yaml:")
        
        for ip in sunspec_devices:
            print(f"""
inverter:
  connection_type: "tcp"
  tcp:
    host: "{ip}"
    port: 502
    slave_id: 1
    timeout: 10
""")
        
        print("Then run: python main.py")
        
    else:
        print("❌ No SunSpec-compatible devices found.")
        print("\nThis could mean:")
        print("1. Your inverter doesn't support SunSpec (check manual)")
        print("2. SunSpec is disabled (check inverter settings)")
        print("3. Different slave ID is needed (try 1-247)")
        print("4. Firewall is blocking connections")


async def test_specific_ip():
    """Test a specific IP address provided by user."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test specific IP for SunSpec compatibility")
    parser.add_argument("ip", help="IP address to test")
    parser.add_argument("--slave-id", type=int, default=1, help="Modbus slave ID (default: 1)")
    
    args = parser.parse_args()
    
    print(f"🧪 Testing specific IP: {args.ip}")
    print("=" * 50)
    
    success = await test_sunspec_connection(args.ip, args.slave_id)
    
    if success:
        print(f"\n✅ {args.ip} is SunSpec compatible!")
    else:
        print(f"\n❌ {args.ip} is not responding or not SunSpec compatible")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # If IP address provided as argument, test it directly
        asyncio.run(test_specific_ip())
    else:
        # Run full discovery
        asyncio.run(discover_inverters()) 