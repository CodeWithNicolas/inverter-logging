#!/usr/bin/env python3
"""
Basic test script to verify the SunSpec Gateway components.
Run this to check if everything is set up correctly.
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import load_config, get_default_config
from src.sunspec_client import SunSpecClient


async def test_basic_setup():
    """Test basic setup and configuration loading."""
    print("🧪 Testing SunSpec Gateway Setup...")
    print("=" * 50)
    
    # Test 1: Configuration loading
    print("1. Testing configuration loading...")
    try:
        # Test with default config since we might not have a config file yet
        config = get_default_config()
        print(f"   ✅ Default config loaded successfully")
        print(f"   Gateway: {config.gateway.name} v{config.gateway.version}")
        print(f"   Connection: {config.inverter.connection_type}")
        
        # Try to load from file if it exists
        if Path("config.yaml").exists():
            file_config = load_config("config.yaml")
            print(f"   ✅ File config loaded successfully")
            print(f"   Inverter host: {file_config.inverter.tcp.host if file_config.inverter.tcp else 'N/A'}")
        else:
            print(f"   ⚠️  config.yaml not found, using defaults")
            
    except Exception as e:
        print(f"   ❌ Configuration loading failed: {e}")
        return False
    
    # Test 2: SunSpec client initialization
    print("\n2. Testing SunSpec client initialization...")
    try:
        client = SunSpecClient(config)
        print(f"   ✅ SunSpec client created successfully")
        print(f"   Connection type: {client.config.inverter.connection_type}")
    except Exception as e:
        print(f"   ❌ SunSpec client creation failed: {e}")
        return False
    
    # Test 3: Import all modules
    print("\n3. Testing module imports...")
    try:
        from src.gateway import SunSpecGateway
        print(f"   ✅ Gateway module imported successfully")
        
        # Try to create gateway instance (without connecting)
        gateway = SunSpecGateway(config)
        print(f"   ✅ Gateway instance created successfully")
        print(f"   API routes: {len(gateway.app.routes)} routes configured")
        
    except Exception as e:
        print(f"   ❌ Gateway creation failed: {e}")
        return False
    
    # Test 4: Dependencies check
    print("\n4. Testing dependencies...")
    try:
        import sunspec2.modbus.client
        print(f"   ✅ pySunSpec2 imported successfully")
        
        import fastapi
        print(f"   ✅ FastAPI imported successfully")
        
        import pydantic
        print(f"   ✅ Pydantic imported successfully")
        
        import yaml
        print(f"   ✅ PyYAML imported successfully")
        
    except Exception as e:
        print(f"   ❌ Dependency check failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All basic tests passed!")
    print()
    print("Next steps:")
    print("1. Update config.yaml with your inverter's IP address")
    print("2. Run: python main.py")
    print("3. Test connection: curl -X POST http://localhost:8080/connect")
    print()
    print("For your Sungrow inverter connected via network cable:")
    print("- Make sure Modbus TCP is enabled on the inverter")
    print("- Check the inverter's IP address (usually in network settings)")
    print("- Default Modbus port is 502, slave ID is usually 1")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_basic_setup())
    sys.exit(0 if success else 1) 