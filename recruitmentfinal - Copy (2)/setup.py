#!/usr/bin/env python3
"""
Setup script for the Recruitment Management System
This script installs all dependencies and prepares the system for use
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description, ignore_errors=False):
    """Run a command and handle errors"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        if ignore_errors:
            print(f"⚠️  {description} had issues but continuing: {e.stderr.strip()[:100]}...")
            return True
        else:
            print(f"❌ {description} failed")
            return False

def detect_environment():
    """Detect if we're in a virtual environment or need special handling"""
    # Check if in virtual environment
    in_venv = (hasattr(sys, 'real_prefix') or 
               (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))
    
    # Check if system has PEP 668 protection
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "install", "--help"], 
                              capture_output=True, text=True)
        has_break_system_packages = "--break-system-packages" in result.stdout
    except:
        has_break_system_packages = False
    
    return in_venv, has_break_system_packages

def install_package(package_name, use_break_system=False):
    """Install a package with appropriate flags"""
    base_cmd = f"{sys.executable} -m pip install {package_name}"
    
    if use_break_system:
        cmd = f"{base_cmd} --break-system-packages"
    else:
        cmd = base_cmd
    
    return run_command(cmd, f"Installing {package_name}", ignore_errors=True)

def create_virtual_environment():
    """Create and activate a virtual environment"""
    venv_path = Path("recruitment_venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return venv_path
    
    print("🔧 Creating virtual environment...")
    try:
        result = subprocess.run([sys.executable, "-m", "venv", str(venv_path)], 
                              check=True, capture_output=True, text=True)
        print("✅ Virtual environment created successfully")
        return venv_path
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e.stderr}")
        return None

def get_venv_python(venv_path):
    """Get the Python executable from virtual environment"""
    if os.name == 'nt':  # Windows
        return venv_path / "Scripts" / "python.exe"
    else:  # Unix-like
        return venv_path / "bin" / "python"

