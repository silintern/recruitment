#!/usr/bin/env python3
"""
Startup script to run both the dashboard and form backends simultaneously
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def start_server(script_path, server_name, port):
    """Start a Flask server in a subprocess"""
    try:
        print(f"Starting {server_name} on port {port}...")
        env = os.environ.copy()
        env['PORT'] = str(port)
        
        process = subprocess.Popen([
            sys.executable, script_path
        ], env=env, cwd=os.path.dirname(script_path))
        
        print(f"✅ {server_name} started with PID {process.pid}")
        return process
    except Exception as e:
        print(f"❌ Failed to start {server_name}: {e}")
        return None

def main():
    """Main function to start both servers"""
    print("🚀 Starting Recruitment System Servers...")
    print("=" * 50)
    
    # Get the current directory
    current_dir = Path(__file__).parent
    
    # Define server paths
    dashboard_path = current_dir / "dashboard" / "app.py"
    form_backend_path = current_dir / "form-backend" / "app.py"
    
    # Check if files exist
    if not dashboard_path.exists():
        print(f"❌ Dashboard app not found at {dashboard_path}")
        return
    
    if not form_backend_path.exists():
        print(f"❌ Form backend app not found at {form_backend_path}")
        return
    
    processes = []
    
    try:
        # Start dashboard server (port 5000)
        dashboard_process = start_server(str(dashboard_path), "Dashboard Server", 5000)
        if dashboard_process:
            processes.append(("Dashboard", dashboard_process))
        
        # Wait a moment before starting the next server
        time.sleep(2)
        
        # Start form backend server (port 5001)
        form_process = start_server(str(form_backend_path), "Form Backend", 5001)
        if form_process:
            processes.append(("Form Backend", form_process))
        
        if not processes:
            print("❌ No servers started successfully")
            return
        
        print("\n" + "=" * 50)
        print("🎉 All servers started successfully!")
        print("\n📊 Dashboard: http://localhost:5000")
        print("📝 Form Backend: http://localhost:5001")
        print("\n💡 Access the recruitment form at:")
        print(f"   file://{current_dir}/campus/recruitment-form.html")
        print("\n" + "=" * 50)
        print("Press Ctrl+C to stop all servers...")
        
        # Wait for user interrupt
        try:
            while True:
                # Check if any process has died
                for name, process in processes:
                    if process.poll() is not None:
                        print(f"⚠️  {name} has stopped unexpectedly")
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Shutting down servers...")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        # Clean up processes
        for name, process in processes:
            try:
                print(f"Stopping {name}...")
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} stopped")
            except subprocess.TimeoutExpired:
                print(f"⚠️  Force killing {name}...")
                process.kill()
            except Exception as e:
                print(f"❌ Error stopping {name}: {e}")
        
        print("🏁 All servers stopped")

if __name__ == "__main__":
    main()