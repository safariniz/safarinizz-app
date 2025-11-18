import pytest
import requests
from datetime import datetime

BASE_URL = "https://vibemind-1.preview.emergentagent.com/api"

class TestCoach:
    """Test V3 AI Coach endpoints"""
    
    @classmethod
    def setup_class(cls):
        """Setup test user and get auth token"""
        timestamp = datetime.now().strftime('%H%M%S')
        test_data = {
            "email": f"coach_test_{timestamp}@example.com",
            "password": "SecurePass123!"
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=test_data)
        data = response.json()
        cls.token = data["access_token"]
        cls.user_id = data["user_id"]
        cls.headers = {"Authorization": f"Bearer {cls.token}"}
        
        # Create profile
        profile_data = {"vibe_identity": "Coach Tester"}
        requests.post(f"{BASE_URL}/v3/profile/create", json=profile_data, headers=cls.headers)
    
    def test_start_coach_session(self):
        """Test starting AI coach session"""
        response = requests.post(
            f"{BASE_URL}/v3/coach/start-session", 
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "session_id" in data
        assert len(data["session_id"]) > 0
        
        # Store session ID for other tests
        self.__class__.session_id = data["session_id"]
    
    def test_coach_message_basic(self):
        """Test sending basic message to AI coach"""
        message_data = {
            "session_id": self.session_id,
            "message": "Hello, I'm feeling a bit stressed today. Can you help?"
        }
        
        response = requests.post(
            f"{BASE_URL}/v3/coach/message", 
            json=message_data, 
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "reply" in data
        assert len(data["reply"]) > 10  # Should be a meaningful response
        
        # Verify it's an empathetic response (basic check)
        reply_lower = data["reply"].lower()
        empathy_indicators = ["sorry", "understand", "help", "support", "feel", "here"]
        assert any(indicator in reply_lower for indicator in empathy_indicators)
    
    def test_coach_message_emotional_support(self):
        """Test coach response to emotional support request"""
        message_data = {
            "session_id": self.session_id,
            "message": "I'm feeling overwhelmed with work and personal life. Everything seems too much."
        }
        
        response = requests.post(
            f"{BASE_URL}/v3/coach/message", 
            json=message_data, 
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "reply" in data
        assert len(data["reply"]) > 20  # Should be substantial response
        
        # Check for supportive language
        reply = data["reply"].lower()
        supportive_phrases = ["understand", "overwhelming", "support", "help", "together", "okay"]
        assert any(phrase in reply for phrase in supportive_phrases)
    
    def test_coach_multi_turn_conversation(self):
        """Test multi-turn conversation with coach"""
        messages = [
            "I've been having trouble sleeping lately.",
            "Yes, I've been thinking about work a lot before bed.",
            "That sounds helpful. What specific techniques do you recommend?"
        ]
        
        for message in messages:
            message_data = {
                "session_id": self.session_id,
                "message": message
            }
            
            response = requests.post(
                f"{BASE_URL}/v3/coach/message", 
                json=message_data, 
                headers=self.headers
            )
            assert response.status_code == 200
            
            data = response.json()
            assert "reply" in data
            assert len(data["reply"]) > 5
    
    def test_coach_session_persistence(self):
        """Test that coach sessions maintain context"""
        # Start new session for this test
        session_response = requests.post(
            f"{BASE_URL}/v3/coach/start-session", 
            headers=self.headers
        )
        new_session_id = session_response.json()["session_id"]
        
        # First message
        message1_data = {
            "session_id": new_session_id,
            "message": "My name is Alex and I work as a software developer."
        }
        requests.post(f"{BASE_URL}/v3/coach/message", json=message1_data, headers=self.headers)
        
        # Second message referencing first
        message2_data = {
            "session_id": new_session_id,
            "message": "Can you help me with stress related to my job?"
        }
        response = requests.post(
            f"{BASE_URL}/v3/coach/message", 
            json=message2_data, 
            headers=self.headers
        )
        
        # Coach should maintain context (though this is hard to test definitively)
        assert response.status_code == 200
        data = response.json()
        assert len(data["reply"]) > 10
    
    def test_coach_invalid_session(self):
        """Test coach message with invalid session ID"""
        message_data = {
            "session_id": "invalid-session-id",
            "message": "This should fail"
        }
        
        response = requests.post(
            f"{BASE_URL}/v3/coach/message", 
            json=message_data, 
            headers=self.headers
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_coach_without_auth(self):
        """Test that coach endpoints require authentication"""
        # Start session without auth
        response = requests.post(f"{BASE_URL}/v3/coach/start-session")
        assert response.status_code == 403
        
        # Send message without auth
        message_data = {
            "session_id": "test-session",
            "message": "Test message"
        }
        response = requests.post(f"{BASE_URL}/v3/coach/message", json=message_data)
        assert response.status_code == 403
    
    def test_coach_empty_message(self):
        """Test coach response to empty message"""
        message_data = {
            "session_id": self.session_id,
            "message": ""
        }
        
        response = requests.post(
            f"{BASE_URL}/v3/coach/message", 
            json=message_data, 
            headers=self.headers
        )
        
        # Should still respond (coach should handle empty input gracefully)
        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
    
    def test_coach_response_quality(self):
        """Test that coach responses are appropriate and helpful"""
        test_scenarios = [
            "I'm feeling anxious about an upcoming presentation.",
            "I had a great day today and feel really positive!",
            "I'm struggling with motivation to exercise regularly."
        ]
        
        for scenario in test_scenarios:
            message_data = {
                "session_id": self.session_id,
                "message": scenario
            }
            
            response = requests.post(
                f"{BASE_URL}/v3/coach/message", 
                json=message_data, 
                headers=self.headers
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Basic quality checks
            reply = data["reply"]
            assert len(reply) > 15  # Substantial response
            assert not reply.startswith("I'm having trouble")  # Not error message
            assert "." in reply or "!" in reply  # Proper punctuation

if __name__ == "__main__":
    pytest.main([__file__])
