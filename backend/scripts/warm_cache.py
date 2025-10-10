#!/usr/bin/env python3
"""
Cache Warming Script

Pre-loads frequently accessed data into Redis cache.
Usage: python scripts/warm_cache.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import logging
from datetime import datetime, timedelta

from app.services.odoo_cache import OdooCache
from app.integrations.odoo_client_v2 import OdooClientV2

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def print_header(text: str):
    """Print header."""
    print("\n" + "=" * 70)
    print(f"{text:^70}")
    print("=" * 70 + "\n")


def print_success(text: str):
    """Print success message."""
    print(f"✓ {text}")


def print_error(text: str):
    """Print error message."""
    print(f"✗ {text}")


def print_info(text: str):
    """Print info message."""
    print(f"ℹ {text}")


async def warm_doctors_cache():
    """Warm doctors cache."""
    print_info("Warming doctors cache...")
    
    try:
        cache = OdooCache()
        odoo_client = OdooClientV2()
        
        # Get all doctors
        doctors = odoo_client.get_doctors()
        
        if doctors:
            # Cache doctors list
            await cache.set_doctors(doctors)
            print_success(f"Cached {len(doctors)} doctors")
            
            # Cache each doctor individually
            for doctor in doctors:
                doctor_id = doctor.get('id')
                if doctor_id:
                    await cache.set_doctor(doctor_id, doctor)
            
            print_success(f"Cached {len(doctors)} individual doctor records")
        else:
            print_info("No doctors found")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to warm doctors cache: {e}")
        return False


async def warm_available_slots_cache():
    """Warm available slots cache."""
    print_info("Warming available slots cache...")
    
    try:
        cache = OdooCache()
        odoo_client = OdooClientV2()
        
        # Get slots for next 7 days
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=7)
        
        slots = odoo_client.get_available_slots(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        if slots:
            # Cache slots
            cache_key = f"slots_{start_date}_{end_date}"
            await cache.set(cache_key, slots, ttl=300)  # 5 minutes
            print_success(f"Cached {len(slots)} available slots")
        else:
            print_info("No available slots found")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to warm slots cache: {e}")
        return False


async def warm_cache():
    """Warm all caches."""
    print_header("DentaFlow Cache Warming")
    
    print_info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    success_count = 0
    total_count = 0
    
    # Warm doctors cache
    total_count += 1
    if await warm_doctors_cache():
        success_count += 1
    
    print("")
    
    # Warm available slots cache
    total_count += 1
    if await warm_available_slots_cache():
        success_count += 1
    
    print("")
    
    # Summary
    print_header("Cache Warming Summary")
    print(f"Total operations: {total_count}")
    print_success(f"Successful: {success_count}")
    print_error(f"Failed: {total_count - success_count}")
    
    if success_count == total_count:
        print("")
        print_success("All caches warmed successfully!")
        return True
    else:
        print("")
        print_error("Some cache warming operations failed")
        return False


def main():
    """Main function."""
    try:
        result = asyncio.run(warm_cache())
        sys.exit(0 if result else 1)
    except Exception as e:
        print_error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

