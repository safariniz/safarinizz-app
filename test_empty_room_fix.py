import requests
import sys
import json
from datetime import datetime

class EmptyRoomTester:
    def __init__(self, base_url="https://vibemind-1.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None

    def register_and_login(self):
        """Register a test user and get token"""
        test_email = f"empty_room_test_{datetime.now().strftime('%H%M%S')}@gmail.com"
        test_password = "TestPass123!"
        
        try:
            response = requests.post(
                f"{self.base_url}/auth/register",
                json={"email": test_email, "password": test_password},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data['access_token']
                print(f"✅ Registered user: {test_email}")
                return True
            else:
                print(f"❌ Registration failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False

    def create_empty_room(self):
        """Create a room but don't join it (empty room)"""
        try:
            headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}
            response = requests.post(
                f"{self.base_url}/room/create",
                json={},
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                room_id = data['id']
                room_code = data['room_code']
                print(f"✅ Created empty room: {room_code} (ID: {room_id})")
                return room_id
            else:
                print(f"❌ Room creation failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Room creation error: {e}")
            return None

    def test_empty_room_collective_css(self, room_id):
        """Test the fixed empty room collective CSS endpoint"""
        try:
            response = requests.get(
                f"{self.base_url}/room/{room_id}/collective-css",
                timeout=30
            )
            
            print(f"\n🔍 Testing Empty Room Collective CSS...")
            print(f"   URL: {self.base_url}/room/{room_id}/collective-css")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Empty room collective CSS - PASSED")
                print(f"   Response: {json.dumps(data, indent=2)}")
                
                # Verify it's actually empty room data
                if data.get('member_count') == 0 and 'Boş Oda' in data.get('emotion_label', ''):
                    print(f"✅ Correctly returns empty room data")
                    return True
                else:
                    print(f"⚠️  Response doesn't look like empty room data")
                    return False
                    
            elif response.status_code == 404:
                print(f"❌ Still returns 404 - BUG NOT FIXED")
                return False
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Empty room collective CSS error: {e}")
            return False

    def run_test(self):
        """Run the empty room test"""
        print("🚀 Testing Empty Room Collective CSS Fix")
        print("=" * 50)
        
        # Step 1: Register and login
        if not self.register_and_login():
            return False
            
        # Step 2: Create empty room
        room_id = self.create_empty_room()
        if not room_id:
            return False
            
        # Step 3: Test empty room collective CSS
        return self.test_empty_room_collective_css(room_id)

def main():
    tester = EmptyRoomTester()
    success = tester.run_test()
    
    if success:
        print("\n🎉 Empty room collective CSS fix is working!")
    else:
        print("\n❌ Empty room collective CSS fix is NOT working!")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())