def main():
    """Main setup function"""
    print("🚀 Setting up Recruitment Management System")
    print("=" * 50)
    
    # Detect environment
    in_venv, has_break_system = detect_environment()
    
    print(f"🔍 Environment Detection:")
    print(f"   In virtual environment: {'Yes' if in_venv else 'No'}")
    print(f"   Has --break-system-packages: {'Yes' if has_break_system else 'No'}")
    
    current_dir = Path(__file__).parent
    python_cmd = sys.executable
    venv_path = None
    
    # Handle different installation strategies
    if not in_venv and not has_break_system:
        print("\n⚠️  Externally managed environment detected")
        print("🔧 Creating virtual environment for safe installation...")
        
        venv_path = create_virtual_environment()
        if venv_path:
            python_cmd = str(get_venv_python(venv_path))
            print(f"✅ Using virtual environment Python: {python_cmd}")
        else:
            print("❌ Could not create virtual environment")
            print("💡 Try running: python3 -m venv recruitment_venv")
            print("   Then: source recruitment_venv/bin/activate (Linux/macOS)")
            print("   Or: recruitment_venv\\Scripts\\activate (Windows)")
            return False
    
    # Install packages
    packages = ["Flask", "Flask-CORS", "Werkzeug", "requests"]
    
    print(f"\n📦 Installing packages using: {python_cmd}")
    
    for package in packages:
        if in_venv or venv_path:
            # In virtual environment, use normal installation
            cmd = f"{python_cmd} -m pip install {package}"
            run_command(cmd, f"Installing {package}", ignore_errors=True)
        elif has_break_system:
            # Use --break-system-packages if available
            install_package(package, use_break_system=True)
        else:
            # Fallback to normal installation
            install_package(package, use_break_system=False)
    
    # Try pandas separately
    print("\n📦 Installing pandas (optional)...")
    pandas_success = False
    
    if in_venv or venv_path:
        cmd = f"{python_cmd} -m pip install pandas"
        pandas_success = run_command(cmd, "Installing pandas", ignore_errors=True)
    elif has_break_system:
        pandas_success = install_package("pandas", use_break_system=True)
    else:
        pandas_success = install_package("pandas", use_break_system=False)
    
    # Install openpyxl
    if in_venv or venv_path:
        cmd = f"{python_cmd} -m pip install openpyxl"
        run_command(cmd, "Installing openpyxl", ignore_errors=True)
    elif has_break_system:
        install_package("openpyxl", use_break_system=True)
    else:
        install_package("openpyxl", use_break_system=False)
    
    # Test imports
    print("\n🧪 Testing system functionality...")
    test_script = """
import sys
critical_imports = []
optional_imports = []

try:
    import flask
    critical_imports.append("Flask")
except ImportError:
    print("❌ Flask import failed - this is required")

try:
    import flask_cors
    critical_imports.append("Flask-CORS")
except ImportError:
    print("❌ Flask-CORS import failed - this is required")

try:
    import sqlite3
    critical_imports.append("SQLite3")
except ImportError:
    print("❌ SQLite3 not available - this is required")

try:
    import pandas
    optional_imports.append("Pandas")
except ImportError:
    print("⚠️  Pandas not available - some features may be limited")

try:
    import openpyxl
    optional_imports.append("OpenPyXL")
except ImportError:
    print("⚠️  OpenPyXL not available - Excel export may not work")

if critical_imports:
    print(f"✅ Critical packages available: {', '.join(critical_imports)}")
if optional_imports:
    print(f"✅ Optional packages available: {', '.join(optional_imports)}")

# Check if we have minimum requirements
if len(critical_imports) >= 2:  # Flask and SQLite3 minimum
    print("✅ Minimum requirements met - system should work")
    sys.exit(0)
else:
    print("❌ Minimum requirements not met")
    sys.exit(1)
"""
    
    try:
        result = subprocess.run([python_cmd, "-c", test_script], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        requirements_met = True
    except subprocess.CalledProcessError as e:
        print(e.stdout)
        print(e.stderr)
        requirements_met = False
    
    # Create upload directories
    upload_dirs = [
        current_dir / "dashboard" / "uploads",
        current_dir / "form-backend" / "uploads"
    ]
    
    for upload_dir in upload_dirs:
        upload_dir.mkdir(exist_ok=True)
        print(f"✅ Created upload directory: {upload_dir}")
    
    # Create activation script for virtual environment
    if venv_path and venv_path.exists():
        activate_script = current_dir / "activate_env.sh"
        with open(activate_script, 'w') as f:
            f.write(f"""#!/bin/bash
# Activation script for recruitment system
echo "🚀 Activating Recruitment System Environment"
source {venv_path}/bin/activate
echo "✅ Environment activated"
echo "📋 Now run: python3 start_servers.py"
""")
        activate_script.chmod(0o755)
        print(f"✅ Created activation script: {activate_script}")
    
    print("\n" + "=" * 50)
    if requirements_met:
        print("🎉 Setup completed successfully!")
    else:
        print("⚠️  Setup completed with warnings")
    
    print("\n📋 Next Steps:")
    
    if venv_path and venv_path.exists():
        print("1. Activate environment:")
        print(f"   source {venv_path}/bin/activate  # Linux/macOS")
        print(f"   {venv_path}\\Scripts\\activate    # Windows")
        print("2. Start servers:")
        print("   python3 start_servers.py")
    else:
        print("1. Start servers:")
        print("   python3 start_servers.py")
    
    print("\n🌐 Access Points:")
    print("   Dashboard: http://localhost:5000")
    print("   Form: campus/recruitment-form.html")
    
    print("\n🔐 Default Login:")
    print("   Email: admin@adventz.com")
    print("   Password: 12345")
    
    if not pandas_success:
        print("\n⚠️  Pandas installation failed - some analytics may be limited")
        print("💡 The system will still work with basic functionality")
    
    print("\n" + "=" * 50)
    
    return requirements_met

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)