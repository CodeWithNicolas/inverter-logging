#!/usr/bin/env python3
"""
Direct Connection Setup Script for SunSpec Gateway.
Helps configure and test direct Ethernet connections to inverters.
"""

import sys
import asyncio
import socket
import subprocess
import platform
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import get_default_config, TCPConfig, InverterConfig
from src.sunspec_client import SunSpecClient


def get_network_info():
    """Get current network configuration."""
    print("🌐 Current Network Configuration:")
    print("=" * 40)
    
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"Computer hostname: {hostname}")
        print(f"Computer IP: {local_ip}")
        
        # Check if it's APIPA range (169.254.x.x)
        if local_ip.startswith("169.254."):
            print("📍 Detected APIPA address - this indicates direct connection!")
            return local_ip, True
        else:
            print("📍 Regular network IP detected")
            return local_ip, False
            
    except Exception as e:
        print(f"❌ Could not determine network info: {e}")
        return None, False


def suggest_inverter_ips(computer_ip):
    """Suggest likely inverter IP addresses based on computer IP."""
    if not computer_ip:
        return []
        
    if computer_ip.startswith("169.254."):
        # APIPA range - inverter could be anywhere in this range
        # Common static IPs that inverters use:
        common_ips = [
            "169.254.1.1",
            "169.254.1.100", 
            "169.254.100.1",
            "192.168.1.1",      # Some inverters use static IPs
            "192.168.1.100",
            "192.168.0.1",
            "10.0.0.1"
        ]
        
        # Also try same subnet as computer
        parts = computer_ip.split('.')
        subnet_base = f"{parts[0]}.{parts[1]}.{parts[2]}"
        
        # Add some IPs in the same subnet
        for i in [1, 2, 3, 4, 5, 10, 100, 200]:
            candidate = f"{subnet_base}.{i}"
            if candidate != computer_ip:  # Don't test our own IP
                common_ips.append(candidate)
                
        return common_ips
    else:
        # Regular network - scan same subnet
        parts = computer_ip.split('.')
        subnet_base = f"{parts[0]}.{parts[1]}.{parts[2]}"
        return [f"{subnet_base}.{i}" for i in range(1, 255) if f"{subnet_base}.{i}" != computer_ip]


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


def scan_direct_connection_ips(computer_ip):
    """Scan for responsive IPs in direct connection scenario."""
    print("\n🔍 Scanning for responsive devices...")
    print("=" * 40)
    
    candidate_ips = suggest_inverter_ips(computer_ip)
    responsive_ips = []
    
    print(f"Testing {len(candidate_ips)} potential inverter IP addresses...")
    
    for ip in candidate_ips[:20]:  # Limit to first 20 to be reasonable
        print(f"  Testing {ip}...", end="", flush=True)
        if test_ping(ip):
            print(" ✅ RESPONDS!")
            responsive_ips.append(ip)
        else:
            print(" ❌")
    
    return responsive_ips


async def test_modbus_connection(ip_address, port=502):
    """Test Modbus connection to an IP."""
    print(f"\n🔧 Testing Modbus connection to {ip_address}:{port}...")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3.0)
    
    try:
        result = sock.connect_ex((ip_address, port))
        if result == 0:
            print(f"   ✅ Modbus port {port} is open!")
            return True
        else:
            print(f"   ❌ Modbus port {port} is closed or filtered")
            return False
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False
    finally:
        sock.close()


async def test_sunspec_on_ip(ip_address):
    """Test SunSpec protocol on an IP address."""
    print(f"\n🌟 Testing SunSpec protocol on {ip_address}...")
    
    # Create temporary config
    config = get_default_config()
    config.inverter = InverterConfig(
        connection_type="tcp",
        tcp=TCPConfig(
            host=ip_address,
            port=502,
            slave_id=1,
            timeout=10
        )
    )
    
    client = SunSpecClient(config)
    
    try:
        success = await client.connect()
        
        if success:
            print(f"   ✅ SunSpec connection successful!")
            
            # Get device info
            device_info = await client.get_device_info()
            if device_info:
                print(f"   📋 Device Details:")
                print(f"      Manufacturer: {device_info.get('manufacturer', 'Unknown')}")
                print(f"      Model: {device_info.get('model', 'Unknown')}")
                print(f"      Serial: {device_info.get('serial_number', 'Unknown')}")
                
            # List models
            print(f"   📊 Available Models: {list(client.available_models.keys())}")
            
            await client.disconnect()
            return True
        else:
            print(f"   ❌ SunSpec connection failed")
            return False
            
    except Exception as e:
        print(f"   ❌ SunSpec error: {e}")
        return False


