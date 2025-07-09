#!/usr/bin/env python3
"""
Session Cleanup Script
This script removes old Flask session files to keep the session directories clean.
"""

import os
import time
from pathlib import Path
import argparse

def cleanup_session_directory(session_dir, max_age_days=7, dry_run=False):
    """
    Clean up old session files in a directory.
    
    Args:
        session_dir (Path): Directory containing session files
        max_age_days (int): Maximum age in days for session files
        dry_run (bool): If True, only show what would be deleted
    
    Returns:
        tuple: (files_deleted, total_size_freed)
    """
    if not session_dir.exists():
        print(f"Session directory {session_dir} does not exist")
        return 0, 0
    
    current_time = time.time()
    max_age_seconds = max_age_days * 24 * 60 * 60
    
    files_deleted = 0
    total_size_freed = 0
    
    print(f"Cleaning up {session_dir}...")
    print(f"Removing files older than {max_age_days} days")
    
    for file_path in session_dir.iterdir():
        if file_path.is_file():
            # Get file modification time
            file_mtime = file_path.stat().st_mtime
            file_age = current_time - file_mtime
            
            if file_age > max_age_seconds:
                file_size = file_path.stat().st_size
                
                if dry_run:
                    print(f"  Would delete: {file_path.name} ({file_size} bytes, {file_age/86400:.1f} days old)")
                else:
                    try:
                        file_path.unlink()
                        print(f"  Deleted: {file_path.name} ({file_size} bytes, {file_age/86400:.1f} days old)")
                        files_deleted += 1
                        total_size_freed += file_size
                    except OSError as e:
                        print(f"  Error deleting {file_path.name}: {e}")
            else:
                print(f"  Keeping: {file_path.name} ({file_age/86400:.1f} days old)")
    
    return files_deleted, total_size_freed

def main():
    """Main cleanup function"""
    parser = argparse.ArgumentParser(description='Clean up old Flask session files')
    parser.add_argument('--max-age', type=int, default=7, 
                       help='Maximum age in days for session files (default: 7)')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be deleted without actually deleting')
    
    args = parser.parse_args()
    
    # Define session directories
    session_dirs = [
        Path('flask_session'),
        Path('tests/flask_session'),
    ]
    
    print("=" * 50)
    print("MyFoodBudget Session Cleanup")
    print("=" * 50)
    
    if args.dry_run:
        print("DRY RUN MODE - No files will be deleted")
    
    total_files_deleted = 0
    total_size_freed = 0
    
    for session_dir in session_dirs:
        files_deleted, size_freed = cleanup_session_directory(
            session_dir, args.max_age, args.dry_run
        )
        total_files_deleted += files_deleted
        total_size_freed += size_freed
        print()
    
    print("=" * 50)
    print("CLEANUP SUMMARY")
    print("=" * 50)
    
    if args.dry_run:
        print(f"Would delete {total_files_deleted} files")
        print(f"Would free {total_size_freed} bytes ({total_size_freed/1024:.1f} KB)")
    else:
        print(f"Deleted {total_files_deleted} files")
        print(f"Freed {total_size_freed} bytes ({total_size_freed/1024:.1f} KB)")
    
    print("\nRecommended usage:")
    print("  python cleanup_sessions.py --dry-run    # Preview what would be deleted")
    print("  python cleanup_sessions.py --max-age 3  # Delete files older than 3 days")
    print("  python cleanup_sessions.py              # Delete files older than 7 days")

if __name__ == "__main__":
    main()