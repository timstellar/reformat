import os
import requests
import json
from PIL import Image
from io import BytesIO

# Test script for QR code URL generation functionality
print("Testing QR Code URL Generation Functionality")

# Ensure the service is running
service_url = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{service_url}/health")
        if response.status_code == 200 and response.json()["status"] == "healthy":
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Health check failed with exception: {str(e)}")
        return False

def test_qr_code_get_request():
    """Test generating a QR code using GET request"""
    try:
        test_url = "https://example.com"
        response = requests.get(
            f"{service_url}/api/v1/generate-qr",
            params={"url": test_url, "size": 200, "format": "png"}
        )
        
        if response.status_code == 200:
            # Save the QR code
            output_path = "temp/test_qr_code_get.png"
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            # Verify it's a valid image
            try:
                img = Image.open(BytesIO(response.content))
                print(f"✅ QR code GET request successful: {output_path} (Size: {img.size})")
                return True
            except Exception as e:
                print(f"❌ QR code validation failed: {str(e)}")
                return False
        else:
            print(f"❌ QR code GET request failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ QR code GET request failed with exception: {str(e)}")
        return False

def test_qr_code_post_request():
    """Test generating a QR code using POST request"""
    try:
        test_url = "https://example.org"
        response = requests.post(
            f"{service_url}/api/v1/generate-qr",
            json={"url": test_url, "size": 300, "format": "png"}
        )
        
        if response.status_code == 200:
            # Save the QR code
            output_path = "temp/test_qr_code_post.png"
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            # Verify it's a valid image
            try:
                img = Image.open(BytesIO(response.content))
                print(f"✅ QR code POST request successful: {output_path} (Size: {img.size})")
                return True
            except Exception as e:
                print(f"❌ QR code validation failed: {str(e)}")
                return False
        else:
            print(f"❌ QR code POST request failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ QR code POST request failed with exception: {str(e)}")
        return False

def test_qr_generator_page():
    """Test the QR generator web page"""
    try:
        response = requests.get(f"{service_url}/qr-generator")
        
        if response.status_code == 200:
            print("✅ QR generator page loaded successfully")
            return True
        else:
            print(f"❌ QR generator page failed to load: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ QR generator page failed with exception: {str(e)}")
        return False

def run_tests():
    """Run all tests"""
    # First check if service is running
    if not test_health_check():
        print("Service is not running. Please start the service with 'python app.py'")
        return False
    
    # Run tests
    test_results = [
        test_qr_code_get_request(),
        test_qr_code_post_request(),
        test_qr_generator_page()
    ]
    
    # Print summary
    success_count = sum(test_results)
    total_count = len(test_results)
    print(f"\nTest Summary: {success_count}/{total_count} tests passed")
    
    return all(test_results)

if __name__ == "__main__":
    run_tests()
