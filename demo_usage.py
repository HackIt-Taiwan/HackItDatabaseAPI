#!/usr/bin/env python3
"""
Demo script for HackIt Database Service v1.1.0
Demonstrates enhanced features and usage patterns.
"""

import asyncio
import json
from datetime import datetime, timedelta
from database_client import DatabaseClient, DatabaseClientError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


async def demo_basic_crud():
    """Demonstrate basic CRUD operations."""
    print("\n📝 Basic CRUD Operations Demo")
    print("-" * 40)
    
    async with DatabaseClient("http://localhost:8001", "your-secret-key") as client:
        # Create a new user
        user_data = {
            "user_id": 111222333,
            "guild_id": 444555666,
            "real_name": "Demo User",
            "email": "demo@hackit.tw",
            "bio": "I'm a demo user showcasing the HackIt Database Service!",
            "location": "Taipei, Taiwan",
            "website": "https://hackit.tw",
            "github_username": "hackit-demo",
            "linkedin_url": "https://linkedin.com/in/hackitdemo",
            "tags": ["student", "developer", "hackathon"]
        }
        
        try:
            print("Creating new user...")
            result = await client.create_user(user_data)
            if result["success"]:
                user_id = result["data"]["id"]
                print(f"✅ User created successfully! ID: {user_id}")
                
                # Read the user
                print("\nRetrieving user information...")
                user = await client.get_user_by_id(user_id)
                if user["success"]:
                    print(f"✅ User found: {user['data']['real_name']}")
                    print(f"   Profile completeness: {user['data']['profile_completeness']:.1f}%")
                
                # Update the user
                print("\nUpdating user bio...")
                update_result = await client.update_user(user_id, {
                    "bio": "Updated bio: Now I'm an expert user of HackIt Database Service!"
                })
                if update_result["success"]:
                    print("✅ User updated successfully!")
                
                return user_id
            else:
                print(f"❌ Failed to create user: {result['message']}")
                return None
                
        except DatabaseClientError as e:
            if e.status_code == 409:
                print("ℹ️  User already exists, retrieving existing user...")
                user = await client.get_user_by_discord_id(111222333, 444555666)
                if user["success"]:
                    return user["data"]["id"]
            else:
                print(f"❌ Error: {e}")
                return None


async def demo_tag_management(user_id: str):
    """Demonstrate tag management features."""
    print("\n🏷️  Tag Management Demo")
    print("-" * 40)
    
    async with DatabaseClient("http://localhost:8001", "your-secret-key") as client:
        try:
            # Add tags
            print("Adding tags to user...")
            await client.add_user_tag(user_id, "api-demo")
            await client.add_user_tag(user_id, "v1.1.0-tested")
            print("✅ Tags added successfully!")
            
            # Get users by tag
            print("\nFinding users with 'developer' tag...")
            result = await client.get_users_by_tag("developer")
            if result["success"]:
                print(f"✅ Found {len(result['data'])} developers")
                for user in result["data"][:3]:  # Show first 3
                    print(f"   - {user['real_name']} ({user['email']})")
            
        except Exception as e:
            print(f"❌ Tag management error: {e}")


async def demo_advanced_search():
    """Demonstrate advanced search and query capabilities."""
    print("\n🔍 Advanced Search Demo")
    print("-" * 40)
    
    async with DatabaseClient("http://localhost:8001", "your-secret-key") as client:
        try:
            # Advanced query with multiple filters
            print("Performing advanced user query...")
            query_params = {
                "is_active": True,
                "limit": 5,
                "order_by": "-registered_at",
                "public_only": True
            }
            
            result = await client.query_users(query_params)
            if result["success"]:
                print(f"✅ Found {result['pagination']['total']} active users")
                print("Recent users:")
                for user in result["data"]:
                    print(f"   - {user['real_name']} (registered: {user['registered_at'][:10]})")
            
            # Search by name
            print("\nSearching users by name...")
            search_result = await client.search_users_by_name("Demo")
            if search_result["success"]:
                print(f"✅ Found {len(search_result['data'])} users with 'Demo' in name")
            
            # List users with pagination
            print("\nListing users with pagination...")
            list_result = await client.list_users(limit=3, offset=0, active_only=True)
            if list_result["success"]:
                print(f"✅ Retrieved {len(list_result['data'])} users")
                print(f"   Total active users: {list_result['pagination']['total']}")
            
        except Exception as e:
            print(f"❌ Search error: {e}")


async def demo_analytics():
    """Demonstrate analytics and statistics features."""
    print("\n📊 Analytics Demo")
    print("-" * 40)
    
    async with DatabaseClient("http://localhost:8001", "your-secret-key") as client:
        try:
            print("Retrieving user statistics...")
            result = await client.get_user_statistics()
            if result["success"]:
                stats = result["data"]
                print("✅ Database Statistics:")
                print(f"   📈 Total Users: {stats['total_users']}")
                print(f"   🟢 Active Users: {stats['active_users']}")
                print(f"   ✅ Verified Users: {stats['verified_users']}")
                print(f"   📅 New Registrations (30d): {stats['recent_registrations_30d']}")
                print(f"   📊 Verification Rate: {stats['verification_rate']:.1f}%")
            
        except Exception as e:
            print(f"❌ Analytics error: {e}")


