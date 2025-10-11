#!/usr/bin/env python3
import requests
import json
from datetime import datetime

def check_api_status():
    """Check the comprehensive API status and show how it looks"""
    
    base_url = "https://princeton-academic-events.spergel-joshua.workers.dev"
    
    print("🌐 PRINCETON ACADEMIC EVENTS API STATUS")
    print("=" * 80)
    print(f"🔗 Base URL: {base_url}")
    print(f"⏰ Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Get all events
    print("📊 TEST 1: Getting all events...")
    try:
        response = requests.get(f"{base_url}/api/events")
        if response.status_code == 200:
            data = response.json()
            events = data.get('events', [])
            print(f"✅ SUCCESS! API returned {len(events)} events")
            
            # Count by department
            dept_counts = {}
            for event in events:
                dept = event.get('department', 'Unknown')
                dept_counts[dept] = dept_counts.get(dept, 0) + 1
            
            print(f"\n📈 EVENTS BY DEPARTMENT (Top 20):")
            print("-" * 60)
            sorted_depts = sorted(dept_counts.items(), key=lambda x: x[1], reverse=True)
            for i, (dept, count) in enumerate(sorted_depts[:20], 1):
                print(f"{i:2d}. {dept:<45} {count:>3} events")
            
            # Show sample events
            print(f"\n🎯 SAMPLE EVENTS (First 10):")
            print("-" * 80)
            for i, event in enumerate(events[:10], 1):
                title = event.get('title', 'No title')[:60]
                dept = event.get('department', 'Unknown')
                date = event.get('start_date', 'No date')
                time = event.get('time', 'No time')
                location = event.get('location', 'No location')
                
                print(f"{i:2d}. {title}")
                print(f"    🏢 {dept}")
                print(f"    📅 {date} | ⏰ {time}")
                print(f"    📍 {location}")
                print()
                
        else:
            print(f"❌ FAILED: {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 2: Get departments
    print("\n🏢 TEST 2: Getting departments...")
    try:
        response = requests.get(f"{base_url}/api/departments")
        if response.status_code == 200:
            data = response.json()
            departments = data.get('departments', [])
            print(f"✅ SUCCESS! Found {len(departments)} departments")
            
            if departments:
                print("📋 Departments:")
                for i, dept in enumerate(departments[:15], 1):
                    print(f"  {i:2d}. {dept}")
                if len(departments) > 15:
                    print(f"  ... and {len(departments) - 15} more")
        else:
            print(f"❌ FAILED: {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 3: Search functionality
    print("\n🔍 TEST 3: Testing search functionality...")
    search_queries = ['music', 'lecture', 'seminar', 'conference']
    
    for query in search_queries:
        try:
            response = requests.get(f"{base_url}/api/search?q={query}")
            if response.status_code == 200:
                data = response.json()
                search_results = data.get('events', [])
                print(f"✅ Search '{query}': {len(search_results)} results")
            else:
                print(f"❌ Search '{query}': Failed ({response.status_code})")
        except Exception as e:
            print(f"❌ Search '{query}' ERROR: {e}")
    
    # Test 4: RSS feed
    print("\n📡 TEST 4: Testing RSS feed...")
    try:
        response = requests.get(f"{base_url}/api/rss")
        if response.status_code == 200:
            print(f"✅ RSS feed working! Content length: {len(response.text)} characters")
            if '<?xml' in response.text:
                print("   📋 Valid XML format detected")
        else:
            print(f"❌ RSS feed failed: {response.status_code}")
    except Exception as e:
        print(f"❌ RSS feed ERROR: {e}")
    
    # Test 5: API health check
    print("\n💚 TEST 5: API health check...")
    try:
        response = requests.get(f"{base_url}/api/events")
        if response.status_code == 200:
            print("✅ API is healthy and responding")
            print(f"   📊 Response time: {response.elapsed.total_seconds():.3f} seconds")
            print(f"   📏 Response size: {len(response.content)} bytes")
        else:
            print(f"❌ API health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API health check ERROR: {e}")
    
    print("\n" + "=" * 80)
    print("🎉 API STATUS CHECK COMPLETE!")

if __name__ == "__main__":
    check_api_status()
