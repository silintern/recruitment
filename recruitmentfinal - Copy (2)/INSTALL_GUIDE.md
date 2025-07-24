# Installation Guide - Recruitment Management System

## 🚨 Common Installation Issues & Solutions

### Issue 1: Pandas Installation Fails

**Error Message:**
```
ERROR: Failed building wheel for pandas
ERROR: Failed to build installable wheels for some pyproject.toml based projects (pandas)
```

**Solutions (try in order):**

#### Solution 1: Use Pre-compiled Binaries
```bash
pip install pandas --only-binary=all
```

#### Solution 2: Install Specific Version
```bash
pip install "pandas<2.0.0"
```

#### Solution 3: Use Conda (if available)
```bash
conda install pandas
```

#### Solution 4: Install Build Dependencies
**On Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3-dev build-essential
pip install pandas
```

**On CentOS/RHEL:**
```bash
sudo yum install python3-devel gcc gcc-c++
pip install pandas
```

**On macOS:**
```bash
xcode-select --install
pip install pandas
```

#### Solution 5: Use Alternative Package Manager
```bash
# Using pipenv
pipenv install pandas

# Using poetry
poetry add pandas
```

### Issue 2: System Works Without Pandas

✅ **Good News!** The system is designed to work without pandas. You'll see this message:
```
WARNING: Pandas not available. Some analytics features will be limited.
```

**What still works:**
- ✅ Form submissions
- ✅ Dashboard login
- ✅ Basic KPIs
- ✅ Form configuration
- ✅ User management
- ✅ Status updates

**What may be limited:**
- ⚠️ Advanced filtering
- ⚠️ Date range filtering
- ⚠️ Complex analytics

## 🔧 Quick Setup Options

### Option 1: Automated Setup (Recommended)
```bash
cd "recruitmentfinal - Copy (2)"
python3 setup.py
```

### Option 2: Manual Installation
```bash
# Install basic requirements
pip install Flask Flask-CORS Werkzeug requests

# Try pandas installation
pip install pandas --only-binary=all

# Optional: Excel support
pip install openpyxl

# Start the system
python3 start_servers.py
```

### Option 3: Minimal Installation (No Pandas)
```bash
# Install only essential packages
pip install Flask Flask-CORS Werkzeug requests

# Start the system (will work without pandas)
python3 start_servers.py
```

## 🐍 Python Version Requirements

- **Minimum:** Python 3.7+
- **Recommended:** Python 3.8+ or Python 3.9+
- **Latest:** Python 3.11+ (fastest)

**Check your Python version:**
```bash
python3 --version
```

## 🌐 Virtual Environment Setup (Recommended)

### Using venv:
```bash
# Create virtual environment
python3 -m venv recruitment_env

# Activate (Linux/macOS)
source recruitment_env/bin/activate

# Activate (Windows)
recruitment_env\Scripts\activate

# Install packages
pip install -r dashboard/requirements.txt
pip install -r form-backend/requirements.txt
```

### Using conda:
```bash
# Create environment
conda create -n recruitment python=3.9

# Activate
conda activate recruitment

# Install packages
conda install flask pandas requests
pip install Flask-CORS
```

## 🔍 Troubleshooting

### Check System Resources
```bash
# Check available disk space
df -h

# Check memory
free -h

# Check Python path
which python3
```

### Test Installation
```bash
cd "recruitmentfinal - Copy (2)"
python3 -c "
import flask
import sqlite3
print('✅ Basic requirements met')
try:
    import pandas
    print('✅ Pandas available')
except ImportError:
    print('⚠️  Pandas not available (system will still work)')
"
```

### Clean Installation
```bash
# Clear pip cache
pip cache purge

# Upgrade pip
pip install --upgrade pip

# Reinstall everything
pip uninstall flask pandas -y
pip install flask pandas --only-binary=all
```

## 🚀 Platform-Specific Instructions

### Ubuntu/Debian
```bash
# Update system
sudo apt update

# Install Python and pip
sudo apt install python3 python3-pip python3-venv

# Install build tools
sudo apt install build-essential python3-dev

# Install the system
cd "recruitmentfinal - Copy (2)"
python3 setup.py
```

### CentOS/RHEL
```bash
# Install Python
sudo yum install python3 python3-pip

# Install development tools
sudo yum groupinstall "Development Tools"
sudo yum install python3-devel

# Install the system
cd "recruitmentfinal - Copy (2)"
python3 setup.py
```

### macOS
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python

# Install the system
cd "recruitmentfinal - Copy (2)"
python3 setup.py
```

### Windows
```bash
# Download Python from python.org
# Install with "Add to PATH" option checked

# Open Command Prompt or PowerShell
cd "recruitmentfinal - Copy (2)"
python setup.py
```

## 📊 Performance Optimization

### For Better Performance:
```bash
# Use faster JSON library
pip install ujson

# Use faster WSGI server
pip install gunicorn

# Start with gunicorn (Linux/macOS)
gunicorn -w 4 -b 0.0.0.0:5000 dashboard.app:app
```

## 🆘 Still Having Issues?

### Check Logs:
1. Look for error messages in terminal
2. Check Python version compatibility
3. Verify disk space availability
4. Ensure network connectivity

### Alternative Approaches:
1. **Docker Installation** (if available):
   ```bash
   # Create Dockerfile with dependencies
   # Run in container
   ```

2. **Cloud Installation**:
   - Deploy to Heroku, AWS, or Google Cloud
   - Use managed Python environments

3. **Simplified Version**:
   - Run without pandas
   - Use basic functionality only
   - Add features gradually

## 📞 Support

If you continue to have issues:

1. **Check Python Version**: Ensure Python 3.7+
2. **Try Virtual Environment**: Isolate dependencies
3. **Use Minimal Install**: Skip pandas initially
4. **Check System Resources**: Ensure adequate disk/memory
5. **Update System**: Ensure OS and Python are current

The system is designed to be resilient and will work even with missing optional dependencies!