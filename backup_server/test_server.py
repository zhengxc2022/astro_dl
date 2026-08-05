#!/usr/bin/env python3
"""
Quick test script to verify the web server is working correctly
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_server():
    print("Testing Astronomical Image Downloader Web Server...")
    print("=" * 60)
    
    # Test 1: Get all surveys
    print("\n📡 Test 1: Fetching all surveys...")
    try:
        response = requests.get(f"{BASE_URL}/api/surveys")
        if response.status_code == 200:
            surveys = response.json()
            print(f"✓ Successfully loaded {len(surveys)} surveys:")
            for key, survey in surveys.items():
                print(f"  - {key}: {survey['name']}")
        else:
            print(f"✗ Failed with status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("\n💡 Make sure to start the server first:")
        print("   cd /home/zhengxc/works/my_script/dltools_web")
        print("   python app.py")
        return False
    
    # Test 2: Get specific survey params
    print("\n📡 Test 2: Fetching VLASS parameters...")
    try:
        response = requests.get(f"{BASE_URL}/api/survey/vlass")
        if response.status_code == 200:
            config = response.json()
            print(f"✓ VLASS config loaded:")
            print(f"  Method: {config['method']}")
            print(f"  Parameters:")
            for key, param in config['params'].items():
                print(f"    - {key}: {param['label']}")
        else:
            print(f"✗ Failed with status code: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print(f"\n🌐 Open your browser and go to: {BASE_URL}")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    test_server()