async def demo_user_management(user_id: str):
    """Demonstrate user status management."""
    print("\n👥 User Management Demo")
    print("-" * 40)
    
    async with DatabaseClient("http://localhost:8001", "your-secret-key") as client:
        try:
            # Update login timestamp
            print("Updating user login timestamp...")
            result = await client.update_user_login(user_id)
            if result["success"]:
                print("✅ Login timestamp updated!")
            
            # Deactivate and reactivate user (demonstration only)
            print("\nTesting user deactivation/activation...")
            
            deactivate_result = await client.deactivate_user(user_id)
            if deactivate_result["success"]:
                print("✅ User deactivated successfully")
                
                # Check user status
                user = await client.get_user_by_id(user_id)
                if user["success"]:
                    print(f"   User active status: {user['data']['is_active']}")
                
                # Reactivate
                activate_result = await client.activate_user(user_id)
                if activate_result["success"]:
                    print("✅ User reactivated successfully")
            
        except Exception as e:
            print(f"❌ User management error: {e}")


async def demo_bulk_operations():
    """Demonstrate bulk operations."""
    print("\n🔄 Bulk Operations Demo")
    print("-" * 40)
    
    async with DatabaseClient("http://localhost:8001", "your-secret-key") as client:
        try:
            # First, get some user IDs for bulk update
            users = await client.list_users(limit=2)
            if users["success"] and len(users["data"]) > 0:
                user_ids = [user["id"] for user in users["data"]]
                
                print(f"Performing bulk update on {len(user_ids)} users...")
                update_data = {
                    "tags": ["bulk-updated", "demo"]
                }
                
                result = await client.bulk_update_users(user_ids, update_data)
                if result["success"]:
                    print(f"✅ Bulk updated {result['data']['updated_count']} users")
                else:
                    print(f"❌ Bulk update failed: {result['message']}")
            else:
                print("ℹ️  No users available for bulk operations demo")
                
        except Exception as e:
            print(f"❌ Bulk operations error: {e}")


async def demo_error_handling():
    """Demonstrate error handling capabilities."""
    print("\n⚠️  Error Handling Demo")
    print("-" * 40)
    
    async with DatabaseClient("http://localhost:8001", "your-secret-key") as client:
        try:
            # Try to get non-existent user
            print("Testing error handling with non-existent user...")
            result = await client.get_user_by_id("000000000000000000000000")
            print(f"❌ Unexpected success: {result}")
            
        except DatabaseClientError as e:
            print(f"✅ Properly handled error: {e.status_code} - {e}")
        
        try:
            # Try to create user with invalid data
            print("Testing validation error handling...")
            invalid_data = {
                "user_id": -1,  # Invalid user ID
                "guild_id": 123,
                "real_name": "",  # Empty name
                "email": "invalid-email"  # Invalid email format
            }
            result = await client.create_user(invalid_data)
            print(f"❌ Unexpected success: {result}")
            
        except DatabaseClientError as e:
            print(f"✅ Properly handled validation error: {e.status_code} - {e}")


async def main():
    """Main demonstration function."""
    print("🚀 HackIt Database Service v1.1.0 - Feature Demo")
    print("=" * 60)
    print("This demo showcases the enhanced features and capabilities")
    print("of the optimized HackIt Database Service.\n")
    
    try:
        # Check service health first
        async with DatabaseClient("http://localhost:8001", "your-secret-key") as client:
            health = await client.health_check()
            if health["status"] == "healthy":
                print(f"✅ Service is healthy (v{health['version']})")
            else:
                print("❌ Service is not healthy!")
                return
        
        # Run demonstrations
        user_id = await demo_basic_crud()
        
        if user_id:
            await demo_tag_management(user_id)
            await demo_user_management(user_id)
        
        await demo_advanced_search()
        await demo_analytics()
        await demo_bulk_operations()
        await demo_error_handling()
        
        print("\n🎉 Demo completed successfully!")
        print("\nKey improvements in v1.1.0:")
        print("• 🔐 Enhanced security with HMAC authentication and rate limiting")
        print("• 🏗️  Extensible architecture with base classes for easy model addition")
        print("• 🔍 Advanced search and filtering capabilities")
        print("• 🏷️  Tag management system for user categorization")
        print("• 📊 Analytics and statistics for user insights")
        print("• 🔄 Bulk operations for efficient data management")
        print("• 👥 Comprehensive user status management")
        print("• 📱 Public/private data separation")
        print("• ⚡ 22 endpoints for complete user lifecycle management")
        
    except Exception as e:
        print(f"\n💥 Demo failed: {str(e)}")
        print("\nPlease ensure:")
        print("1. Database service is running on http://localhost:8001")
        print("2. MongoDB is accessible and running")
        print("3. API secret key matches service configuration")


if __name__ == "__main__":
    asyncio.run(main()) 