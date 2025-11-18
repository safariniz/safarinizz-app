import requests
import sys
import json
from datetime import datetime
import uuid
import time

class CogitoSyncV3APITester:
    def __init__(self, base_url="https://vibemind-1.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.profile_id = None
        self.css_id = None
        self.session_id = None
        self.room_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.critical_failures = []

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

    def run_test(self, name, method, endpoint, expected_status, data=None, auth_required=True, priority="P1"):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if auth_required and self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        
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
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    self.log_test(name, True)
                    return True, response_data
                except:
                    self.log_test(name, True, "No JSON response")
                    return True, {}
            else:
                try:
                    error_data = response.json()
                    error_msg = f"Status {response.status_code}: {error_data}"
                    if priority in ["CRITICAL", "P0"]:
                        self.critical_failures.append(f"{name}: {error_msg}")
                    self.log_test(name, False, error_msg)
                except:
                    error_msg = f"Status {response.status_code}: {response.text}"
                    if priority in ["CRITICAL", "P0"]:
                        self.critical_failures.append(f"{name}: {error_msg}")
                    self.log_test(name, False, error_msg)
                return False, {}

        except Exception as e:
            error_msg = f"Exception: {str(e)}"
            if priority in ["CRITICAL", "P0"]:
                self.critical_failures.append(f"{name}: {error_msg}")
            self.log_test(name, False, error_msg)
            return False, {}

    # ========== AUTHENTICATION TESTS (CRITICAL) ==========
    
    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root Endpoint", "GET", "", 200, auth_required=False, priority="CRITICAL")

    def test_register(self):
        """Test user registration"""
        timestamp = datetime.now().strftime('%H%M%S')
        test_email = f"cogito_test_{timestamp}@example.com"
        test_password = "SecurePass123!"
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data={"email": test_email, "password": test_password},
            auth_required=False,
            priority="CRITICAL"
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user_id']
            print(f"   ✅ Registered user: {test_email}")
            print(f"   ✅ JWT Token received: {self.token[:20]}...")
            return True
        return False

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        success, response = self.run_test(
            "Login Invalid Credentials",
            "POST",
            "auth/login",
            401,
            data={"email": "invalid@test.com", "password": "wrongpass"},
            auth_required=False,
            priority="CRITICAL"
        )
        return success

    # ========== PROFILE MANAGEMENT TESTS (P0) ==========
    
    def test_create_profile(self):
        """Test V3 profile creation with vibe identity"""
        success, response = self.run_test(
            "V3 Profile Creation",
            "POST",
            "v3/profile/create",
            200,
            data={
                "vibe_identity": "Digital Nomad Explorer",
                "bio": "Testing the cognitive sync experience"
            },
            priority="P0"
        )
        
        if success and 'handle' in response:
            self.profile_id = response['id']
            print(f"   ✅ Profile created with handle: {response['handle']}")
            print(f"   ✅ Vibe Identity: {response['vibe_identity']}")
            return True
        return False

    def test_get_my_profile(self):
        """Test getting current user's profile"""
        success, response = self.run_test(
            "Get My Profile",
            "GET",
            "v3/profile/me",
            200,
            priority="P0"
        )
        
        if success and 'handle' in response:
            print(f"   ✅ Retrieved profile: {response['handle']}")
            return True
        return False

    def test_update_profile(self):
        """Test profile update"""
        return self.run_test(
            "Update Profile",
            "PUT",
            "v3/profile/update",
            200,
            data={"bio": "Updated bio for testing purposes"},
            priority="P0"
        )

    # ========== CSS CREATION WITH AI TESTS (P0) ==========
    
    def test_create_css_with_ai(self):
        """Test CSS creation with OpenAI integration"""
        emotion_input = "I feel peaceful and contemplative today, like watching clouds drift across a vast sky"
        
        success, response = self.run_test(
            "CSS Creation with AI",
            "POST",
            "css/create",
            200,
            data={"emotion_input": emotion_input},
            priority="P0"
        )
        
        if success and 'id' in response:
            self.css_id = response['id']
            print(f"   ✅ CSS Created: {response.get('emotion_label', 'Unknown')}")
            print(f"   ✅ Color: {response.get('color', 'Unknown')}")
            print(f"   ✅ Light Frequency: {response.get('light_frequency', 'Unknown')}")
            print(f"   ✅ Sound Texture: {response.get('sound_texture', 'Unknown')}")
            print(f"   ✅ Description: {response.get('description', 'Unknown')}")
            
            # Verify AI generated real data (not fallback)
            if response.get('error') == 'fallback':
                print("   ⚠️  WARNING: AI returned fallback data - OpenAI integration may have issues")
            
            return True
        return False

    def test_get_css_history(self):
        """Test getting user's CSS history"""
        success, response = self.run_test(
            "CSS History",
            "GET",
            "css/my-history",
            200,
            priority="P0"
        )
        
        if success and 'history' in response:
            print(f"   ✅ Retrieved {len(response['history'])} CSS entries")
            return True
        return False

    # ========== SOCIAL FEATURES TESTS (P0) ==========
    
    def test_follow_user(self):
        """Test following another user (simulate with dummy user ID)"""
        dummy_user_id = str(uuid.uuid4())
        success, response = self.run_test(
            "Follow User",
            "POST",
            f"v3/social/follow/{dummy_user_id}",
            200,
            priority="P0"
        )
        
        if success:
            print(f"   ✅ Successfully followed user: {dummy_user_id}")
            return True
        return False

    def test_follow_self_error(self):
        """Test that following yourself returns error"""
        if self.user_id:
            success, response = self.run_test(
                "Follow Self (Should Fail)",
                "POST",
                f"v3/social/follow/{self.user_id}",
                400,
                priority="P0"
            )
            return success
        return False

    def test_get_personalized_feed(self):
        """Test getting personalized social feed"""
        success, response = self.run_test(
            "Personalized Feed",
            "GET",
            "v3/social/feed",
            200,
            priority="P0"
        )
        
        if success and 'feed' in response:
            print(f"   ✅ Retrieved {len(response['feed'])} feed items")
            print(f"   ✅ Is personalized: {response.get('is_personalized', False)}")
            return True
        return False

    def test_get_global_feed(self):
        """Test getting global social feed"""
        success, response = self.run_test(
            "Global Feed",
            "GET",
            "v3/social/global-feed",
            200,
            priority="P0"
        )
        
        if success and 'feed' in response:
            print(f"   ✅ Retrieved {len(response['feed'])} global feed items")
            return True
        return False

    # ========== AI COACH TESTS (P0) ==========
    
    def test_start_coach_session(self):
        """Test starting AI coach session"""
        success, response = self.run_test(
            "Start Coach Session",
            "POST",
            "v3/coach/start-session",
            200,
            priority="P0"
        )
        
        if success and 'session_id' in response:
            self.session_id = response['session_id']
            print(f"   ✅ Coach session started: {self.session_id}")
            return True
        return False

    def test_coach_message(self):
        """Test sending message to AI coach"""
        if not self.session_id:
            self.log_test("Coach Message", False, "No session ID available")
            return False
            
        success, response = self.run_test(
            "Coach Message",
            "POST",
            "v3/coach/message",
            200,
            data={
                "session_id": self.session_id,
                "message": "I'm feeling overwhelmed with work today. Can you help me find some clarity?"
            },
            priority="P0"
        )
        
        if success and 'reply' in response:
            print(f"   ✅ AI Coach replied: {response['reply'][:100]}...")
            return True
        return False

    # ========== COMMUNITY ROOMS TESTS (P1) ==========
    
    def test_list_rooms(self):
        """Test listing community rooms"""
        success, response = self.run_test(
            "List Community Rooms",
            "GET",
            "v3/rooms/list",
            200,
            priority="P1"
        )
        
        if success and 'rooms' in response:
            print(f"   ✅ Retrieved {len(response['rooms'])} rooms")
            if response['rooms']:
                self.room_id = response['rooms'][0].get('id')
                print(f"   ✅ First room ID: {self.room_id}")
            return True
        return False

    def test_trending_rooms(self):
        """Test getting trending rooms"""
        success, response = self.run_test(
            "Trending Rooms",
            "GET",
            "v3/rooms/trending",
            200,
            priority="P1"
        )
        
        if success and 'rooms' in response:
            print(f"   ✅ Retrieved {len(response['rooms'])} trending rooms")
            return True
        return False

    def test_join_room(self):
        """Test joining a community room"""
        if not self.room_id:
            self.log_test("Join Room", False, "No room ID available")
            return False
            
        success, response = self.run_test(
            "Join Room",
            "POST",
            f"v3/rooms/{self.room_id}/join",
            200,
            priority="P1"
        )
        
        if success:
            print(f"   ✅ Successfully joined room: {self.room_id}")
            return True
        return False

    def test_leave_room(self):
        """Test leaving a community room"""
        if not self.room_id:
            self.log_test("Leave Room", False, "No room ID available")
            return False
            
        success, response = self.run_test(
            "Leave Room",
            "POST",
            f"v3/rooms/{self.room_id}/leave",
            200,
            priority="P1"
        )
        
        if success:
            print(f"   ✅ Successfully left room: {self.room_id}")
            return True
        return False

    # ========== REACTIONS SYSTEM TESTS (P1) ==========
    
    def test_react_to_css(self):
        """Test reacting to CSS"""
        if not self.css_id:
            self.log_test("React to CSS", False, "No CSS ID available")
            return False
            
        success, response = self.run_test(
            "React to CSS",
            "POST",
            "v3/css/react",
            200,
            data={
                "css_id": self.css_id,
                "reaction_type": "wave"
            },
            priority="P1"
        )
        
        if success:
            print(f"   ✅ Successfully reacted to CSS: {self.css_id}")
            return True
        return False

    def test_get_css_reactions(self):
        """Test getting reactions for CSS"""
        if not self.css_id:
            self.log_test("Get CSS Reactions", False, "No CSS ID available")
            return False
            
        success, response = self.run_test(
            "Get CSS Reactions",
            "GET",
            f"v3/css/{self.css_id}/reactions",
            200,
            priority="P1"
        )
        
        if success and 'reactions' in response:
            print(f"   ✅ Retrieved {response.get('count', 0)} reactions")
            return True
        return False

    # ========== PREMIUM FEATURES TESTS (P2) ==========
    
    def test_check_premium_status(self):
        """Test checking premium status"""
        success, response = self.run_test(
            "Check Premium Status",
            "GET",
            "v3/premium/check",
            200,
            priority="P2"
        )
        
        if success and 'is_premium' in response:
            print(f"   ✅ Premium status: {response['is_premium']}")
            return True
        return False

    def test_subscribe_premium(self):
        """Test premium subscription"""
        success, response = self.run_test(
            "Subscribe Premium",
            "POST",
            "v3/premium/subscribe",
            200,
            priority="P2"
        )
        
        if success:
            print(f"   ✅ Premium subscription activated")
            return True
        return False

    def run_all_tests(self):
        """Run comprehensive CogitoSync V3.0 API tests"""
        print("🚀 Starting CogitoSync V3.0 Comprehensive API Tests")
        print("=" * 60)
        print(f"🌐 Backend URL: {self.base_url}")
        print("=" * 60)

        # ========== CRITICAL TESTS ==========
        print("\n🔥 CRITICAL TESTS - Authentication Flow")
        self.test_root_endpoint()
        
        if not self.test_register():
            print("❌ Registration failed - stopping critical tests")
            return False
            
        self.test_login_invalid_credentials()

        if not self.token:
            print("❌ Authentication failed - stopping all tests")
            return False

        # ========== P0 TESTS ==========
        print("\n⭐ P0 TESTS - Core Features")
        
        # Profile Management
        print("\n📋 Profile Management Tests:")
        self.test_create_profile()
        self.test_get_my_profile()
        self.test_update_profile()
        
        # CSS Creation with AI
        print("\n🎨 CSS Creation with AI Tests:")
        self.test_create_css_with_ai()
        self.test_get_css_history()
        
        # Social Features
        print("\n👥 Social Features Tests:")
        self.test_follow_user()
        self.test_follow_self_error()
        self.test_get_personalized_feed()
        self.test_get_global_feed()
        
        # AI Coach
        print("\n🤖 AI Coach Tests:")
        self.test_start_coach_session()
        self.test_coach_message()

        # ========== P1 TESTS ==========
        print("\n🏢 P1 TESTS - Community Features")
        
        # Community Rooms
        print("\n🏠 Community Rooms Tests:")
        self.test_list_rooms()
        self.test_trending_rooms()
        self.test_join_room()
        self.test_leave_room()
        
        # Reactions System
        print("\n💫 Reactions System Tests:")
        self.test_react_to_css()
        self.test_get_css_reactions()

        # ========== P2 TESTS ==========
        print("\n💎 P2 TESTS - Premium Features")
        self.test_check_premium_status()
        self.test_subscribe_premium()

        # ========== SUMMARY ==========
        self.print_test_summary()
        
        return self.tests_passed == self.tests_run

    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 COGITOSYNC V3.0 TEST RESULTS")
        print("=" * 60)
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.critical_failures:
            print(f"\n🚨 CRITICAL FAILURES ({len(self.critical_failures)}):")
            for failure in self.critical_failures:
                print(f"   • {failure}")
        
        if success_rate == 100:
            print("\n🎉 ALL TESTS PASSED! CogitoSync V3.0 backend is fully functional!")
        elif success_rate >= 80:
            print("\n✅ Most tests passed. Minor issues detected.")
        else:
            print("\n⚠️  Significant issues detected. Backend needs attention.")
        
        print("=" * 60)

def main():
    tester = CogitoSyncV3APITester()
    success = tester.run_all_tests()
    
    # Create test reports directory if it doesn't exist
    import os
    os.makedirs('/app/test_reports', exist_ok=True)
    
    # Save detailed results
    with open('/app/test_reports/cogitosync_v3_backend_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'version': '3.0.0',
            'backend_url': tester.base_url,
            'total_tests': tester.tests_run,
            'passed_tests': tester.tests_passed,
            'failed_tests': tester.tests_run - tester.tests_passed,
            'success_rate': (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0,
            'critical_failures': tester.critical_failures,
            'detailed_results': tester.test_results
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: /app/test_reports/cogitosync_v3_backend_results.json")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())