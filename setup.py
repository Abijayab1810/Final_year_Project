"""
First-Time Setup Script
Initializes databases and creates test users
Run this ONCE before first use
"""

import os
import sys
from datetime import datetime

def setup_platform():
    """Initialize all databases and create test accounts"""
    
    print("\n" + "=" * 70)
    print("🚀 LUGGAGE DETECTION PLATFORM - FIRST TIME SETUP")
    print("=" * 70 + "\n")
    
    # Step 1: Initialize Users Database
    print("📋 Step 1: Initializing User Database...")
    try:
        from users_db import init_users_database
        init_users_database()
        print("   ✅ Users database initialized\n")
    except Exception as e:
        print(f"   ❌ Error initializing users database: {e}\n")
        return False
    
    # Step 2: Initialize Forensic Database
    print("📋 Step 2: Initializing Forensic Database...")
    try:
        from forensic_db import init_forensic_database
        init_forensic_database()
        print("   ✅ Forensic database initialized\n")
    except Exception as e:
        print(f"   ❌ Error initializing forensic database: {e}\n")
        return False
    
    # Step 3: Initialize Cameras Database
    print("📋 Step 3: Initializing Cameras Database...")
    try:
        from cameras_db import init_cameras_database
        init_cameras_database()
        print("   ✅ Cameras database initialized\n")
    except Exception as e:
        print(f"   ❌ Error initializing cameras database: {e}\n")
        return False
    
    # Step 4: Load/Create Configuration
    print("📋 Step 4: Initializing Configuration...")
    try:
        from config import load_config, print_config
        config = load_config()
        print("   ✅ Configuration loaded/created")
        print("\n   Current Detection Settings:")
        print(f"     - Min abandonment time: {config['detection']['min_abandonment_time']}s")
        print(f"     - Confidence threshold: {config['detection']['confidence_threshold']}")
        print(f"     - Frame size: {config['detection']['frame_width']}x{config['detection']['frame_height']}\n")
    except Exception as e:
        print(f"   ⚠️  Error loading configuration: {e}\n")
    
    # Step 5: Create Test Users
    print("📋 Step 5: Creating Test Users...")
    try:
        from users_db import register_user, authenticate_user
        
        test_users = [
            ("demo", "demo@example.com", "Demo123", "Demo User"),
            ("testuser", "test@example.com", "Test123", "Test User"),
            ("operator", "operator@airport.com", "Operator123", "Airport Operator"),
        ]
        
        created_count = 0
        skipped_count = 0
        
        for username, email, password, full_name in test_users:
            result = register_user(username, email, password, full_name)
            if result["status"] == "success":
                print(f"   ✅ Created: {username}")
                created_count += 1
            else:
                print(f"   ℹ️  {username}: {result['message']}")
                skipped_count += 1
        
        print(f"\n   Created: {created_count}, Skipped: {skipped_count}\n")
        
    except Exception as e:
        print(f"   ❌ Error creating test users: {e}\n")
        return False
    
    # Step 6: Create EVIDENCE folder if needed
    print("📋 Step 6: Setting up Evidence Folder...")
    try:
        from forensic_db import EVIDENCE_FOLDER
        if not os.path.exists(EVIDENCE_FOLDER):
            os.makedirs(EVIDENCE_FOLDER)
            print(f"   ✅ Created evidence folder: {EVIDENCE_FOLDER}\n")
        else:
            print(f"   ℹ️  Evidence folder already exists: {EVIDENCE_FOLDER}\n")
    except Exception as e:
        print(f"   ⚠️  Error setting up evidence folder: {e}\n")
    
    # Final Summary
    print("=" * 70)
    print("✅ SETUP COMPLETE!")
    print("=" * 70)
    
    print("\n📝 TEST ACCOUNTS CREATED:")
    print("\n   Account 1:")
    print("     Username: demo")
    print("     Password: Demo123")
    print("     Email: demo@example.com")
    
    print("\n   Account 2:")
    print("     Username: testuser")
    print("     Password: Test123")
    print("     Email: test@example.com")
    
    print("\n   Account 3:")
    print("     Username: operator")
    print("     Password: Operator123")
    print("     Email: operator@airport.com")
    
    print("\n🚀 NEXT STEPS:")
    print("\n   1. Run the platform:")
    print("      Windows: START_PLATFORM.bat")
    print("      Linux/Mac: bash start_platform.sh")
    print("\n   2. Access dashboard:")
    print("      http://localhost:8501")
    print("\n   3. Login with any account above")
    print("\n   4. Add a camera via Camera Management")
    print("\n   5. Start detection in Live Monitoring")
    
    print("\n📖 DOCUMENTATION:")
    print("   - QUICK_START.md - Complete setup guide")
    print("   - TUNING_GUIDE.md - Real-time configuration")
    print("   - CAMERA_MANAGEMENT_GUIDE.md - Camera setup")
    
    print("\n📊 CONFIGURATION FILE:")
    print(f"   File: detection_config.json")
    print("   Edit to adjust detection in real-time (no restart needed!)")
    
    print("\n" + "=" * 70 + "\n")
    
    return True


if __name__ == "__main__":
    try:
        success = setup_platform()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error during setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
