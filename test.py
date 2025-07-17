#!/usr/bin/env python3
"""
Console test script for GST verification
Usage: python console_test.py
"""

import requests
import json
import sys

def test_gst_verification():
    """Test GST verification through console"""
    
    # Base URL for the Flask app
    BASE_URL = "http://localhost:5000"
    
    print("GST Number Verification Console Test")
    print("=" * 50)
    
    while True:
        try:
            # Get GST number from user
            gst_number = input("\nEnter GST number (or 'quit' to exit): ").strip()
            
            if gst_number.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not gst_number:
                print("Please enter a valid GST number")
                continue
            
            # Make API request
            print(f"Verifying GST number: {gst_number}")
            print("Please wait...")
            
            response = requests.post(
                f"{BASE_URL}/api/verify-gst-console",
                json={"gst_number": gst_number},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("\n" + data.get('console_output', 'No output available'))
                    
                    # Also show raw data
                    if data.get('raw_data'):
                        print("\nRaw Data (JSON):")
                        print(json.dumps(data['raw_data'], indent=2))
                else:
                    print(f"Error: {data.get('error', 'Unknown error')}")
            else:
                error_data = response.json()
                print(f"API Error: {error_data.get('error', 'Unknown error')}")
                
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except requests.exceptions.ConnectionError:
            print("Error: Cannot connect to the Flask app. Make sure it's running on http://localhost:5000")
            break
        except requests.exceptions.Timeout:
            print("Error: Request timed out. The website might be slow to respond.")
        except Exception as e:
            print(f"Error: {str(e)}")

def test_sample_gst_numbers():
    """Test with sample GST numbers"""
    sample_numbers = [
        "37AAACP2678Q1ZP",  # From the image
        "27AAACP2678Q1ZP",
        "09AAACP2678Q1ZP"
    ]
    
    BASE_URL = "http://localhost:5000"
    
    print("Testing Sample GST Numbers")
    print("=" * 50)
    
    for gst_number in sample_numbers:
        print(f"\nTesting: {gst_number}")
        print("-" * 30)
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/verify-gst-console",
                json={"gst_number": gst_number},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(data.get('console_output', 'No output available'))
                else:
                    print(f"Error: {data.get('error', 'Unknown error')}")
            else:
                error_data = response.json()
                print(f"API Error: {error_data.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--sample":
        test_sample_gst_numbers()
    else:
        test_gst_verification()