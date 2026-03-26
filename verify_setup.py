#!/usr/bin/env python3
"""
System Verification Script for Business Idea Validator
Checks all dependencies and configurations before running the application
"""

import sys
import os
import json
from pathlib import Path

def check_python_version():
    """Verify Python 3.8+"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False

def check_required_files():
    """Verify all required files exist"""
    print("\n🔍 Checking required files...")
    required_files = {
        'main.py': 'FastAPI application',
        'agent.py': 'Gemini AI agent',
        'models.py': 'Pydantic schemas',
        'redis_client.py': 'Redis manager',
        'requirements.txt': 'Dependencies',
        '.env': 'Environment configuration',
        'UI_Pages/index.html': 'Frontend HTML',
        'UI_Pages/index.css': 'Frontend CSS',
        'UI_Pages/index.js': 'Frontend JavaScript',
    }
    
    all_exist = True
    for filename, description in required_files.items():
        path = Path(filename)
        if path.exists():
            size = path.stat().st_size
            print(f"✅ {filename:30} ({description:25}) - {size:8} bytes")
        else:
            print(f"❌ {filename:30} ({description:25}) - MISSING")
            all_exist = False
    
    return all_exist

def check_dependencies():
    """Check if required packages are installed"""
    print("\n🔍 Checking Python dependencies...")
    
    required_packages = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn ASGI server',
        'pydantic': 'Data validation',
        'google.generativeai': 'Google Gemini API',
        'redis': 'Redis client',
        'dotenv': 'Environment variables',
    }
    
    all_installed = True
    for module_name, description in required_packages.items():
        try:
            __import__(module_name)
            print(f"✅ {module_name:25} ({description})")
        except ImportError:
            print(f"❌ {module_name:25} ({description}) - NOT INSTALLED")
            all_installed = False
    
    return all_installed

def check_env_file():
    """Verify .env configuration"""
    print("\n🔍 Checking environment configuration...")
    
    env_path = Path('.env')
    if not env_path.exists():
        print("❌ .env file not found")
        print("   Create .env with: API_KEY=your_gemini_api_key")
        return False
    
    with open(env_path, 'r') as f:
        content = f.read()
        if 'API_KEY' in content and not content.strip().endswith('API_KEY='):
            # Check if it's not empty
            lines = content.split('\n')
            for line in lines:
                if line.startswith('API_KEY=') and len(line.split('=')[1].strip()) > 0:
                    print(f"✅ API_KEY configured")
                    return True
    
    print("❌ API_KEY not properly configured in .env")
    return False

def check_redis_connection():
    """Test Redis connection"""
    print("\n🔍 Checking Redis connection...")
    
    try:
        import redis
        try:
            r = redis.from_url("redis://localhost:6379/0", decode_responses=True)
            info = r.ping()
            if info:
                print("✅ Redis connection successful")
                return True
        except Exception as e:
            print(f"⚠️  Redis not running locally (optional)")
            print(f"   To enable conversation memory, start Redis:")
            print(f"   - Docker: docker run -d -p 6379:6379 redis:latest")
            print(f"   - macOS: brew install redis && redis-server")
            print(f"   - Linux: sudo apt-get install redis-server && redis-server")
            return True  # Not required, but recommended
    except ImportError:
        print("⚠️  Redis client not installed (optional)")
        return True

def check_api_key_validity():
    """Quick check on API key format"""
    print("\n🔍 Checking API key format...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('API_KEY')
    
    if not api_key:
        print("❌ API_KEY environment variable not set")
        return False
    
    if api_key.startswith('AIza') and len(api_key) > 20:
        print(f"✅ API_KEY format looks valid")
        return True
    else:
        print(f"⚠️  API_KEY format may be incorrect")
        print(f"   Key should start with 'AIza' and be 39+ characters")
        return True  # Not blocking, will fail at runtime if wrong

def check_file_permissions():
    """Verify write permissions for logs"""
    print("\n🔍 Checking file permissions...")
    
    try:
        # Try to create a test file
        test_file = Path('.verify_test')
        test_file.write_text('test')
        test_file.unlink()
        print("✅ Write permissions OK")
        return True
    except Exception as e:
        print(f"❌ Cannot write to directory: {e}")
        return False

def main():
    """Run all checks"""
    print("=" * 70)
    print("Business Idea Validator - System Verification")
    print("=" * 70)
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Files", check_required_files),
        ("Dependencies", check_dependencies),
        ("Environment Config", check_env_file),
        ("File Permissions", check_file_permissions),
        ("API Key Format", check_api_key_validity),
        ("Redis Connection", check_redis_connection),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error during {name} check: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "⚠️  WARN"
        print(f"{status:10} {name}")
    
    print("\n" + "=" * 70)
    
    if passed == total:
        print(f"✅ All checks passed! ({passed}/{total})")
        print("\n✅ You're ready to run: python main.py")
        print("   Then open: http://127.0.0.1:8000")
        return 0
    else:
        print(f"⚠️  {passed}/{total} checks passed")
        print("\n💡 Some issues found, but app may still run.")
        print("   Review warnings above and fix critical errors.")
        print("\n   You can still try: python main.py")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
