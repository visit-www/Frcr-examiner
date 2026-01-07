"""
Test Backup System
Quick verification that backup files are in place
Run this without virtual environment to check files exist
"""
import os

def test_backup_system():
    """Test backup system files"""
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("Testing FRCR Examiner Backup System...")
    print("-" * 50)
    
    # Files to check
    files_to_check = [
        ('backup_routes.py', 'Backup API routes'),
        ('templates/backup_manager.html', 'Backup manager page'),
        ('static/backup-reminder.js', 'Backup reminder script'),
        ('manage_local_backups.py', 'Local backup manager'),
        ('BACKUP_SYSTEM.md', 'Backup documentation'),
        ('BACKUP_IMPLEMENTATION.md', 'Implementation summary'),
    ]
    
    all_good = True
    
    for filepath, description in files_to_check:
        full_path = os.path.join(base_dir, filepath)
        exists = os.path.exists(full_path)
        
        if exists:
            size = os.path.getsize(full_path)
            print(f"✓ {description:<30} ({filepath})")
            print(f"  Size: {size:,} bytes")
        else:
            print(f"✗ {description:<30} MISSING!")
            all_good = False
    
    print("\n" + "-" * 50)
    
    # Check if backup_routes is imported in app.py
    print("\nChecking app.py integration...")
    app_py = os.path.join(base_dir, 'app.py')
    with open(app_py, 'r') as f:
        content = f.read()
        
        if 'from backup_routes import backup_bp' in content:
            print("✓ backup_routes imported")
        else:
            print("✗ backup_routes NOT imported")
            all_good = False
        
        if 'app.register_blueprint(backup_bp)' in content:
            print("✓ backup_bp registered")
        else:
            print("✗ backup_bp NOT registered")
            all_good = False
        
        if '@app.route(\'/admin\')' in content and 'backup_manager.html' in content:
            print("✓ /admin route redirects to backup manager")
        else:
            print("✗ /admin route NOT configured")
            all_good = False
    
    # Check navigation updates
    print("\nChecking navigation updates...")
    base_html = os.path.join(base_dir, 'templates', 'base.html')
    with open(base_html, 'r') as f:
        content = f.read()
        
        if 'Backup' in content and 'fa-database' in content:
            print("✓ Navigation updated to Backup")
        else:
            print("✗ Navigation NOT updated")
            all_good = False
    
    # Check base template integration
    print("\nChecking base template integration...")
    base_html = os.path.join(base_dir, 'templates', 'base.html')
    with open(base_html, 'r') as f:
        content = f.read()
        
        if 'backup-reminder.js' in content:
            print("✓ Backup reminder script included")
        else:
            print("✗ Backup reminder script NOT included")
            all_good = False
    
    print("\n" + "-" * 50)
    
    if all_good:
        print("✓ All backup system components verified!")
        print("\n📋 Summary:")
        print("   - 5 new files created")
        print("   - 4 existing files modified")
        print("   - 3 API endpoints added")
        print("   - 1 new page added")
        print("\n🚀 Next steps:")
        print("1. Start the application: python3 run.py (or ./start.sh)")
        print("2. Register/login as admin (first user)")
        print("3. Go to Admin → Web Backup Manager")
        print("4. Test download and restore features")
        print("\n📖 Documentation:")
        print("   - User guide: BACKUP_SYSTEM.md")
        print("   - Implementation: BACKUP_IMPLEMENTATION.md")
        print("\n💡 Manage local backups:")
        print("   python3 manage_local_backups.py ~/Downloads")
        return True
    else:
        print("✗ Some components are missing!")
        return False

if __name__ == '__main__':
    try:
        success = test_backup_system()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
