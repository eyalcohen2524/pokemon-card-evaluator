#!/usr/bin/env python3
"""
Setup script for Pokemon Card Price Checker
Installs dependencies and tests the system
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"   ✅ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed: {e}")
        print(f"   Output: {e.stdout}")
        print(f"   Error: {e.stderr}")
        return False

def check_system_requirements():
    """Check if system has required tools"""
    print("🔍 Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print(f"   ❌ Python 3.8+ required, found {sys.version}")
        return False
    print(f"   ✅ Python {sys.version}")
    
    # Check if tesseract is installed
    try:
        result = subprocess.run(['tesseract', '--version'], capture_output=True, text=True)
        print(f"   ✅ Tesseract installed")
    except FileNotFoundError:
        print(f"   ❌ Tesseract not found. Please install:")
        print(f"      macOS: brew install tesseract")
        print(f"      Ubuntu: apt-get install tesseract-ocr")
        return False
    
    return True

def install_dependencies():
    """Install Python dependencies in a virtual environment"""
    project_dir = os.path.dirname(__file__)
    backend_dir = os.path.join(project_dir, 'backend')
    requirements_file = os.path.join(backend_dir, 'requirements.txt')
    venv_dir = os.path.join(project_dir, 'venv')
    
    if not os.path.exists(requirements_file):
        print(f"   ❌ Requirements file not found: {requirements_file}")
        return False
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists(venv_dir):
        if not run_command(f"python3 -m venv {venv_dir}", "Creating virtual environment"):
            return False
    
    # Activate virtual environment and install packages
    activate_script = os.path.join(venv_dir, 'bin', 'activate')
    cmd = f"source {activate_script} && pip install -r {requirements_file}"
    return run_command(cmd, "Installing Python dependencies in virtual environment")

def create_test_image():
    """Create a simple test image for validation"""
    print("🎨 Creating test image...")
    
    try:
        import cv2
        import numpy as np
        
        # Create a simple test image that looks like a card
        img = np.ones((400, 300, 3), dtype=np.uint8) * 255  # White background
        
        # Add some text-like elements
        cv2.rectangle(img, (20, 20), (280, 80), (0, 0, 0), 2)  # Card border
        cv2.putText(img, "CHARIZARD", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(img, "120 HP", (200, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(img, "4/102", (240, 380), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        # Save test image
        test_image_path = "data/test_card.jpg"
        os.makedirs("data", exist_ok=True)
        cv2.imwrite(test_image_path, img)
        
        print(f"   ✅ Test image created: {test_image_path}")
        return test_image_path
        
    except Exception as e:
        print(f"   ❌ Failed to create test image: {e}")
        return None

def test_identification():
    """Test the card identification system"""
    print("🧪 Testing card identification...")
    
    test_image = create_test_image()
    if not test_image:
        return False
    
    # Test the main script using virtual environment
    project_dir = os.path.dirname(__file__)
    backend_dir = os.path.join(project_dir, 'backend')
    venv_dir = os.path.join(project_dir, 'venv')
    activate_script = os.path.join(venv_dir, 'bin', 'activate')
    
    cmd = f"cd {backend_dir} && source {activate_script} && python main.py ../{test_image}"
    return run_command(cmd, "Running identification test")

def main():
    """Main setup process"""
    print("🚀 Setting up Pokemon Card Price Checker")
    print("=" * 50)
    
    # Check system requirements
    if not check_system_requirements():
        print("\n❌ System requirements not met. Please install missing components.")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Failed to install dependencies.")
        sys.exit(1)
    
    # Test the system
    if not test_identification():
        print("\n❌ System test failed.")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Add real Pokemon card images to data/ folder")
    print("2. Activate virtual environment: source venv/bin/activate")
    print("3. Test with: cd backend && python main.py ../data/your_card.jpg")
    print("4. Check backend/identification_result.json for detailed results")
    print("\nTo run the API server:")
    print("   source venv/bin/activate")
    print("   cd backend && python -m api.server")

if __name__ == "__main__":
    main()