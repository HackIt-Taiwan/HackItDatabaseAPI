#!/usr/bin/env python3
"""
Test script for HackIt Database Service API v1.1.0
Tests all endpoints and validates functionality.
"""

import asyncio
import json
import sys
from typing import Dict, Any
from database_client import DatabaseClient, DatabaseClientError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class APITester:
    """Comprehensive API testing class for HackIt Database Service."""
    
    def __init__(self, base_url: str = "http://localhost:8001", api_secret: str = "your-secret-key"):
        """Initialize API tester with client configuration."""
        self.base_url = base_url
        self.api_secret = api_secret
        self.test_user_id = None
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "tests": []
        }
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result."""
        status = "PASS" if success else "FAIL"
        logger.info(f"[{status}] {test_name}: {message}")
        
        self.test_results["tests"].append({
            "name": test_name,
            "status": status,
            "message": message
        })
        
        if success:
            self.test_results["passed"] += 1
        else:
            self.test_results["failed"] += 1
    
    async def test_health_check(self, client: DatabaseClient) -> bool:
        """Test health check endpoint."""
        try:
            response = await client.health_check()
            if response.get("status") == "healthy":
                self.log_test("Health Check", True, f"Service version: {response.get('version')}")
                return True
            else:
                self.log_test("Health Check", False, f"Service unhealthy: {response}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, str(e))
            return False
    
    async def test_create_user(self, client: DatabaseClient) -> bool:
        """Test user creation."""
        try:
            user_data = {
                "user_id": 123456789,
                "guild_id": 987654321,
                "real_name": "Test User",
                "email": "test@example.com",
                "bio": "This is a test user for API validation",
                "location": "Taiwan",
                "github_username": "testuser",
                "tags": ["developer", "tester"]
            }
            
            response = await client.create_user(user_data)
            if response.get("success"):
                self.test_user_id = response["data"]["id"]
                self.log_test("Create User", True, f"Created user with ID: {self.test_user_id}")
                return True
            else:
                self.log_test("Create User", False, response.get("message", "Unknown error"))
                return False
        except DatabaseClientError as e:
            if e.status_code == 409:
                # User already exists, try to find it
                try:
                    response = await client.get_user_by_discord_id(123456789, 987654321)
                    if response.get("success"):
                        self.test_user_id = response["data"]["id"]
                        self.log_test("Create User", True, f"User already exists with ID: {self.test_user_id}")
                        return True
                except:
                    pass
            self.log_test("Create User", False, str(e))
            return False
        except Exception as e:
            self.log_test("Create User", False, str(e))
            return False
    
    async def test_get_user_operations(self, client: DatabaseClient) -> bool:
        """Test various user retrieval operations."""
        if not self.test_user_id:
            self.log_test("Get User Operations", False, "No test user ID available")
            return False
        
        success_count = 0
        total_tests = 4
        
        # Test get by ID
        try:
            response = await client.get_user_by_id(self.test_user_id)
            if response.get("success"):
                self.log_test("Get User by ID", True)
                success_count += 1
            else:
                self.log_test("Get User by ID", False, response.get("message"))
        except Exception as e:
            self.log_test("Get User by ID", False, str(e))
        
        # Test get public info
        try:
            response = await client.get_user_by_id(self.test_user_id, public_only=True)
            if response.get("success"):
                self.log_test("Get User Public Info", True)
                success_count += 1
            else:
                self.log_test("Get User Public Info", False, response.get("message"))
        except Exception as e:
            self.log_test("Get User Public Info", False, str(e))
        
        # Test get by email
        try:
            response = await client.get_user_by_email("test@example.com")
            if response.get("success"):
                self.log_test("Get User by Email", True)
                success_count += 1
            else:
                self.log_test("Get User by Email", False, response.get("message"))
        except Exception as e:
            self.log_test("Get User by Email", False, str(e))
        
        # Test get by Discord ID
        try:
            response = await client.get_user_by_discord_id(123456789, 987654321)
            if response.get("success"):
                self.log_test("Get User by Discord ID", True)
                success_count += 1
            else:
                self.log_test("Get User by Discord ID", False, response.get("message"))
        except Exception as e:
            self.log_test("Get User by Discord ID", False, str(e))
        
        return success_count == total_tests
    
    async def test_update_user(self, client: DatabaseClient) -> bool:
        """Test user update operations."""
        if not self.test_user_id:
            self.log_test("Update User", False, "No test user ID available")
            return False
        
        try:
            update_data = {
                "bio": "Updated bio for testing",
                "website": "https://example.com",
                "linkedin_url": "https://linkedin.com/in/testuser"
            }
            
            response = await client.update_user(self.test_user_id, update_data)
            if response.get("success"):
                self.log_test("Update User", True)
                return True
            else:
                self.log_test("Update User", False, response.get("message"))
                return False
        except Exception as e:
            self.log_test("Update User", False, str(e))
            return False
    
    async def test_tag_operations(self, client: DatabaseClient) -> bool:
        """Test tag management operations."""
        if not self.test_user_id:
            self.log_test("Tag Operations", False, "No test user ID available")
            return False
        
        success_count = 0
        
        # Test add tag
        try:
            response = await client.add_user_tag(self.test_user_id, "api-tested")
            if response.get("success"):
                self.log_test("Add User Tag", True)
                success_count += 1
            else:
                self.log_test("Add User Tag", False, response.get("message"))
        except Exception as e:
            self.log_test("Add User Tag", False, str(e))
        
        # Test get users by tag
        try:
            response = await client.get_users_by_tag("api-tested")
            if response.get("success"):
                self.log_test("Get Users by Tag", True)
                success_count += 1
            else:
                self.log_test("Get Users by Tag", False, response.get("message"))
        except Exception as e:
            self.log_test("Get Users by Tag", False, str(e))
        
        return success_count == 2
    
    async def test_search_operations(self, client: DatabaseClient) -> bool:
        """Test search and query operations."""
        success_count = 0
        
        # Test list users
        try:
            response = await client.list_users(limit=5)
            if response.get("success"):
                self.log_test("List Users", True, f"Found {len(response['data'])} users")
                success_count += 1
            else:
                self.log_test("List Users", False, response.get("message"))
        except Exception as e:
            self.log_test("List Users", False, str(e))
        
        # Test search by name
        try:
            response = await client.search_users_by_name("Test")
            if response.get("success"):
                self.log_test("Search Users by Name", True, f"Found {len(response['data'])} users")
                success_count += 1
            else:
                self.log_test("Search Users by Name", False, response.get("message"))
        except Exception as e:
            self.log_test("Search Users by Name", False, str(e))
        
        # Test advanced query
        try:
            query_params = {
                "is_active": True,
                "limit": 10,
                "order_by": "-registered_at"
            }
            response = await client.query_users(query_params)
            if response.get("success"):
                self.log_test("Advanced User Query", True, f"Found {len(response['data'])} users")
                success_count += 1
            else:
                self.log_test("Advanced User Query", False, response.get("message"))
        except Exception as e:
            self.log_test("Advanced User Query", False, str(e))
        
        return success_count == 3
    
    async def test_analytics(self, client: DatabaseClient) -> bool:
        """Test analytics and statistics."""
        try:
            response = await client.get_user_statistics()
            if response.get("success"):
                stats = response["data"]
                self.log_test("User Statistics", True, 
                             f"Total users: {stats['total_users']}, Active: {stats['active_users']}")
                return True
            else:
                self.log_test("User Statistics", False, response.get("message"))
                return False
        except Exception as e:
            self.log_test("User Statistics", False, str(e))
            return False
    
    async def test_user_management(self, client: DatabaseClient) -> bool:
        """Test user status management operations."""
        if not self.test_user_id:
            self.log_test("User Management", False, "No test user ID available")
            return False
        
        success_count = 0
        
        # Test update login
        try:
            response = await client.update_user_login(self.test_user_id)
            if response.get("success"):
                self.log_test("Update User Login", True)
                success_count += 1
            else:
                self.log_test("Update User Login", False, response.get("message"))
        except Exception as e:
            self.log_test("Update User Login", False, str(e))
        
        # Test deactivate user
        try:
            response = await client.deactivate_user(self.test_user_id)
            if response.get("success"):
                self.log_test("Deactivate User", True)
                success_count += 1
            else:
                self.log_test("Deactivate User", False, response.get("message"))
        except Exception as e:
            self.log_test("Deactivate User", False, str(e))
        
        # Test activate user
        try:
            response = await client.activate_user(self.test_user_id)
            if response.get("success"):
                self.log_test("Activate User", True)
                success_count += 1
            else:
                self.log_test("Activate User", False, response.get("message"))
        except Exception as e:
            self.log_test("Activate User", False, str(e))
        
        return success_count == 3
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all API tests."""
        logger.info("🚀 Starting HackIt Database Service API Tests v1.1.0")
        logger.info("=" * 60)
        
        async with DatabaseClient(self.base_url, self.api_secret) as client:
            # Core functionality tests
            await self.test_health_check(client)
            await self.test_create_user(client)
            await self.test_get_user_operations(client)
            await self.test_update_user(client)
            
            # Advanced feature tests
            await self.test_tag_operations(client)
            await self.test_search_operations(client)
            await self.test_analytics(client)
            await self.test_user_management(client)
        
        # Print summary
        logger.info("=" * 60)
        logger.info(f"📊 Test Summary:")
        logger.info(f"   ✅ Passed: {self.test_results['passed']}")
        logger.info(f"   ❌ Failed: {self.test_results['failed']}")
        logger.info(f"   📈 Success Rate: {(self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed']) * 100):.1f}%")
        
        return self.test_results


async def main():
    """Main test function."""
    # Configuration
    base_url = "http://localhost:8001"
    api_secret = "your-secret-key"
    
    print("🔧 HackIt Database Service API Tester v1.1.0")
    print("=" * 50)
    print(f"Service URL: {base_url}")
    print(f"Testing comprehensive API functionality...")
    print()
    
    try:
        tester = APITester(base_url, api_secret)
        results = await tester.run_all_tests()
        
        # Return appropriate exit code
        if results["failed"] == 0:
            print("\n🎉 All tests passed! API is working correctly.")
            return 0
        else:
            print(f"\n⚠️  {results['failed']} test(s) failed. Please check the service.")
            return 1
    
    except Exception as e:
        logger.error(f"Fatal error during testing: {str(e)}")
        print("\n💥 Testing failed due to connection or configuration issues.")
        print("Please ensure:")
        print("1. Database service is running on http://localhost:8001")
        print("2. MongoDB is accessible")
        print("3. API secret key is correctly configured")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 