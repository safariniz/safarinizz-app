import requests
import sys
import json
import time
from datetime import datetime

class OpenAIIntegrationTester:
    def __init__(self, base_url="https://babel-cogito.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None

    def register_and_login(self):
        """Register a test user and get token"""
        test_email = f"openai_test_{datetime.now().strftime('%H%M%S')}@gmail.com"
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

    def test_css_creation_with_ai(self):
        """Test CSS creation to see if real AI is working"""
        emotion_inputs = [
            "Bugün çok mutluyum ve enerjik hissediyorum! Güneş parlıyor ve her şey mükemmel.",
            "Derin bir hüzün içindeyim, sanki kalbimdeki ağırlık hiç geçmeyecekmiş gibi.",
            "Öfkeliyim ve sinirli, her şey yanlış gidiyor ve sabrım taştı!"
        ]
        
        results = []
        
        for i, emotion_input in enumerate(emotion_inputs, 1):
            print(f"\n🔍 Testing CSS Creation #{i}...")
            print(f"   Input: {emotion_input[:50]}...")
            
            try:
                headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}
                response = requests.post(
                    f"{self.base_url}/css/create",
                    json={"emotion_input": emotion_input},
                    headers=headers,
                    timeout=60  # Longer timeout for AI processing
                )
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ CSS Creation #{i} - PASSED")
                    print(f"   Emotion Label: {data.get('emotion_label', 'Unknown')}")
                    print(f"   Color: {data.get('color', 'Unknown')}")
                    print(f"   Light Frequency: {data.get('light_frequency', 'Unknown')}")
                    print(f"   Sound Texture: {data.get('sound_texture', 'Unknown')}")
                    print(f"   Description: {data.get('description', 'Unknown')[:100]}...")
                    print(f"   Image URL: {'Yes' if data.get('image_url') else 'No'}")
                    
                    # Check if this looks like AI-generated content or fallback
                    is_fallback = (
                        data.get('emotion_label') == 'Belirsiz Dalga' and
                        data.get('color') == '#8B9DC3' and
                        data.get('light_frequency') == 0.5 and
                        data.get('sound_texture') == 'flowing'
                    )
                    
                    results.append({
                        'test_number': i,
                        'success': True,
                        'is_fallback': is_fallback,
                        'data': data
                    })
                    
                    if is_fallback:
                        print(f"⚠️  This appears to be fallback data (OpenAI API might not be working)")
                    else:
                        print(f"🎉 This appears to be real AI-generated content!")
                        
                else:
                    print(f"❌ CSS Creation #{i} - FAILED: {response.status_code}")
                    try:
                        error_data = response.json()
                        print(f"   Error: {error_data}")
                    except:
                        print(f"   Error: {response.text}")
                    
                    results.append({
                        'test_number': i,
                        'success': False,
                        'is_fallback': False,
                        'data': None
                    })
                
                # Wait between requests to avoid rate limiting
                if i < len(emotion_inputs):
                    print("   Waiting 3 seconds...")
                    time.sleep(3)
                    
            except Exception as e:
                print(f"❌ CSS Creation #{i} error: {e}")
                results.append({
                    'test_number': i,
                    'success': False,
                    'is_fallback': False,
                    'data': None
                })
        
        return results

    def test_css_reflection(self, css_id):
        """Test CSS reflection to see if AI is working"""
        print(f"\n🔍 Testing CSS Reflection...")
        
        try:
            headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}
            response = requests.post(
                f"{self.base_url}/reflection/analyze",
                json={"css_id": css_id},
                headers=headers,
                timeout=60
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                reflection = data.get('reflection', '')
                print(f"✅ CSS Reflection - PASSED")
                print(f"   Reflection: {reflection}")
                
                # Check if this is the fallback response
                is_fallback = "Bu CSS, içinde bir yankı bırakıyor. Belki tanıdık, belki yabancı." in reflection
                
                if is_fallback:
                    print(f"⚠️  This appears to be fallback reflection (OpenAI API might not be working)")
                    return False
                else:
                    print(f"🎉 This appears to be real AI-generated reflection!")
                    return True
                    
            else:
                print(f"❌ CSS Reflection - FAILED: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ CSS Reflection error: {e}")
            return False

    def run_test(self):
        """Run the OpenAI integration test"""
        print("🚀 Testing OpenAI Integration (GPT-4o + DALL-E 3)")
        print("=" * 60)
        
        # Step 1: Register and login
        if not self.register_and_login():
            return False
            
        # Step 2: Test CSS creation with different emotions
        css_results = self.test_css_creation_with_ai()
        
        # Step 3: Test reflection if we have a CSS
        reflection_working = False
        for result in css_results:
            if result['success'] and result['data']:
                css_id = result['data'].get('id')
                if css_id:
                    reflection_working = self.test_css_reflection(css_id)
                    break
        
        # Analyze results
        print(f"\n" + "=" * 60)
        print(f"📊 OpenAI Integration Test Results:")
        
        successful_css = sum(1 for r in css_results if r['success'])
        fallback_css = sum(1 for r in css_results if r['success'] and r['is_fallback'])
        real_ai_css = successful_css - fallback_css
        
        print(f"   CSS Creation: {successful_css}/3 successful")
        print(f"   Real AI CSS: {real_ai_css}/3")
        print(f"   Fallback CSS: {fallback_css}/3")
        print(f"   CSS Reflection: {'Working' if reflection_working else 'Fallback'}")
        
        # Check for images
        images_generated = sum(1 for r in css_results if r['success'] and r['data'] and r['data'].get('image_url'))
        print(f"   DALL-E Images: {images_generated}/3 generated")
        
        if real_ai_css > 0 or reflection_working or images_generated > 0:
            print(f"\n🎉 OpenAI API is working! Credits are available.")
            return True
        else:
            print(f"\n❌ OpenAI API appears to be using fallbacks. Credits might be exhausted or API key invalid.")
            return False

def main():
    tester = OpenAIIntegrationTester()
    success = tester.run_test()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())