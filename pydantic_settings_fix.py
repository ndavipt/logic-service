"""
This is a temporary fix for a known issue with pydantic_settings.
Run this script to fix the import issue before starting the app.
"""

def fix_imports():
    try:
        # Try to import pydantic_settings
        import pydantic_settings
        print("pydantic_settings already installed")
        return True
    except ImportError:
        print("pydantic_settings not found. Installing...")
        
        try:
            import subprocess
            import sys
            
            # Install pydantic_settings
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pydantic-settings"])
            print("pydantic_settings installed successfully")
            return True
        except Exception as e:
            print(f"Error installing pydantic_settings: {e}")
            return False

if __name__ == "__main__":
    fix_imports()