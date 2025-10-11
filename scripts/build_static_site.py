#!/usr/bin/env python3
"""
Build script for Princeton Academic Events static site.
This script:
1. Runs all scrapers to get fresh data
2. Aggregates all events into static JSON files
3. Builds the Next.js static site
4. Optionally deploys to hosting platform
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def run_command(command: str, cwd: str = None, description: str = None) -> bool:
    """Run a shell command and return success status"""
    if description:
        print(f"\n🔄 {description}")
        print(f"   Command: {command}")
        print("-" * 50)
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.stdout:
            print(result.stdout)
        
        if description:
            print(f"✅ {description} - SUCCESS")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ {description or 'Command'} - FAILED")
        print(f"   Error: {e}")
        if e.stdout:
            print(f"   stdout: {e.stdout}")
        if e.stderr:
            print(f"   stderr: {e.stderr}")
        return False

def run_scrapers() -> bool:
    """Run all department scrapers to get fresh event data"""
    print("🕷️  RUNNING ALL SCRAPERS")
    print("=" * 50)
    
    scrapers_dir = "scrapers"
    
    # Test the universal Drupal scraper on a few key departments
    test_departments = [
        "sociology", "african_studies", "cbe", "orfe", "ece", 
        "history", "anthropology", "slavic_languages", "french_italian"
    ]
    
    success_count = 0
    total_count = len(test_departments)
    
    for dept in test_departments:
        print(f"\n📊 Scraping {dept}...")
        success = run_command(
            f"python universal_drupal_cloudscraper.py {dept}",
            cwd=scrapers_dir,
            description=f"Scraping {dept} events"
        )
        if success:
            success_count += 1
        time.sleep(2)  # Be respectful to servers
    
    print(f"\n📊 SCRAPER SUMMARY")
    print(f"   Successful: {success_count}/{total_count}")
    print(f"   Success rate: {(success_count/total_count)*100:.1f}%")
    
    return success_count > 0

def aggregate_data() -> bool:
    """Aggregate all scraped data into static JSON files"""
    return run_command(
        "python aggregate_events.py",
        cwd="scripts",
        description="Aggregating all events into static data files"
    )

def build_frontend() -> bool:
    """Build the Next.js static site"""
    print("\n🏗️  BUILDING FRONTEND")
    print("=" * 50)
    
    # Install dependencies if needed
    if not os.path.exists("frontend/node_modules"):
        print("📦 Installing frontend dependencies...")
        if not run_command("npm install", cwd="frontend", description="Installing dependencies"):
            return False
    
    # Build the static site
    return run_command(
        "npm run build",
        cwd="frontend",
        description="Building Next.js static site"
    )

def deploy_site(deploy_target: str = None) -> bool:
    """Deploy the built site (placeholder for now)"""
    if not deploy_target:
        print("📋 Deployment skipped - no target specified")
        return True
    
    print(f"\n🚀 DEPLOYING TO {deploy_target.upper()}")
    print("=" * 50)
    
    # This would be customized based on deployment target
    # For now, just copy the built files to a deployment directory
    deploy_dir = f"deploy/{deploy_target}"
    os.makedirs(deploy_dir, exist_ok=True)
    
    return run_command(
        f"cp -r frontend/out/* {deploy_dir}/",
        description=f"Copying built files to {deploy_dir}"
    )

def main():
    """Main build process"""
    print("🚀 PRINCETON ACADEMIC EVENTS - STATIC SITE BUILDER")
    print("=" * 60)
    print("This script will:")
    print("1. Run all department scrapers")
    print("2. Aggregate events into static JSON files")
    print("3. Build the Next.js static site")
    print("4. Optionally deploy to hosting platform")
    print("=" * 60)
    
    start_time = time.time()
    
    # Step 1: Run scrapers
    if not run_scrapers():
        print("❌ Scraper step failed - aborting build")
        sys.exit(1)
    
    # Step 2: Aggregate data
    if not aggregate_data():
        print("❌ Data aggregation failed - aborting build")
        sys.exit(1)
    
    # Step 3: Build frontend
    if not build_frontend():
        print("❌ Frontend build failed - aborting build")
        sys.exit(1)
    
    # Step 4: Deploy (optional)
    deploy_target = os.getenv('DEPLOY_TARGET')
    if deploy_target:
        if not deploy_site(deploy_target):
            print("❌ Deployment failed")
            sys.exit(1)
    
    end_time = time.time()
    build_time = end_time - start_time
    
    print(f"\n🎉 BUILD COMPLETE!")
    print(f"   ⏱️  Total build time: {build_time:.1f} seconds")
    print(f"   📁 Static site built in: frontend/out/")
    print(f"   🌐 Ready for deployment!")
    
    if deploy_target:
        print(f"   🚀 Deployed to: {deploy_target}")
    else:
        print(f"   💡 To deploy, set DEPLOY_TARGET environment variable")

if __name__ == "__main__":
    main()
