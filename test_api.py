#!/usr/bin/env python3
"""
Quick test script to verify the gateway API endpoints are working.
"""

import requests
import json
import time

def test_endpoint(url, description):
    """Test a single endpoint and print results."""
    try:
        print(f"\n🧪 Testing {description}")
        print(f"   URL: {url}")
        
        response = requests.get(url, timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success! Data keys: {list(data.keys())}")
            return True
        else:
            print(f"   ❌ Failed: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"   ⏰ Timeout after 5 seconds")
        return False
    except requests.exceptions.ConnectionError:
        print(f"   🔌 Connection failed")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Test all endpoints the dashboard needs."""
    base_url = "http://192.168.1.102:8080"
    
    print("🌞 Testing Solar Gateway API Endpoints")
    print("=" * 50)
    
    # Test all endpoints the dashboard calls
    endpoints = [
        ("/health", "Health Check"),
        ("/device/info", "Device Information"),
        ("/data/live", "Live Data"),
    ]
    
    results = []
    for endpoint, description in endpoints:
        success = test_endpoint(f"{base_url}{endpoint}", description)
        results.append((endpoint, success))
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print("\n📊 Test Results Summary:")
    print("=" * 30)
    for endpoint, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {endpoint}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\n🎯 Overall: {passed}/{total} endpoints working")
    
    if passed == total:
        print("🎉 All endpoints working! Web dashboard should work perfectly.")
    else:
        print("⚠️  Some endpoints failed. Web dashboard may show connection errors.")

if __name__ == "__main__":
    main() 