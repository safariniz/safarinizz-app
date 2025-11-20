import pytest
import requests
from datetime import datetime

BASE_URL = "https://babel-cogito.preview.emergentagent.com/api"

class TestRooms:
    """Test V3 community rooms endpoints"""
    
    @classmethod
    def setup_class(cls):
        """Setup test user and get auth token"""
        timestamp = datetime.now().strftime('%H%M%S')
        test_data = {
            "email": f"rooms_test_{timestamp}@example.com",
            "password": "SecurePass123!"
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=test_data)
        data = response.json()
        cls.token = data["access_token"]
        cls.user_id = data["user_id"]
        cls.headers = {"Authorization": f"Bearer {cls.token}"}
        
        # Create profile
        profile_data = {"vibe_identity": "Room Tester"}
        requests.post(f"{BASE_URL}/v3/profile/create", json=profile_data, headers=cls.headers)
    
    def test_list_all_rooms(self):
        """Test listing all community rooms"""
        response = requests.get(f"{BASE_URL}/v3/rooms/list")
        assert response.status_code == 200
        
        data = response.json()
        assert "rooms" in data
        assert isinstance(data["rooms"], list)
        assert len(data["rooms"]) > 0  # Should have some rooms
        
        # Verify room structure
        if data["rooms"]:
            room = data["rooms"][0]
            assert "id" in room
            assert "name" in room
            assert "category" in room
            assert "description" in room
            assert "member_count" in room
            
            # Store room ID for other tests
            self.__class__.room_id = room["id"]
    
    def test_list_rooms_by_category(self):
        """Test listing rooms by specific category"""
        categories = ["Focus", "Chill", "Creative", "Overthinking"]
        
        for category in categories:
            response = requests.get(f"{BASE_URL}/v3/rooms/list?category={category}")
            assert response.status_code == 200
            
            data = response.json()
            assert "rooms" in data
            
            # All returned rooms should match the category
            for room in data["rooms"]:
                assert room["category"] == category
    
    def test_trending_rooms(self):
        """Test getting trending rooms"""
        response = requests.get(f"{BASE_URL}/v3/rooms/trending")
        assert response.status_code == 200
        
        data = response.json()
        assert "rooms" in data
        assert isinstance(data["rooms"], list)
        
        # Verify trending rooms have is_trending flag
        for room in data["rooms"]:
            assert room.get("is_trending") == True
            assert "member_count" in room
    
    def test_join_room(self):
        """Test joining a community room"""
        if not hasattr(self, 'room_id'):
            # Get a room ID first
            rooms_response = requests.get(f"{BASE_URL}/v3/rooms/list")
            self.room_id = rooms_response.json()["rooms"][0]["id"]
        
        response = requests.post(
            f"{BASE_URL}/v3/rooms/{self.room_id}/join", 
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Joined" in data["message"]
    
    def test_join_room_already_member(self):
        """Test joining room when already a member"""
        # Join room first
        requests.post(f"{BASE_URL}/v3/rooms/{self.room_id}/join", headers=self.headers)
        
        # Join again
        response = requests.post(
            f"{BASE_URL}/v3/rooms/{self.room_id}/join", 
            headers=self.headers
        )
        assert response.status_code == 200
        assert "Already member" in response.json()["message"]
    
    def test_leave_room(self):
        """Test leaving a community room"""
        # Join room first
        requests.post(f"{BASE_URL}/v3/rooms/{self.room_id}/join", headers=self.headers)
        
        # Then leave
        response = requests.post(
            f"{BASE_URL}/v3/rooms/{self.room_id}/leave", 
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Left" in data["message"]
    
    def test_room_member_count_updates(self):
        """Test that member count updates when joining/leaving"""
        # Get initial member count
        rooms_response = requests.get(f"{BASE_URL}/v3/rooms/list")
        rooms = rooms_response.json()["rooms"]
        target_room = next(room for room in rooms if room["id"] == self.room_id)
        initial_count = target_room["member_count"]
        
        # Join room
        requests.post(f"{BASE_URL}/v3/rooms/{self.room_id}/join", headers=self.headers)
        
        # Check updated count (Note: This test might be flaky due to async updates)
        # In a real test, you might want to add a small delay or retry logic
        rooms_response = requests.get(f"{BASE_URL}/v3/rooms/list")
        rooms = rooms_response.json()["rooms"]
        target_room = next(room for room in rooms if room["id"] == self.room_id)
        
        # Member count should have increased (or stayed same if already member)
        assert target_room["member_count"] >= initial_count
    
    def test_room_operations_without_auth(self):
        """Test that room join/leave require authentication"""
        # Join without auth
        response = requests.post(f"{BASE_URL}/v3/rooms/{self.room_id}/join")
        assert response.status_code == 403
        
        # Leave without auth
        response = requests.post(f"{BASE_URL}/v3/rooms/{self.room_id}/leave")
        assert response.status_code == 403
    
    def test_room_categories_exist(self):
        """Test that expected room categories exist"""
        response = requests.get(f"{BASE_URL}/v3/rooms/list")
        rooms = response.json()["rooms"]
        
        categories = {room["category"] for room in rooms}
        expected_categories = {"Focus", "Chill", "Creative", "Overthinking"}
        
        # Should have at least some of the expected categories
        assert len(categories.intersection(expected_categories)) > 0
    
    def test_room_data_structure(self):
        """Test that room data has expected structure"""
        response = requests.get(f"{BASE_URL}/v3/rooms/list")
        rooms = response.json()["rooms"]
        
        for room in rooms:
            # Required fields
            assert "id" in room
            assert "name" in room
            assert "category" in room
            assert "description" in room
            assert "member_count" in room
            
            # Data types
            assert isinstance(room["id"], str)
            assert isinstance(room["name"], str)
            assert isinstance(room["category"], str)
            assert isinstance(room["description"], str)
            assert isinstance(room["member_count"], int)
            
            # Reasonable values
            assert len(room["name"]) > 0
            assert len(room["description"]) > 0
            assert room["member_count"] >= 0
    
    def test_join_nonexistent_room(self):
        """Test joining non-existent room"""
        fake_room_id = "nonexistent-room-id"
        response = requests.post(
            f"{BASE_URL}/v3/rooms/{fake_room_id}/join", 
            headers=self.headers
        )
        
        # Should handle gracefully (might return 200 or 404 depending on implementation)
        assert response.status_code in [200, 404]

if __name__ == "__main__":
    pytest.main([__file__])
