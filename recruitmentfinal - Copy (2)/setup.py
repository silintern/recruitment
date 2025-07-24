#!/usr/bin/env python3
"""
Setup script for the Recruitment Management System
This script installs all dependencies and prepares the system for use
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Recruitment Management System")
    print("=" * 50)
    
    current_dir = Path(__file__).parent
    
    # Install dashboard dependencies
    dashboard_dir = current_dir / "dashboard"
    if dashboard_dir.exists():
        os.chdir(dashboard_dir)
        success = run_command(
            f"{sys.executable} -m pip install -r requirements.txt",
            "Installing dashboard dependencies"
        )
        if not success:
            print("❌ Failed to install dashboard dependencies")
            return False
    
    # Install form backend dependencies
    form_backend_dir = current_dir / "form-backend"
    if form_backend_dir.exists():
        os.chdir(form_backend_dir)
        success = run_command(
            f"{sys.executable} -m pip install -r requirements.txt",
            "Installing form backend dependencies"
        )
        if not success:
            print("❌ Failed to install form backend dependencies")
            return False
    
    # Return to original directory
    os.chdir(current_dir)
    
    # Test imports
    print("🧪 Testing system functionality...")
    try:
        import flask
        import flask_cors
        import pandas
        import sqlite3
        print("✅ All required packages are available")
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        return False
    
    # Create upload directories
    upload_dirs = [
        dashboard_dir / "uploads",
        form_backend_dir / "uploads"
    ]
    
    for upload_dir in upload_dirs:
        upload_dir.mkdir(exist_ok=True)
        print(f"✅ Created upload directory: {upload_dir}")
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Run: python3 start_servers.py")
    print("2. Access dashboard: http://localhost:5000")
    print("3. Open recruitment form: campus/recruitment-form.html")
    print("\n🔐 Default Login:")
    print("   Email: admin@adventz.com")
    print("   Password: 12345")
    print("\n" + "=" * 50)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)