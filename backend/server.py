from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import jwt
from passlib.context import CryptContext
import openai
import json
import random
import string
import asyncio
import hashlib

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
mongo_client = AsyncIOMotorClient(mongo_url)
db = mongo_client[os.environ['DB_NAME']]

openai_client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = os.environ['JWT_SECRET']
JWT_ALGORITHM = os.environ['JWT_ALGORITHM']
JWT_EXPIRATION_HOURS = int(os.environ.get('JWT_EXPIRATION_HOURS', 168))

security = HTTPBearer()
app = FastAPI(title="CogitoSync v3.0")
api_router = APIRouter(prefix="/api")

# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, room_id: str = "global"):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, room_id: str = "global"):
        if room_id in self.active_connections and websocket in self.active_connections[room_id]:
            self.active_connections[room_id].remove(websocket)
    
    async def broadcast(self, message: dict, room_id: str = "global"):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass

manager = ConnectionManager()

# Models
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    password_hash: str
    is_premium: bool = False
    premium_expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    is_premium: bool = False

class CSS(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    color: str
    light_frequency: float
    sound_texture: str
    emotion_label: str
    description: str
    image_url: Optional[str] = None
    location_hash: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CSSCreate(BaseModel):
    emotion_input: str
    location: Optional[Dict[str, float]] = None
    language: Optional[str] = 'tr'

class ProfileCreate(BaseModel):
    vibe_identity: str
    bio: Optional[str] = None

class ProfileUpdate(BaseModel):
    bio: Optional[str] = None
    vibe_identity: Optional[str] = None

class CoachMessage(BaseModel):
    session_id: str
    message: str
    language: Optional[str] = 'tr'

class Reaction(BaseModel):
    css_id: str
    reaction_type: str  # wave, pulse, spiral, color-shift

# Utilities
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def generate_handle():
    return f"vibe-{''.join(random.choices(string.digits, k=4))}"

def hash_location(lat: float, lon: float, precision: int = 3) -> str:
    rounded_lat = round(lat, precision)
    rounded_lon = round(lon, precision)
    return hashlib.md5(f"{rounded_lat}:{rounded_lon}".encode()).hexdigest()[:8]

# AI Functions
async def generate_css_with_ai(emotion_input: str, language: str = 'tr') -> dict:
    try:
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("API key not configured")
        
        if language == 'en':
            system_prompt = """Create a JSON object representing an emotional cognitive state snapshot.
Return ONLY valid JSON with these fields:
{
  "color": "#RRGGBB hex color code",
  "light_frequency": number between 0.0 and 1.0,
  "sound_texture": "descriptive word like flowing/sharp/warm",
  "emotion_label": "short English emotion label (e.g., Peaceful Focus, Excited Energy, Soft Anxiety)",
  "description": "short poetic English description"
}
All values must be correct types. light_frequency must be a number (float), not a string. All text must be in English."""
        else:
            system_prompt = """Duygusal bir bilişsel durum anlık görüntüsünü temsil eden bir JSON nesnesi oluştur.
SADECE şu alanları içeren geçerli JSON döndür:
{
  "color": "#RRGGBB hex renk kodu",
  "light_frequency": 0.0 ile 1.0 arasında sayı,
  "sound_texture": "akan/keskin/sıcak gibi tanımlayıcı kelime",
  "emotion_label": "kısa Türkçe duygu etiketi (örn: Huzurlu Odak, Coşkulu Enerji, Yumuşak Kaygı)",
  "description": "kısa şiirsel Türkçe açıklama"
}
Tüm değerler doğru tipte olmalı. light_frequency sayı (float) olmalı, string değil. Tüm metinler Türkçe olmalı."""

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Emotion: {emotion_input}"}
            ],
            temperature=0.8,
            timeout=30
        )
        
        content = response.choices[0].message.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        result = json.loads(content.strip())
        
        # Validate and fix types
        if isinstance(result.get('light_frequency'), str):
            result['light_frequency'] = 0.5
        
        return result
    except Exception as e:
        logging.error(f"AI CSS error: {e}")
        if language == 'en':
            return {
                "color": "#8B9DC3", "light_frequency": 0.5, "sound_texture": "flowing",
                "emotion_label": "Uncertain Wave", "description": "An internal vibration, not yet formed.",
                "error": "fallback"
            }
        else:
            return {
                "color": "#8B9DC3", "light_frequency": 0.5, "sound_texture": "akan",
                "emotion_label": "Belirsiz Dalga", "description": "İçsel bir titreşim, henüz biçimlenmemiş.",
                "error": "fallback"
            }

