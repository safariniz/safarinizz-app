import pytest
import requests
from datetime import datetime

BASE_URL = "https://vibemind-1.preview.emergentagent.com/api"

class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_root_endpoint(self):
        """Test root API endpoint"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "CogitoSync v3.0 - Production"
        assert data["version"] == "3.0.0"
    
    def test_user_registration(self):
        """Test user registration with valid data"""
        timestamp = datetime.now().strftime('%H%M%S')
        test_data = {
            "email": f"test_auth_{timestamp}@example.com",
            "password": "SecurePass123!"
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=test_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "user_id" in data
        assert data["token_type"] == "bearer"
        assert data["email"] == test_data["email"]
        
        # Store token for other tests
        self.token = data["access_token"]
        self.user_id = data["user_id"]
    
    def test_duplicate_registration(self):
        """Test registration with existing email fails"""
        test_data = {
            "email": "duplicate@example.com",
            "password": "SecurePass123!"
        }
        
        # First registration
        requests.post(f"{BASE_URL}/auth/register", json=test_data)
        
        # Second registration should fail
        response = requests.post(f"{BASE_URL}/auth/register", json=test_data)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        test_data = {
            "email": "invalid@example.com",
            "password": "wrongpassword"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=test_data)
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_jwt_token_validation(self):
        """Test that JWT tokens are properly formatted"""
        timestamp = datetime.now().strftime('%H%M%S')
        test_data = {
            "email": f"jwt_test_{timestamp}@example.com",
            "password": "SecurePass123!"
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=test_data)
        token = response.json()["access_token"]
        
        # JWT tokens have 3 parts separated by dots
        parts = token.split('.')
        assert len(parts) == 3
        
        # Test using token for authenticated request
        headers = {"Authorization": f"Bearer {token}"}
        profile_response = requests.get(f"{BASE_URL}/v3/profile/me", headers=headers)
        # Should not be 401 (unauthorized)
        assert profile_response.status_code != 401

if __name__ == "__main__":
    pytest.main([__file__])