def print_connection_guide():
    """Print guide for setting up direct connection."""
    print("\n" + "=" * 60)
    print("📚 DIRECT CONNECTION SETUP GUIDE")
    print("=" * 60)
    print()
    print("For Sungrow inverters with direct Ethernet connection:")
    print()
    print("1. 🔌 PHYSICAL CONNECTION:")
    print("   - Connect Ethernet cable from your computer to inverter")
    print("   - Wait 30 seconds for link to establish")
    print()
    print("2. ⚙️ INVERTER SETTINGS:")
    print("   - Access inverter menu (usually via LCD display)")
    print("   - Navigate to: Settings → Communication → Ethernet")
    print("   - Enable: Modbus TCP")
    print("   - Note the IP address (or set static IP like 192.168.1.100)")
    print("   - Port should be 502 (default)")
    print("   - Slave ID usually 1")
    print()
    print("3. 💻 COMPUTER NETWORK SETTINGS (if needed):")
    print("   - If inverter has static IP (e.g., 192.168.1.100):")
    print("     Set your computer to same subnet (e.g., 192.168.1.50)")
    print("   - If both use APIPA (169.254.x.x), should work automatically")
    print()
    print("4. 🧪 TEST CONNECTION:")
    print("   - Use this script to find your inverter")
    print("   - Update config.yaml with the correct IP")
    print("   - Run: python main.py")


async def main():
    """Main direct connection setup function."""
    print("🔗 SunSpec Direct Connection Setup")
    print("=" * 50)
    
    # Step 1: Check network configuration
    computer_ip, is_direct = get_network_info()
    
    if not computer_ip:
        print("❌ Could not determine network configuration")
        return
    
    if not is_direct:
        print("⚠️  Warning: This doesn't look like a direct connection")
        print("   Your IP suggests you're on a regular network")
        print("   This script is optimized for direct inverter connections")
        print()
    
    # Step 2: Scan for responsive devices
    responsive_ips = scan_direct_connection_ips(computer_ip)
    
    if not responsive_ips:
        print("\n❌ No responsive devices found!")
        print_connection_guide()
        return
    
    print(f"\n✅ Found {len(responsive_ips)} responsive device(s):")
    for ip in responsive_ips:
        print(f"   📍 {ip}")
    
    # Step 3: Test Modbus on responsive IPs
    modbus_devices = []
    for ip in responsive_ips:
        if await test_modbus_connection(ip):
            modbus_devices.append(ip)
    
    if not modbus_devices:
        print("\n❌ No devices with Modbus port open found!")
        print("   Try enabling Modbus TCP on your inverter")
        print_connection_guide()
        return
    
    # Step 4: Test SunSpec on Modbus devices
    sunspec_devices = []
    for ip in modbus_devices:
        if await test_sunspec_on_ip(ip):
            sunspec_devices.append(ip)
    
    # Step 5: Results and configuration
    print("\n" + "=" * 50)
    print("📋 DISCOVERY RESULTS")
    print("=" * 50)
    
    if sunspec_devices:
        print(f"🎉 Found {len(sunspec_devices)} SunSpec inverter(s)!")
        
        for ip in sunspec_devices:
            print(f"\n✅ Inverter found at: {ip}")
            print(f"📝 Add this to your config.yaml:")
            print(f"""
inverter:
  connection_type: "tcp"
  tcp:
    host: "{ip}"
    port: 502
    slave_id: 1
    timeout: 10
""")
        
        print("🚀 Next steps:")
        print("1. Update config.yaml with the IP above")
        print("2. Run: python main.py")
        print("3. Test: curl -X POST http://localhost:8080/connect")
        
    else:
        print("❌ No SunSpec-compatible devices found")
        if modbus_devices:
            print(f"   Found Modbus devices at: {modbus_devices}")
            print("   But they don't respond to SunSpec protocol")
            print("   Check if SunSpec is enabled on your inverter")
        print_connection_guide()


if __name__ == "__main__":
    asyncio.run(main()) 