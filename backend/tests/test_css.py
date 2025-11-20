import pytest
import requests
from datetime import datetime
import json

BASE_URL = "https://babel-cogito.preview.emergentagent.com/api"

class TestCSS:
    """Test CSS creation and AI integration endpoints"""
    
    @classmethod
    def setup_class(cls):
        """Setup test user and get auth token"""
        timestamp = datetime.now().strftime('%H%M%S')
        test_data = {
            "email": f"css_test_{timestamp}@example.com",
            "password": "SecurePass123!"
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=test_data)
        data = response.json()
        cls.token = data["access_token"]
        cls.user_id = data["user_id"]
        cls.headers = {"Authorization": f"Bearer {cls.token}"}
        
        # Create profile
        profile_data = {"vibe_identity": "CSS Tester"}
        requests.post(f"{BASE_URL}/v3/profile/create", json=profile_data, headers=cls.headers)
    
    def test_create_css_with_ai(self):
        """Test CSS creation with OpenAI integration"""
        css_data = {
            "emotion_input": "I feel serene and contemplative, like sitting by a calm lake at sunset"
        }
        
        response = requests.post(
            f"{BASE_URL}/css/create", 
            json=css_data, 
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert "color" in data
        assert "light_frequency" in data
        assert "sound_texture" in data
        assert "emotion_label" in data
        assert "description" in data
        
        # Verify AI generated real data (not fallback)
        assert data["color"].startswith("#")
        assert len(data["color"]) == 7  # Hex color format
        assert 0.0 <= data["light_frequency"] <= 1.0
        assert len(data["emotion_label"]) > 0
        assert len(data["description"]) > 10  # Should be descriptive
        
        # Store CSS ID for other tests
        self.__class__.css_id = data["id"]
    
    def test_css_with_location(self):
        """Test CSS creation with location data"""
        css_data = {
            "emotion_input": "Feeling energized and motivated",
            "location": {
                "lat": 40.7128,
                "lon": -74.0060
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/css/create", 
            json=css_data, 
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "location_hash" in data
        assert data["location_hash"] is not None
    
    def test_get_css_history(self):
        """Test getting user's CSS history"""
        response = requests.get(f"{BASE_URL}/css/my-history", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "history" in data
        assert isinstance(data["history"], list)
        assert len(data["history"]) >= 1  # Should have at least one from previous test
        
        # Verify history item structure
        if data["history"]:
            item = data["history"][0]
            assert "id" in item
            assert "color" in item
            assert "emotion_label" in item
            assert "timestamp" in item
    
    def test_css_without_auth(self):
        """Test that CSS creation requires authentication"""
        css_data = {"emotion_input": "Test without auth"}
        
        response = requests.post(f"{BASE_URL}/css/create", json=css_data)
        assert response.status_code == 403  # Forbidden without auth
    
    def test_css_profile_count_update(self):
        """Test that CSS creation updates profile CSS count"""
        # Get initial CSS count
        profile_response = requests.get(f"{BASE_URL}/v3/profile/me", headers=self.headers)
        initial_count = profile_response.json().get("css_count", 0)
        
        # Create new CSS
        css_data = {"emotion_input": "Testing count update"}
        requests.post(f"{BASE_URL}/css/create", json=css_data, headers=self.headers)
        
        # Check updated count
        profile_response = requests.get(f"{BASE_URL}/v3/profile/me", headers=self.headers)
        new_count = profile_response.json().get("css_count", 0)
        
        assert new_count == initial_count + 1
    
    def test_ai_response_quality(self):
        """Test that AI responses are high quality and contextual"""
        test_cases = [
            "I feel anxious and overwhelmed by work deadlines",
            "Peaceful morning meditation in nature",
            "Excited about a new creative project"
        ]
        
        for emotion_input in test_cases:
            css_data = {"emotion_input": emotion_input}
            response = requests.post(
                f"{BASE_URL}/css/create", 
                json=css_data, 
                headers=self.headers
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify no fallback error
            assert data.get("error") != "fallback"
            
            # Verify contextual response
            assert len(data["description"]) > 20
            assert data["emotion_label"] != "Belirsiz Dalga"  # Not fallback
    
    def test_invalid_emotion_input(self):
        """Test CSS creation with invalid/empty input"""
        css_data = {"emotion_input": ""}
        
        response = requests.post(
            f"{BASE_URL}/css/create", 
            json=css_data, 
            headers=self.headers
        )
        
        # Should still work but might return fallback
        assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__])
