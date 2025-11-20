import pytest
import requests
from datetime import datetime
import uuid

BASE_URL = "https://babel-cogito.preview.emergentagent.com/api"

class TestSocial:
    """Test V3 social features endpoints"""
    
    @classmethod
    def setup_class(cls):
        """Setup test users and get auth tokens"""
        timestamp = datetime.now().strftime('%H%M%S')
        
        # Create first user
        test_data1 = {
            "email": f"social_test1_{timestamp}@example.com",
            "password": "SecurePass123!"
        }
        response1 = requests.post(f"{BASE_URL}/auth/register", json=test_data1)
        data1 = response1.json()
        cls.token1 = data1["access_token"]
        cls.user_id1 = data1["user_id"]
        cls.headers1 = {"Authorization": f"Bearer {cls.token1}"}
        
        # Create second user
        test_data2 = {
            "email": f"social_test2_{timestamp}@example.com",
            "password": "SecurePass123!"
        }
        response2 = requests.post(f"{BASE_URL}/auth/register", json=test_data2)
        data2 = response2.json()
        cls.token2 = data2["access_token"]
        cls.user_id2 = data2["user_id"]
        cls.headers2 = {"Authorization": f"Bearer {cls.token2}"}
        
        # Create profiles for both users
        profile_data1 = {"vibe_identity": "Social Tester 1"}
        profile_data2 = {"vibe_identity": "Social Tester 2"}
        requests.post(f"{BASE_URL}/v3/profile/create", json=profile_data1, headers=cls.headers1)
        requests.post(f"{BASE_URL}/v3/profile/create", json=profile_data2, headers=cls.headers2)
        
        # Create some CSS for feed testing
        css_data = {"emotion_input": "Testing social features"}
        requests.post(f"{BASE_URL}/css/create", json=css_data, headers=cls.headers1)
        requests.post(f"{BASE_URL}/css/create", json=css_data, headers=cls.headers2)
    
    def test_follow_user(self):
        """Test following another user"""
        response = requests.post(
            f"{BASE_URL}/v3/social/follow/{self.user_id2}", 
            headers=self.headers1
        )
        assert response.status_code == 200
        assert "Followed" in response.json()["message"]
    
    def test_follow_self_error(self):
        """Test that following yourself returns error"""
        response = requests.post(
            f"{BASE_URL}/v3/social/follow/{self.user_id1}", 
            headers=self.headers1
        )
        assert response.status_code == 400
        assert "Cannot follow yourself" in response.json()["detail"]
    
    def test_follow_already_following(self):
        """Test following user already being followed"""
        # Follow user (should work)
        requests.post(f"{BASE_URL}/v3/social/follow/{self.user_id2}", headers=self.headers1)
        
        # Follow again (should return already following)
        response = requests.post(
            f"{BASE_URL}/v3/social/follow/{self.user_id2}", 
            headers=self.headers1
        )
        assert response.status_code == 200
        assert "Already following" in response.json()["message"]
    
    def test_unfollow_user(self):
        """Test unfollowing a user"""
        # First follow
        requests.post(f"{BASE_URL}/v3/social/follow/{self.user_id2}", headers=self.headers1)
        
        # Then unfollow
        response = requests.post(
            f"{BASE_URL}/v3/social/unfollow/{self.user_id2}", 
            headers=self.headers1
        )
        assert response.status_code == 200
        assert "Unfollowed" in response.json()["message"]
    
    def test_follower_count_updates(self):
        """Test that follower/following counts update correctly"""
        # Get initial counts
        profile1 = requests.get(f"{BASE_URL}/v3/profile/me", headers=self.headers1).json()
        profile2 = requests.get(f"{BASE_URL}/v3/profile/me", headers=self.headers2).json()
        
        initial_following1 = profile1.get("following_count", 0)
        initial_followers2 = profile2.get("followers_count", 0)
        
        # Follow user
        requests.post(f"{BASE_URL}/v3/social/follow/{self.user_id2}", headers=self.headers1)
        
        # Check updated counts
        profile1 = requests.get(f"{BASE_URL}/v3/profile/me", headers=self.headers1).json()
        profile2 = requests.get(f"{BASE_URL}/v3/profile/me", headers=self.headers2).json()
        
        assert profile1["following_count"] == initial_following1 + 1
        assert profile2["followers_count"] == initial_followers2 + 1
    
    def test_get_personalized_feed(self):
        """Test getting personalized social feed"""
        # Follow user2 to get personalized feed
        requests.post(f"{BASE_URL}/v3/social/follow/{self.user_id2}", headers=self.headers1)
        
        response = requests.get(f"{BASE_URL}/v3/social/feed", headers=self.headers1)
        assert response.status_code == 200
        
        data = response.json()
        assert "feed" in data
        assert "is_personalized" in data
        assert isinstance(data["feed"], list)
        
        # Should be personalized since we're following someone
        assert data["is_personalized"] == True
    
    def test_get_global_feed(self):
        """Test getting global social feed"""
        response = requests.get(f"{BASE_URL}/v3/social/global-feed")
        assert response.status_code == 200
        
        data = response.json()
        assert "feed" in data
        assert isinstance(data["feed"], list)
        
        # Verify feed items have profile data
        if data["feed"]:
            item = data["feed"][0]
            assert "id" in item
            assert "color" in item
            assert "profile" in item
            
            if item["profile"]:
                assert "handle" in item["profile"]
                assert "vibe_identity" in item["profile"]
    
    def test_feed_with_limit(self):
        """Test feed with custom limit parameter"""
        response = requests.get(f"{BASE_URL}/v3/social/global-feed?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["feed"]) <= 5
    
    def test_social_without_auth(self):
        """Test that social endpoints require authentication"""
        # Follow endpoint
        response = requests.post(f"{BASE_URL}/v3/social/follow/{self.user_id2}")
        assert response.status_code == 403
        
        # Personalized feed endpoint
        response = requests.get(f"{BASE_URL}/v3/social/feed")
        assert response.status_code == 403
    
    def test_follow_nonexistent_user(self):
        """Test following non-existent user"""
        fake_user_id = str(uuid.uuid4())
        response = requests.post(
            f"{BASE_URL}/v3/social/follow/{fake_user_id}", 
            headers=self.headers1
        )
        # Should still return 200 (follow operation doesn't validate target user exists)
        assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__])
