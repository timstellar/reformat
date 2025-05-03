import os
import requests
import json
from PIL import Image
from io import BytesIO

# Test script for updated QR code layout in PDF
print("Testing Updated QR Code Layout in PDF")

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

def test_waste_transfer_act_updated_layout():
    """Test generating a waste transfer act PDF with updated QR code layout"""
    try:
        # Load example data
        example_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "examples", "waste_transfer_act_example.json")
        with open(example_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Ensure qr_url is present
        if not data.get('qr_url'):
            print("❌ qr_url field is missing in waste_transfer_act_example.json")
            return False
        
        # Send request to generate PDF
        response = requests.post(
            f"{service_url}/api/v1/waste-transfer-act",
            json=data
        )
        
        if response.status_code == 200:
            # Save the PDF
            output_path = "temp/test_waste_transfer_act_updated_layout.pdf"
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"✅ Waste transfer act PDF with updated layout generated successfully: {output_path}")
            print("   Please manually verify that:")
            print("   1. Only one QR code appears on the left side")
            print("   2. The QR code is larger (150px) and positioned correctly (50px from top and left)")
            print("   3. No QR code appears on the right side")
            return True
        else:
            print(f"❌ Waste transfer act generation failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Waste transfer act generation failed with exception: {str(e)}")
        return False

def test_waste_removal_request_updated_layout():
    """Test generating a waste removal request PDF with updated QR code layout"""
    try:
        # Load example data
        example_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "examples", "waste_removal_request_example.json")
        with open(example_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Ensure qr_url is present
        if not data.get('qr_url'):
            print("❌ qr_url field is missing in waste_removal_request_example.json")
            return False
        
        # Send request to generate PDF
        response = requests.post(
            f"{service_url}/api/v1/waste-removal-request",
            json=data
        )
        
        if response.status_code == 200:
            # Save the PDF
            output_path = "temp/test_waste_removal_request_updated_layout.pdf"
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"✅ Waste removal request PDF with updated layout generated successfully: {output_path}")
            print("   Please manually verify that:")
            print("   1. Only one QR code appears on the left side")
            print("   2. The QR code is larger (150px) and positioned correctly (50px from top and left)")
            print("   3. No QR code appears on the right side")
            return True
        else:
            print(f"❌ Waste removal request generation failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Waste removal request generation failed with exception: {str(e)}")
        return False

def run_tests():
    """Run all tests"""
    # First check if service is running
    if not test_health_check():
        print("Service is not running. Please start the service with 'python app.py'")
        return False
    
    # Run tests
    test_results = [
        test_waste_transfer_act_updated_layout(),
        test_waste_removal_request_updated_layout()
    ]
    
    # Print summary
    success_count = sum(test_results)
    total_count = len(test_results)
    print(f"\nTest Summary: {success_count}/{total_count} tests passed")
    print("\nIMPORTANT: Please manually check the generated PDFs to confirm that:")
    print("1. Only one QR code appears on the left side")
    print("2. The QR code is larger (150px) and positioned correctly (50px from top and left)")
    print("3. No QR code appears on the right side")
    
    return all(test_results)

if __name__ == "__main__":
    run_tests()
