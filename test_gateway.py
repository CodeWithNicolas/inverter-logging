#!/usr/bin/env python3
"""
Test script to demonstrate your working SunSpec Gateway
"""

import requests
import json
import time

def test_gateway():
    """Test all gateway endpoints and show live data"""
    base_url = "http://localhost:8888"
    
    print("🔍 Testing your SunSpec Gateway with Sungrow Inverter")
    print("=" * 60)
    
    try:
        # Test 1: Gateway status
        print("1. 📊 Gateway Status:")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Name: {data['name']}")
            print(f"   ✅ Version: {data['version']}")
            print(f"   ✅ Status: {data['status']}")
            print(f"   ✅ Connected: {data['connected']}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            return
        
        # Test 2: Device information
        print("\n2. 🔌 Inverter Device Information:")
        response = requests.get(f"{base_url}/device/info")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Manufacturer: {data.get('manufacturer', 'Unknown')}")
            print(f"   ✅ Model: {data.get('model', 'Unknown')}")
            print(f"   ✅ Serial: {data.get('serial_number', 'Unknown')}")
            print(f"   ✅ Firmware: {data.get('version', 'Unknown')}")
        else:
            print(f"   ⚠️  Device info not available: {response.status_code}")
        
        # Test 3: Live data
        print("\n3. ⚡ Live Inverter Data:")
        response = requests.get(f"{base_url}/data/live")
        if response.status_code == 200:
            data = response.json()
            
            # Show key measurements
            model_data = data.get('models', {})
            if '101' in model_data:  # Inverter model
                inv_data = model_data['101']
                print(f"   ✅ AC Power: {inv_data.get('W', 'N/A')} W")
                print(f"   ✅ AC Current: {inv_data.get('A', 'N/A')} A")
                print(f"   ✅ AC Voltage: {inv_data.get('PhV', 'N/A')} V")
                print(f"   ✅ Frequency: {inv_data.get('Hz', 'N/A')} Hz")
                print(f"   ✅ Energy Total: {inv_data.get('WH', 'N/A')} Wh")
                print(f"   ✅ Temperature: {inv_data.get('TmpCab', 'N/A')} °C")
            else:
                print(f"   📋 Raw data available:")
                for model_id, model_data in data.get('models', {}).items():
                    print(f"     Model {model_id}: {len(model_data)} data points")
        else:
            print(f"   ⚠️  Live data not available: {response.status_code}")
        
        # Test 4: List available endpoints
        print("\n4. 🌐 Available API Endpoints:")
        endpoints = [
            "/",
            "/device/info",
            "/device/models",
            "/data/live",
            "/data/history",
            "/control/start",
            "/control/stop",
        ]
        
        for endpoint in endpoints:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            status = "✅ Working" if response.status_code == 200 else f"⚠️  {response.status_code}"
            print(f"   {endpoint:20s}: {status}")
        
        print("\n" + "=" * 60)
        print("🎉 SUCCESS! Your SunSpec Gateway is fully operational!")
        print(f"🌐 Access your gateway at: http://localhost:8888")
        print("📖 API Documentation: http://localhost:8888/docs")
        print("🔍 Real-time monitoring: http://localhost:8888/data/live")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to gateway. Make sure it's running:")
        print("   python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_gateway() 