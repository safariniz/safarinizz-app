import requests
import sys
import json
from datetime import datetime

class CogitoSyncAPITester:
    def __init__(self, base_url="https://cognitivehub-1.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, auth_required=True):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if auth_required and self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)

            print(f"   Status: {response.status_code}")
            
            success = response.status_code == expected_status
            
            if success:
                try:
                    response_data = response.json()
                    self.log_test(name, True)
                    return True, response_data
                except:
                    self.log_test(name, True, "No JSON response")
                    return True, {}
            else:
                try:
                    error_data = response.json()
                    self.log_test(name, False, f"Status {response.status_code}: {error_data}")
                except:
                    self.log_test(name, False, f"Status {response.status_code}: {response.text}")
                return False, {}

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root Endpoint", "GET", "", 200, auth_required=False)

    def test_register(self):
        """Test user registration"""
        test_email = f"test_{datetime.now().strftime('%H%M%S')}@cogitosync.test"
        test_password = "TestPass123!"
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data={"email": test_email, "password": test_password},
            auth_required=False
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user_id']
            print(f"   Registered user: {test_email}")
            return True
        return False

    def test_login(self):
        """Test user login with existing credentials"""
        # Try to login with a test account
        test_email = "test@cogitosync.test"
        test_password = "TestPass123!"
        
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data={"email": test_email, "password": test_password},
            auth_required=False
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user_id']
            return True
        return False

    def test_create_css(self):
        """Test CSS creation with AI"""
        emotion_input = "Bugün kendimi huzurlu ama biraz melankolik hissediyorum. İçimde hafif bir nostalji var."
        
        success, response = self.run_test(
            "CSS Creation",
            "POST",
            "css/create",
            200,
            data={"emotion_input": emotion_input}
        )
        
        if success and 'id' in response:
            self.css_id = response['id']
            print(f"   Created CSS: {response.get('emotion_label', 'Unknown')}")
            print(f"   Color: {response.get('color', 'Unknown')}")
            print(f"   Light Frequency: {response.get('light_frequency', 'Unknown')}")
            print(f"   Sound Texture: {response.get('sound_texture', 'Unknown')}")
            return True
        return False

    def test_get_css_history(self):
        """Test getting user's CSS history"""
        return self.run_test("CSS History", "GET", "css/my-history", 200)

    def test_get_css_by_id(self):
        """Test getting CSS by ID"""
        if hasattr(self, 'css_id'):
            return self.run_test("Get CSS by ID", "GET", f"css/{self.css_id}", 200, auth_required=False)
        else:
            self.log_test("Get CSS by ID", False, "No CSS ID available")
            return False

    def test_create_room(self):
        """Test room creation"""
        success, response = self.run_test("Room Creation", "POST", "room/create", 200, data={})
        
        if success and 'room_code' in response:
            self.room_code = response['room_code']
            self.room_id = response['id']
            print(f"   Room Code: {self.room_code}")
            return True
        return False

    def test_join_room(self):
        """Test joining a room"""
        if hasattr(self, 'room_code') and hasattr(self, 'css_id'):
            success, response = self.run_test(
                "Join Room",
                "POST",
                "room/join",
                200,
                data={"room_code": self.room_code, "css_id": self.css_id}
            )
            return success
        else:
            self.log_test("Join Room", False, "No room code or CSS ID available")
            return False

    def test_get_collective_css(self):
        """Test getting collective CSS"""
        if hasattr(self, 'room_id'):
            return self.run_test("Collective CSS", "GET", f"room/{self.room_id}/collective-css", 200)
        else:
            self.log_test("Collective CSS", False, "No room ID available")
            return False

    def test_get_room_members(self):
        """Test getting room members"""
        if hasattr(self, 'room_id'):
            return self.run_test("Room Members", "GET", f"room/{self.room_id}/members", 200)
        else:
            self.log_test("Room Members", False, "No room ID available")
            return False

    def test_css_reflection(self):
        """Test CSS reflection analysis"""
        if hasattr(self, 'css_id'):
            success, response = self.run_test(
                "CSS Reflection",
                "POST",
                "reflection/analyze",
                200,
                data={"css_id": self.css_id}
            )
            if success and 'reflection' in response:
                print(f"   Reflection: {response['reflection'][:100]}...")
            return success
        else:
            self.log_test("CSS Reflection", False, "No CSS ID available")
            return False

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting CogitoSync API Tests")
        print("=" * 50)

        # Test basic connectivity
        self.test_root_endpoint()

        # Test authentication
        if not self.test_register():
            # If registration fails, try login
            self.test_login()

        if not self.token:
            print("❌ Authentication failed - stopping tests")
            return False

        # Test CSS functionality
        self.test_create_css()
        self.test_get_css_history()
        self.test_get_css_by_id()

        # Test room functionality
        self.test_create_room()
        self.test_join_room()
        self.test_get_collective_css()
        self.test_get_room_members()

        # Test reflection
        self.test_css_reflection()

        # Print summary
        print("\n" + "=" * 50)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            print("⚠️  Some tests failed")
            return False

def main():
    tester = CogitoSyncAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/test_reports/backend_api_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_tests': tester.tests_run,
            'passed_tests': tester.tests_passed,
            'success_rate': (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0,
            'results': tester.test_results
        }, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())