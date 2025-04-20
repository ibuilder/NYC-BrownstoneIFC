#!/usr/bin/env python3
"""
Setup script for Brownstone IFC Generator

This script checks for required dependencies and attempts to install them
if they are not present.
"""

import sys
import subprocess
import platform
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.7 or newer"""
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
        print("Error: Python 3.7 or newer is required")
        print(f"Current version: {sys.version}")
        return False
    return True

def check_pip():
    """Check if pip is installed and install if not"""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', '--version'], 
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        print("pip is not installed. Installing pip...")
        try:
            subprocess.check_call([sys.executable, '-m', 'ensurepip', '--default-pip'], 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError:
            print("Failed to install pip. Please install pip manually.")
            return False

def install_package(package_name):
    """Install a Python package using pip"""
    print(f"Installing {package_name}...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package_name], 
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError:
        print(f"Failed to install {package_name}")
        return False

def install_ifcopenshell():
    """Install IfcOpenShell"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    
    # Try simple pip install first
    try:
        print("Attempting to install IfcOpenShell via pip...")
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'ifcopenshell'], 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Check if installation was successful
        if result.returncode == 0:
            print("Successfully installed IfcOpenShell via pip")
            return True
    except:
        pass
    
    print("Direct pip installation failed. Attempting alternative methods...")
    
    # If pip install fails, try alternative methods based on platform
    if system == 'windows':
        print("Detected Windows system")
        wheel_url = f"https://github.com/IfcOpenShell/IfcOpenShell/releases/download/v0.7.0/ifcopenshell-python{python_version}-{system}-{machine}.whl"
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', wheel_url], 
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Successfully installed IfcOpenShell from GitHub release")
            return True
        except subprocess.CalledProcessError:
            print("Failed to install IfcOpenShell from GitHub release")
    else:  # Linux or macOS
        print(f"Detected {system} system")
        print("For Linux/macOS, manual installation from source may be required.")
        print("Please visit: https://ifcopenshell.org/ for installation instructions")
    
    print("\nIfcOpenShell installation guide:")
    print("1. Visit https://ifcopenshell.org/")
    print("2. Download the appropriate version for your system")
    print("3. Follow the installation instructions on the website")
    
    return False

def check_imports():
    """Check if required packages can be imported"""
    required_packages = {
        'numpy': 'numpy',
        'ifcopenshell': None,  # Special handling for IfcOpenShell
        'pyvista': 'pyvista'
    }
    
    missing_packages = []
    
    for package, pip_name in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(pip_name if pip_name else package)
    
    return missing_packages

def setup():
    """Main setup function"""
    print("Brownstone IFC Generator Setup")
    print("==============================")
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check pip
    if not check_pip():
        return False
    
    # Check for required packages
    missing_packages = check_imports()
    
    # Install missing packages
    if missing_packages:
        print("\nInstalling missing packages...")
        
        # Install numpy and pyvista first if needed
        for package in missing_packages[:]:
            if package and package != 'ifcopenshell':
                if install_package(package):
                    missing_packages.remove(package)
        
        # Handle IfcOpenShell separately
        if 'ifcopenshell' in missing_packages:
            install_ifcopenshell()
    
    # Final check
    print("\nPerforming final check...")
    missing_packages = check_imports()
    
    if missing_packages:
        print("\n⚠️ Setup incomplete. Some packages could not be installed:")
        for package in missing_packages:
            print(f"  - {package}")
        return False
    else:
        print("\n✅ Setup complete. All required packages are installed.")
        return True

def main():
    """Main entry point"""
    success = setup()
    
    if success:
        print("\nYou can now run the brownstone IFC generator:")
        print("python brownstone-ifc-generator.py")
        print("\nAnd visualize the result with:")
        print("python brownstone-ifc-viewer.py")
    else:
        print("\nSetup incomplete. Please resolve the issues above before running the scripts.")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