# Routes
@api_router.get("/")
async def root():
    return {"message": "CogitoSync v3.0 - Production", "version": "3.0.0"}

# Auth
@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(email=user_data.email, password_hash=hash_password(user_data.password))
    doc = user.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    if doc.get('premium_expires_at'):
        doc['premium_expires_at'] = doc['premium_expires_at'].isoformat()
    await db.users.insert_one(doc)
    
    token = create_access_token({"user_id": user.id, "email": user.email})
    return TokenResponse(access_token=token, user_id=user.id, email=user.email, is_premium=user.is_premium)

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    user = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if not user or not verify_password(user_data.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"user_id": user['id'], "email": user['email']})
    return TokenResponse(access_token=token, user_id=user['id'], email=user['email'], is_premium=user.get('is_premium', False))

# CSS
@api_router.post("/css/create", response_model=CSS)
async def create_css(css_input: CSSCreate, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    css_data = await generate_css_with_ai(css_input.emotion_input, css_input.language or 'tr')
    location_hash = None
    if css_input.location:
        location_hash = hash_location(css_input.location['lat'], css_input.location['lon'])
    
    css = CSS(
        user_id=current_user['id'],
        color=css_data['color'],
        light_frequency=css_data['light_frequency'],
        sound_texture=css_data['sound_texture'],
        emotion_label=css_data['emotion_label'],
        description=css_data['description'],
        location_hash=location_hash
    )
    
    doc = css.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.css_snapshots.insert_one(doc)
    
    # Update profile CSS count
    await db.profiles.update_one({"user_id": current_user['id']}, {"$inc": {"css_count": 1}})
    
    # Broadcast to WebSocket
    background_tasks.add_task(manager.broadcast, {"type": "new_css", "data": doc}, "global")
    
    return css

@api_router.get("/css/my-history")
async def get_my_history(current_user: dict = Depends(get_current_user)):
    css_list = await db.css_snapshots.find({"user_id": current_user['id']}, {"_id": 0}).sort("timestamp", -1).limit(100).to_list(100)
    return {"history": css_list}

# V3 Profile
@api_router.post("/v3/profile/create")
async def create_profile(profile_data: ProfileCreate, current_user: dict = Depends(get_current_user)):
    existing = await db.profiles.find_one({"user_id": current_user['id']}, {"_id": 0})
    if existing:
        raise HTTPException(400, "Profile exists")
    
    handle = generate_handle()
    while await db.profiles.find_one({"handle": handle}):
        handle = generate_handle()
    
    profile_id = str(uuid.uuid4())
    profile = {
        "id": profile_id, "user_id": current_user['id'], "handle": handle,
        "vibe_identity": profile_data.vibe_identity, "bio": profile_data.bio or "",
        "avatar_url": None, "followers_count": 0, "following_count": 0, "css_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.profiles.insert_one(profile)
    
    # Return profile without MongoDB's _id field
    created_profile = await db.profiles.find_one({"id": profile_id}, {"_id": 0})
    return created_profile

@api_router.get("/v3/profile/me")
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    profile = await db.profiles.find_one({"user_id": current_user['id']}, {"_id": 0})
    if not profile:
        raise HTTPException(404, "Profile not found")
    return profile

@api_router.put("/v3/profile/update")
async def update_profile(updates: ProfileUpdate, current_user: dict = Depends(get_current_user)):
    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
    if update_data:
        await db.profiles.update_one({"user_id": current_user['id']}, {"$set": update_data})
    return {"message": "Updated"}

# Social
@api_router.post("/v3/social/follow/{target_user_id}")
async def follow_user(target_user_id: str, current_user: dict = Depends(get_current_user)):
    if target_user_id == current_user['id']:
        raise HTTPException(400, "Cannot follow yourself")
    
    existing = await db.social_graph.find_one({"follower_id": current_user['id'], "following_id": target_user_id})
    if existing:
        return {"message": "Already following"}
    
    await db.social_graph.insert_one({
        "id": str(uuid.uuid4()), "follower_id": current_user['id'], "following_id": target_user_id,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    await db.profiles.update_one({"user_id": current_user['id']}, {"$inc": {"following_count": 1}})
    await db.profiles.update_one({"user_id": target_user_id}, {"$inc": {"followers_count": 1}})
    return {"message": "Followed"}

@api_router.post("/v3/social/unfollow/{target_user_id}")
async def unfollow_user(target_user_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.social_graph.delete_one({"follower_id": current_user['id'], "following_id": target_user_id})
    if result.deleted_count > 0:
        await db.profiles.update_one({"user_id": current_user['id']}, {"$inc": {"following_count": -1}})
        await db.profiles.update_one({"user_id": target_user_id}, {"$inc": {"followers_count": -1}})
    return {"message": "Unfollowed"}

@api_router.get("/v3/social/feed")
async def get_feed(limit: int = 20, current_user: dict = Depends(get_current_user)):
    following = await db.social_graph.find({"follower_id": current_user['id']}, {"following_id": 1}).to_list(100)
    following_ids = [f['following_id'] for f in following]
    
    query = {"user_id": {"$in": following_ids}} if following_ids else {}
    feed = await db.css_snapshots.find(query, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    
    for item in feed:
        profile = await db.profiles.find_one({"user_id": item['user_id']}, {"_id": 0, "handle": 1, "vibe_identity": 1, "avatar_url": 1})
        item['profile'] = profile or {}
    
    return {"feed": feed, "is_personalized": bool(following_ids)}

@api_router.get("/v3/social/global-feed")
async def get_global_feed(limit: int = 30):
    feed = await db.css_snapshots.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    for item in feed:
        profile = await db.profiles.find_one({"user_id": item['user_id']}, {"_id": 0, "handle": 1, "vibe_identity": 1})
        item['profile'] = profile or {}
    return {"feed": feed}

# AI Coach
@api_router.post("/v3/coach/start-session")
async def start_coach_session(current_user: dict = Depends(get_current_user)):
    session_id = str(uuid.uuid4())
    await db.coach_sessions.insert_one({
        "id": session_id, "user_id": current_user['id'], "messages": [],
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    return {"session_id": session_id}

@api_router.post("/v3/coach/message")
async def coach_message(msg: CoachMessage, current_user: dict = Depends(get_current_user)):
    session = await db.coach_sessions.find_one({"id": msg.session_id})
    if not session or session['user_id'] != current_user['id']:
        raise HTTPException(404, "Session not found")
    
    messages = session.get('messages', [])
    messages.append({"role": "user", "content": msg.message})
    
    language = msg.language or 'tr'
    if language == 'en':
        system_message = "You are an empathetic AI coach. Speak in English. Be supportive, understanding, and non-judgmental. Give short and concise answers. Start by validating the user's emotional state and offer small, actionable suggestions."
        error_message = "I'm having trouble connecting right now. Please try again."
    else:
        system_message = "Sen empatik bir yapay zeka koçusun. Türkçe konuş. Destekleyici, anlayışlı ve yargısız ol. Kısa ve öz cevaplar ver. Kullanıcının duygusal durumunu onaylayarak başla ve küçük, uygulanabilir öneriler sun."
        error_message = "Şu an bağlantı kurmakta zorlanıyorum. Lütfen tekrar dene."
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_message}, *messages],
            temperature=0.7, max_tokens=150
        )
        reply = response.choices[0].message.content
    except Exception as e:
        logging.error(f"Coach AI error: {e}")
        reply = error_message
    
    messages.append({"role": "assistant", "content": reply})
    await db.coach_sessions.update_one({"id": msg.session_id}, {"$set": {"messages": messages}})
    return {"reply": reply}

# Community Rooms
@api_router.get("/v3/rooms/list")
async def list_rooms(category: Optional[str] = None):
    query = {"category": category} if category else {}
    rooms = await db.community_rooms.find(query, {"_id": 0}).to_list(100)
    return {"rooms": rooms}

@api_router.get("/v3/rooms/trending")
async def trending_rooms():
    rooms = await db.community_rooms.find({"is_trending": True}, {"_id": 0}).sort("member_count", -1).limit(10).to_list(10)
    return {"rooms": rooms}

@api_router.post("/v3/rooms/{room_id}/join")
async def join_room(room_id: str, current_user: dict = Depends(get_current_user)):
    existing = await db.room_memberships.find_one({"user_id": current_user['id'], "room_id": room_id})
    if existing:
        return {"message": "Already member"}
    
    await db.room_memberships.insert_one({
        "id": str(uuid.uuid4()), "user_id": current_user['id'], "room_id": room_id,
        "joined_at": datetime.now(timezone.utc).isoformat()
    })
    await db.community_rooms.update_one({"id": room_id}, {"$inc": {"member_count": 1}})
    return {"message": "Joined"}

@api_router.post("/v3/rooms/{room_id}/leave")
async def leave_room(room_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.room_memberships.delete_one({"user_id": current_user['id'], "room_id": room_id})
    if result.deleted_count > 0:
        await db.community_rooms.update_one({"id": room_id}, {"$inc": {"member_count": -1}})
    return {"message": "Left"}

# Reactions
@api_router.post("/v3/css/react")
async def react_to_css(reaction: Reaction, current_user: dict = Depends(get_current_user)):
    await db.reactions.insert_one({
        "id": str(uuid.uuid4()), "css_id": reaction.css_id, "user_id": current_user['id'],
        "reaction_type": reaction.reaction_type, "created_at": datetime.now(timezone.utc).isoformat()
    })
    return {"message": "Reacted"}

@api_router.get("/v3/css/{css_id}/reactions")
async def get_reactions(css_id: str):
    reactions = await db.reactions.find({"css_id": css_id}, {"_id": 0}).to_list(100)
    return {"reactions": reactions, "count": len(reactions)}

# Premium
@api_router.get("/v3/premium/check")
async def check_premium(current_user: dict = Depends(get_current_user)):
    return {"is_premium": current_user.get('is_premium', False)}

@api_router.post("/v3/premium/subscribe")
async def subscribe_premium(current_user: dict = Depends(get_current_user)):
    await db.users.update_one({"id": current_user['id']}, {"$set": {
        "is_premium": True,
        "premium_expires_at": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat()
    }})
    return {"message": "Premium activated"}

# Vibe Radar - Find nearby users by vibe
@api_router.get("/v3/vibe-radar/nearby")
async def vibe_radar_nearby(current_user: dict = Depends(get_current_user), limit: int = 20):
    """Find users with similar vibes based on CSS patterns"""
    try:
        # Get current user's recent CSS
        my_css = await db.css_snapshots.find({"user_id": current_user['id']}, {"_id": 0}).sort("timestamp", -1).limit(10).to_list(10)
        
        if not my_css:
            return {"nearby": [], "message": "Create some CSS to find vibe matches"}
        
        # Calculate average light frequency as simple vibe metric
        my_avg_freq = sum([c.get('light_frequency', 0.5) for c in my_css]) / len(my_css)
        
        # Find profiles with similar vibe patterns
        all_profiles = await db.profiles.find({}, {"_id": 0}).limit(100).to_list(100)
        matches = []
        
        for profile in all_profiles:
            if profile['user_id'] == current_user['id']:
                continue
            
            # Get their recent CSS
            their_css = await db.css_snapshots.find({"user_id": profile['user_id']}, {"_id": 0}).sort("timestamp", -1).limit(10).to_list(10)
            
            if their_css:
                their_avg_freq = sum([c.get('light_frequency', 0.5) for c in their_css]) / len(their_css)
                similarity = 1 - abs(my_avg_freq - their_avg_freq)
                
                if similarity > 0.7:  # 70% similarity threshold
                    matches.append({
                        "profile": profile,
                        "similarity": round(similarity * 100, 1),
                        "recent_vibe": their_css[0].get('emotion_label', 'Unknown') if their_css else 'Unknown'
                    })
        
        # Sort by similarity
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        
        return {"nearby": matches[:limit], "count": len(matches)}
    except Exception as e:
        logging.error(f"Vibe radar error: {e}")
        return {"nearby": [], "error": "Could not fetch nearby vibes"}

# Avatar Generation
@api_router.post("/v3/avatar/generate")
async def generate_avatar(current_user: dict = Depends(get_current_user)):
    """Generate AI avatar based on user's CSS history"""
    try:
        # Get user's recent CSS
        css_list = await db.css_snapshots.find({"user_id": current_user['id']}, {"_id": 0}).sort("timestamp", -1).limit(10).to_list(10)
        
        if not css_list:
            return {"error": "Need at least one CSS to generate avatar", "avatar_url": None}
        
        # Analyze CSS patterns
        dominant_colors = [c.get('color', '#8B9DC3') for c in css_list[:3]]
        emotions = [c.get('emotion_label', '') for c in css_list[:5]]
        
        # Create prompt for DALL-E
        prompt = f"Abstract minimalist avatar representing emotional states: {', '.join(emotions[:3])}. Color palette: {', '.join(dominant_colors)}. Geometric, fluid, meditative style. No text, no face."
        
        # Generate with DALL-E
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("API key not configured")
        
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        avatar_url = response.data[0].url
        
        # Update profile with avatar
        await db.profiles.update_one(
            {"user_id": current_user['id']},
            {"$set": {"avatar_url": avatar_url}}
        )
        
        # Store in avatar history
        await db.avatar_evolutions.insert_one({
            "id": str(uuid.uuid4()),
            "user_id": current_user['id'],
            "avatar_url": avatar_url,
            "prompt": prompt,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        return {"avatar_url": avatar_url, "message": "Avatar generated"}
        
    except Exception as e:
        logging.error(f"Avatar generation error: {e}")
        return {"error": "Could not generate avatar", "avatar_url": None, "fallback": True}

@api_router.get("/v3/avatar/my")
async def get_my_avatar(current_user: dict = Depends(get_current_user)):
    """Get user's current avatar"""
    profile = await db.profiles.find_one({"user_id": current_user['id']}, {"_id": 0, "avatar_url": 1})
    if not profile:
        return {"avatar_url": None}
    return {"avatar_url": profile.get('avatar_url')}

# Mood Journal Timeline
@api_router.get("/v3/mood-journal/timeline")
async def mood_timeline(current_user: dict = Depends(get_current_user), days: int = 7):
    """Get mood timeline for the past N days"""
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        css_list = await db.css_snapshots.find(
            {
                "user_id": current_user['id'],
                "timestamp": {"$gte": cutoff_date.isoformat()}
            },
            {"_id": 0}
        ).sort("timestamp", 1).to_list(1000)
        
        # Group by day
        timeline = {}
        for css in css_list:
            date_key = css['timestamp'][:10]  # YYYY-MM-DD
            if date_key not in timeline:
                timeline[date_key] = []
            timeline[date_key].append(css)
        
        return {"timeline": timeline, "total_days": len(timeline), "total_entries": len(css_list)}
    except Exception as e:
        logging.error(f"Timeline error: {e}")
        return {"timeline": {}, "error": "Could not fetch timeline"}

# AI Coach Insights
@api_router.get("/v3/ai-coach/insights")
async def ai_coach_insights(current_user: dict = Depends(get_current_user)):
    """Get AI-generated insights from CSS history"""
    try:
        css_list = await db.css_snapshots.find({"user_id": current_user['id']}, {"_id": 0}).sort("timestamp", -1).limit(30).to_list(30)
        
        if not css_list:
            return {"insights": [], "message": "İçgörüler için daha fazla CSS oluştur"}
        
        # Analyze patterns
        emotions = [c.get('emotion_label', '') for c in css_list]
        frequencies = [c.get('light_frequency', 0.5) for c in css_list]
        avg_freq = sum(frequencies) / len(frequencies)
        
        # Generate AI insight
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("API key not configured")
        
        prompt = f"""Bu kullanıcının son duygusal örüntülerini analiz et ve 3-4 kısa, destekleyici içgörü sun. TÜRKÇE yaz.

Son duygular: {', '.join(emotions[:15])}
Ortalama yoğunluk: {avg_freq:.2f}

Duygusal örüntüleri hakkında pratik, empatik gözlemler sun. Kısa ve uygulanabilir ol. Her içgörü 1-2 cümle olsun."""

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200
        )
        
        insight_text = response.choices[0].message.content
        
        # Split into individual insights
        insights = [line.strip() for line in insight_text.split('\n') if line.strip() and len(line.strip()) > 10]
        
        return {"insights": insights, "based_on_entries": len(css_list)}
        
    except Exception as e:
        logging.error(f"AI insights error: {e}")
        return {
            "insights": [
                "Duygusal örüntülerin hakkında farkındalık geliştiriyorsun.",
                "Düzenli kontroller kendini daha iyi anlamana yardımcı oluyor.",
                "Hangi durumların seni olumlu hissettirdiğini gözlemle."
            ],
            "fallback": True
        }

# AI Mood Forecast
@api_router.get("/v3/ai-forecast/predict")
async def mood_forecast(current_user: dict = Depends(get_current_user)):
    """Predict mood trends for next 24 hours"""
    try:
        css_list = await db.css_snapshots.find({"user_id": current_user['id']}, {"_id": 0}).sort("timestamp", -1).limit(20).to_list(20)
        
        if len(css_list) < 5:
            return {"forecast": "Tahmin için en az 5 CSS kaydı gerekli", "confidence": "düşük"}
        
        # Analyze recent trends
        recent_emotions = [c.get('emotion_label', '') for c in css_list[:10]]
        frequencies = [c.get('light_frequency', 0.5) for c in css_list[:10]]
        
        # Generate forecast with AI
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("API key not configured")
        
        prompt = f"""Bu son duygusal durumlara dayanarak kısa bir 24 saatlik ruh hali tahmini sun. TÜRKÇE yaz.

Son durumlar: {', '.join(recent_emotions[:7])}

Olası duygusal eğilimler hakkında kısa, destekleyici bir tahmin (2-3 cümle) ve uygulanabilir bir öneri ver."""

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150
        )
        
        forecast_text = response.choices[0].message.content
        
        return {"forecast": forecast_text, "confidence": "medium", "based_on": len(css_list)}
        
    except Exception as e:
        logging.error(f"Forecast error: {e}")
        return {
            "forecast": "Bilinçli farkındalığına devam et. Küçük olumlu adımlar zamanla büyük etkiler yaratır.",
            "confidence": "düşük",
            "fallback": True
        }

# Room Dynamics
@api_router.get("/v3/room/{room_id}/dynamics")
async def room_dynamics(room_id: str):
    """Get collective mood dynamics for a room"""
    try:
        # Get room members
        members = await db.room_memberships.find({"room_id": room_id}, {"_id": 0, "user_id": 1}).to_list(100)
        member_ids = [m['user_id'] for m in members]
        
        if not member_ids:
            return {"dynamics": {}, "message": "No members in room"}
        
        # Get recent CSS from members
        recent_css = await db.css_snapshots.find(
            {"user_id": {"$in": member_ids}},
            {"_id": 0}
        ).sort("timestamp", -1).limit(50).to_list(50)
        
        if not recent_css:
            return {"dynamics": {}, "message": "No recent activity"}
        
        # Calculate collective metrics
        emotions = {}
        colors = []
        total_freq = 0
        
        for css in recent_css:
            emotion = css.get('emotion_label', 'Unknown')
            emotions[emotion] = emotions.get(emotion, 0) + 1
            colors.append(css.get('color', '#8B9DC3'))
            total_freq += css.get('light_frequency', 0.5)
        
        dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0] if emotions else "Mixed"
        avg_frequency = total_freq / len(recent_css) if recent_css else 0.5
        
        dynamics = {
            "dominant_emotion": dominant_emotion,
            "emotion_distribution": emotions,
            "collective_intensity": round(avg_frequency, 2),
            "active_members": len(set([c['user_id'] for c in recent_css])),
            "recent_activity_count": len(recent_css)
        }
        
        return {"dynamics": dynamics}
        
    except Exception as e:
        logging.error(f"Room dynamics error: {e}")
        return {"dynamics": {}, "error": "Could not fetch dynamics"}

# Empathy Match
@api_router.get("/v3/empathy/find-match")
async def empathy_match(current_user: dict = Depends(get_current_user)):
    """Find empathy match based on emotional resonance"""
    try:
        # Get user's recent CSS
        my_css = await db.css_snapshots.find({"user_id": current_user['id']}, {"_id": 0}).sort("timestamp", -1).limit(10).to_list(10)
        
        if len(my_css) < 3:
            return {"match": None, "message": "Need at least 3 CSS entries to find matches"}
        
        # Extract emotional signature
        my_emotions = [c.get('emotion_label', '').lower() for c in my_css]
        my_textures = [c.get('sound_texture', '').lower() for c in my_css]
        
        # Find potential matches
        all_users = await db.profiles.find({}, {"_id": 0, "user_id": 1}).limit(50).to_list(50)
        matches = []
        
        for profile in all_users:
            if profile['user_id'] == current_user['id']:
                continue
            
            their_css = await db.css_snapshots.find({"user_id": profile['user_id']}, {"_id": 0}).sort("timestamp", -1).limit(10).to_list(10)
            
            if len(their_css) < 3:
                continue
            
            their_emotions = [c.get('emotion_label', '').lower() for c in their_css]
            their_textures = [c.get('sound_texture', '').lower() for c in their_css]
            
            # Calculate emotional overlap
            emotion_overlap = len(set(my_emotions) & set(their_emotions))
            texture_overlap = len(set(my_textures) & set(their_textures))
            
            empathy_score = (emotion_overlap * 10) + (texture_overlap * 5)
            
            if empathy_score > 15:
                profile_data = await db.profiles.find_one({"user_id": profile['user_id']}, {"_id": 0})
                matches.append({
                    "profile": profile_data,
                    "empathy_score": empathy_score,
                    "shared_emotions": list(set(my_emotions) & set(their_emotions))[:3]
                })
        
        # Sort by empathy score
        matches.sort(key=lambda x: x['empathy_score'], reverse=True)
        
        best_match = matches[0] if matches else None
        
        return {"match": best_match, "total_potential_matches": len(matches)}
        
    except Exception as e:
        logging.error(f"Empathy match error: {e}")
        return {"match": None, "error": "Could not find matches"}


# WebSocket
@app.websocket("/ws/live")
async def websocket_live(websocket: WebSocket, room_id: str = "global"):
    """Enhanced WebSocket with mobile reconnection support"""
    await manager.connect(websocket, room_id)
    
    # Send initial connection confirmation
    try:
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "room_id": room_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    except:
        pass
    
    try:
        # Heartbeat mechanism for mobile stability
        last_ping = datetime.now(timezone.utc)
        
        while True:
            try:
                # Wait for message with timeout
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                
                # Handle ping/pong
                if data == "ping":
                    await websocket.send_text("pong")
                    last_ping = datetime.now(timezone.utc)
                
                # Check if client is still responsive
                if (datetime.now(timezone.utc) - last_ping).seconds > 60:
                    # Send ping to check connection
                    await websocket.send_json({"type": "ping"})
                    last_ping = datetime.now(timezone.utc)
                
            except asyncio.TimeoutError:
                # Send keep-alive ping
                try:
                    await websocket.send_json({"type": "ping"})
                    last_ping = datetime.now(timezone.utc)
                except:
                    break
            except:
                break
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logging.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket, room_id)

app.include_router(api_router)
app.add_middleware(CORSMiddleware, allow_credentials=True, allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','), allow_methods=["*"], allow_headers=["*"])

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.on_event("startup")
async def create_indexes():
    try:
        await db.users.create_index("id", unique=True)
        await db.users.create_index("email", unique=True)
        await db.profiles.create_index("user_id", unique=True)
        await db.profiles.create_index("handle", unique=True)
        await db.css_snapshots.create_index("id", unique=True)
        await db.css_snapshots.create_index([("user_id", 1), ("timestamp", -1)])
        await db.social_graph.create_index([("follower_id", 1), ("following_id", 1)], unique=True)
        await db.community_rooms.create_index("id", unique=True)
        await db.coach_sessions.create_index("user_id")
        await db.reactions.create_index("css_id")
        logging.info("Database indexes created")
    except Exception as e:
        logging.warning(f"Index creation: {e}")

@app.on_event("shutdown")
async def shutdown():
    mongo_client.close()
