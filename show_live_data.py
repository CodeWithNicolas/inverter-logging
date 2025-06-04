#!/usr/bin/env python3
"""
Live Energy Data Viewer for Sungrow Inverter
Shows real-time power, energy, and performance data
"""

import requests
import json
import time
from datetime import datetime

def format_value(value, unit="", decimals=2):
    """Format numeric values with proper units"""
    if value is None or value == "N/A":
        return "N/A"
    
    try:
        if isinstance(value, (int, float)):
            if decimals == 0:
                return f"{int(value):,} {unit}".strip()
            else:
                return f"{value:,.{decimals}f} {unit}".strip()
        return f"{value} {unit}".strip()
    except:
        return f"{value} {unit}".strip()

def show_live_energy_data():
    """Display live energy data from the Sungrow inverter"""
    base_url = "http://localhost:8888"
    
    print("⚡ SUNGROW INVERTER LIVE ENERGY DATA")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Get device info first
        print("📋 DEVICE INFORMATION:")
        response = requests.get(f"{base_url}/device/info")
        if response.status_code == 200:
            info = response.json()
            print(f"   🏭 Manufacturer: {info.get('manufacturer', 'Unknown')}")
            print(f"   📱 Model: {info.get('model', 'Unknown')}")
            print(f"   🔢 Serial: {info.get('serial_number', 'Unknown')}")
            print()
        
        # Get available models
        print("🔍 AVAILABLE SUNSPEC MODELS:")
        response = requests.get(f"{base_url}/device/models")
        if response.status_code == 200:
            models = response.json()
            available = models.get('available_models', {})
            print(f"   📊 Available Models: {', '.join(f'{k} ({v})' for k, v in available.items())}")
            print()
        
        # Get live data
        print("⚡ LIVE ENERGY DATA:")
        response = requests.get(f"{base_url}/data/live")
        if response.status_code != 200:
            print(f"   ❌ Error getting live data: {response.status_code}")
            return
            
        data = response.json()
        
        if not data:
            print("   ⚠️  No model data available")
            return
        
        # Process Model 1 (Common model - device info)
        if 'model_1' in data:
            model_1_data = data['model_1']
            points = model_1_data.get('points', {})
            timestamp = model_1_data.get('timestamp', 'Unknown')
            
            print(f"📊 MODEL 1 - DEVICE IDENTIFICATION:")
            print(f"   ⏰ Last Updated: {timestamp}")
            print("-" * 40)
            
            # Map the common model fields
            device_info = {
                'Mn': ('Manufacturer', 'SUNGROW'),
                'Md': ('Model', 'Unknown'),
                'Opt': ('Options', 'Unknown'),
                'Vr': ('Firmware Version', 'Unknown'),
                'SN': ('Serial Number', 'Unknown'),
                'DA': ('Device Address', 'Unknown'),
                'ID': ('Model ID', 'Unknown'),
                'L': ('Model Length', 'registers')
            }
            
            for key, (label, unit) in device_info.items():
                if key in points:
                    value = points[key]
                    if unit and not isinstance(value, str):
                        formatted_value = format_value(value, unit)
                    else:
                        formatted_value = value
                    print(f"   {label:20s}: {formatted_value}")
        
        # Process Model 101 (Inverter model - power data)
        if 'model_101' in data:
            model_101_data = data['model_101']
            points = model_101_data.get('points', {})
            timestamp = model_101_data.get('timestamp', 'Unknown')
            
            print(f"\n📊 MODEL 101 - INVERTER MEASUREMENTS:")
            print(f"   ⏰ Last Updated: {timestamp}")
            print("-" * 40)
            
            # Map the inverter model fields
            inverter_fields = {
                # Power measurements
                'W': ('AC Power Output', 'W'),
                'WH': ('Total Energy Produced', 'Wh'),
                'DCA': ('DC Current', 'A'),
                'DCV': ('DC Voltage', 'V'),
                'DCW': ('DC Power', 'W'),
                'ACA': ('AC Current', 'A'),
                'ACV': ('AC Voltage', 'V'),
                'PhV': ('Phase Voltage', 'V'),
                'A': ('Current', 'A'),
                'Hz': ('Grid Frequency', 'Hz'),
                'VA': ('Apparent Power', 'VA'),
                'VAr': ('Reactive Power', 'VAr'),
                'PF': ('Power Factor', ''),
                
                # Temperature measurements
                'TmpCab': ('Cabinet Temperature', '°C'),
                'TmpSnk': ('Heat Sink Temperature', '°C'),
                'TmpTrns': ('Transformer Temperature', '°C'),
                'TmpOt': ('Other Temperature', '°C'),
                
                # Status and events
                'St': ('Operating State', ''),
                'StVnd': ('Vendor State', ''),
                'Evt1': ('Event Flags 1', ''),
                'Evt2': ('Event Flags 2', ''),
                'EvtVnd1': ('Vendor Event 1', ''),
                'EvtVnd2': ('Vendor Event 2', ''),
                'EvtVnd3': ('Vendor Event 3', ''),
                'EvtVnd4': ('Vendor Event 4', ''),
            }
            
            # Show main power measurements first
            power_found = False
            print("   ⚡ POWER & ENERGY:")
            power_keys = ['W', 'WH', 'DCA', 'DCV', 'DCW', 'ACA', 'ACV', 'PhV', 'Hz', 'VA', 'VAr', 'PF']
            for key in power_keys:
                if key in points and points[key] is not None:
                    label, unit = inverter_fields.get(key, (key, ''))
                    value = points[key]
                    formatted_value = format_value(value, unit)
                    print(f"      {label:25s}: {formatted_value}")
                    power_found = True
            
            # Show temperature measurements
            temp_found = False
            temp_keys = ['TmpCab', 'TmpSnk', 'TmpTrns', 'TmpOt']
            for key in temp_keys:
                if key in points and points[key] is not None:
                    if not temp_found:
                        print("   🌡️  TEMPERATURES:")
                        temp_found = True
                    label, unit = inverter_fields.get(key, (key, ''))
                    value = points[key]
                    formatted_value = format_value(value, unit)
                    print(f"      {label:25s}: {formatted_value}")
            
            # Show status information
            status_found = False
            status_keys = ['St', 'StVnd', 'Evt1', 'Evt2', 'EvtVnd1', 'EvtVnd2', 'EvtVnd3', 'EvtVnd4']
            for key in status_keys:
                if key in points and points[key] is not None:
                    if not status_found:
                        print("   📊 STATUS & EVENTS:")
                        status_found = True
                    label, unit = inverter_fields.get(key, (key, ''))
                    value = points[key]
                    print(f"      {label:25s}: {value}")
            
            # Show any other data we might have missed
            other_keys = [k for k in points.keys() if k not in inverter_fields and points[k] is not None]
            if other_keys:
                print("   📋 OTHER DATA:")
                for key in other_keys:
                    value = points[key]
                    print(f"      {key:25s}: {value}")
            
            if not power_found and not temp_found and not status_found and not other_keys:
                print("      ⚠️  No measurement data available in this model")
        
        # Handle any other models
        other_models = [k for k in data.keys() if k not in ['model_1', 'model_101']]
        for model_key in other_models:
            model_data = data[model_key]
            points = model_data.get('points', {})
            timestamp = model_data.get('timestamp', 'Unknown')
            
            print(f"\n📊 {model_key.upper()} - RAW DATA:")
            print(f"   ⏰ Last Updated: {timestamp}")
            print("-" * 40)
            for key, value in points.items():
                if value is not None:
                    print(f"   {key:25s}: {value}")
        
        print("\n" + "=" * 60)
        print("🔄 Run this script again to see updated values")
        print("⏱️  Gateway polls every 30 seconds")
        print("🌐 API: http://localhost:8888/data/live")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to gateway. Make sure it's running:")
        print("   python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")

def continuous_monitoring():
    """Show live data with continuous updates"""
    print("🔄 CONTINUOUS MONITORING MODE")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        while True:
            # Clear screen (works on most terminals)
            print("\033[2J\033[H", end="")
            show_live_energy_data()
            print("\n⏳ Next update in 10 seconds...")
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        continuous_monitoring()
    else:
        show_live_energy_data()
        print("\n💡 Tip: Run with --continuous for live updates:")
        print("   python show_live_data.py --continuous") 