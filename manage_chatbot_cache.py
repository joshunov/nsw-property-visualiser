#!/usr/bin/env python3
"""
Chatbot Cache Management Script
Build, refresh, and clear the chatbot data cache for faster loading
"""

import sys
import os
import argparse
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from chatbot.property_chatbot import PropertyChatbot

def build_cache():
    """Build the initial cache"""
    print("🏗️ Building chatbot cache...")
    start_time = time.time()
    
    try:
        # Initialize chatbot with cache disabled to force fresh load
        chatbot = PropertyChatbot(use_cache=False)
        
        # Save to cache
        chatbot._save_cache()
        
        elapsed_time = time.time() - start_time
        print(f"✅ Cache built successfully in {elapsed_time:.2f} seconds")
        print(f"📊 Historical records: {len(chatbot.historical_df):,}")
        print(f"📊 Current listings: {len(chatbot.current_df):,}")
        
    except Exception as e:
        print(f"❌ Failed to build cache: {e}")
        return False
    
    return True

def refresh_cache():
    """Refresh the existing cache"""
    print("🔄 Refreshing chatbot cache...")
    start_time = time.time()
    
    try:
        # Initialize chatbot
        chatbot = PropertyChatbot(use_cache=False)
        
        # Refresh cache
        chatbot.refresh_cache()
        
        elapsed_time = time.time() - start_time
        print(f"✅ Cache refreshed successfully in {elapsed_time:.2f} seconds")
        print(f"📊 Historical records: {len(chatbot.historical_df):,}")
        print(f"📊 Current listings: {len(chatbot.current_df):,}")
        
    except Exception as e:
        print(f"❌ Failed to refresh cache: {e}")
        return False
    
    return True

def clear_cache():
    """Clear the cache files"""
    print("🗑️ Clearing chatbot cache...")
    
    try:
        # Get cache directory
        cache_dir = os.path.join(os.path.dirname(__file__), 'src', 'cache')
        historical_cache = os.path.join(cache_dir, "historical_data_cache.pkl")
        current_cache = os.path.join(cache_dir, "current_data_cache.pkl")
        
        # Remove cache files
        files_removed = 0
        if os.path.exists(historical_cache):
            os.remove(historical_cache)
            files_removed += 1
            print("🗑️ Removed historical data cache")
        
        if os.path.exists(current_cache):
            os.remove(current_cache)
            files_removed += 1
            print("🗑️ Removed current data cache")
        
        if files_removed == 0:
            print("ℹ️ No cache files found to remove")
        else:
            print(f"✅ Cache cleared successfully ({files_removed} files removed)")
        
    except Exception as e:
        print(f"❌ Failed to clear cache: {e}")
        return False
    
    return True

def check_cache():
    """Check cache status"""
    print("🔍 Checking cache status...")
    
    try:
        # Get cache directory
        cache_dir = os.path.join(os.path.dirname(__file__), 'src', 'cache')
        historical_cache = os.path.join(cache_dir, "historical_data_cache.pkl")
        current_cache = os.path.join(cache_dir, "current_data_cache.pkl")
        
        if not os.path.exists(historical_cache) or not os.path.exists(current_cache):
            print("❌ Cache not found")
            return False
        
        # Check cache age
        cache_time = os.path.getmtime(historical_cache)
        current_time = time.time()
        cache_age_hours = (current_time - cache_time) / 3600
        
        print(f"✅ Cache found")
        print(f"📅 Cache age: {cache_age_hours:.1f} hours")
        print(f"📁 Cache location: {cache_dir}")
        
        # Check if cache is still valid (less than 24 hours old)
        if cache_age_hours < 24:
            print("✅ Cache is valid (less than 24 hours old)")
        else:
            print("⚠️ Cache is old (more than 24 hours old)")
        
        # Try to load cache to check data
        try:
            chatbot = PropertyChatbot(use_cache=True)
            print(f"📊 Historical records: {len(chatbot.historical_df):,}")
            print(f"📊 Current listings: {len(chatbot.current_df):,}")
        except Exception as e:
            print(f"❌ Cache data is corrupted: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Failed to check cache: {e}")
        return False
    
    return True

def test_performance():
    """Test cache performance"""
    print("⚡ Testing cache performance...")
    
    # Test without cache
    print("\n🔄 Testing without cache (fresh load)...")
    start_time = time.time()
    try:
        chatbot_no_cache = PropertyChatbot(use_cache=False)
        no_cache_time = time.time() - start_time
        print(f"⏱️ Fresh load time: {no_cache_time:.2f} seconds")
    except Exception as e:
        print(f"❌ Fresh load failed: {e}")
        return False
    
    # Test with cache
    print("\n⚡ Testing with cache...")
    start_time = time.time()
    try:
        chatbot_with_cache = PropertyChatbot(use_cache=True)
        with_cache_time = time.time() - start_time
        print(f"⏱️ Cache load time: {with_cache_time:.2f} seconds")
    except Exception as e:
        print(f"❌ Cache load failed: {e}")
        return False
    
    # Calculate improvement
    if no_cache_time > 0:
        improvement = ((no_cache_time - with_cache_time) / no_cache_time) * 100
        print(f"\n📈 Performance improvement: {improvement:.1f}% faster with cache")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Manage chatbot cache for faster loading')
    parser.add_argument('action', choices=['build', 'refresh', 'clear', 'check', 'test'], 
                       help='Action to perform')
    
    args = parser.parse_args()
    
    print("🏠 Eastern Suburbs Property AI Chatbot - Cache Manager")
    print("=" * 60)
    
    if args.action == 'build':
        success = build_cache()
    elif args.action == 'refresh':
        success = refresh_cache()
    elif args.action == 'clear':
        success = clear_cache()
    elif args.action == 'check':
        success = check_cache()
    elif args.action == 'test':
        success = test_performance()
    
    if success:
        print("\n✅ Operation completed successfully")
    else:
        print("\n❌ Operation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
