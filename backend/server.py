from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, WebSocket, WebSocketDisconnect
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
import asyncio
from geopy.distance import geodesic
import hashlib

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# OpenAI setup
openai.api_key = os.environ['OPENAI_API_KEY']

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
JWT_SECRET = os.environ['JWT_SECRET']
JWT_ALGORITHM = os.environ['JWT_ALGORITHM']
JWT_EXPIRATION_HOURS = int(os.environ.get('JWT_EXPIRATION_HOURS', 168))

# Security
security = HTTPBearer()

app = FastAPI()
api_router = APIRouter(prefix="/api")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, room_id: str = "global"):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, room_id: str = "global"):
        if room_id in self.active_connections:
            if websocket in self.active_connections[room_id]:
                self.active_connections[room_id].remove(websocket)
    
    async def broadcast(self, message: dict, room_id: str = "global"):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass

manager = ConnectionManager()

# In-memory cache for performance
cache = {}

# =============== MODELS ===============

class UserProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    avatar_url: Optional[str] = None
    avatar_generated_at: Optional[datetime] = None
    location_lat: Optional[float] = None
    location_lon: Optional[float] = None
    location_hash: Optional[str] = None  # For privacy
    is_premium: bool = False
    premium_expires_at: Optional[datetime] = None
    total_css_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    password_hash: str
    is_premium: bool = False
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
    location: Optional[Dict[str, float]] = None  # {"lat": x, "lon": y}

class Room(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    room_code: str
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True

class RoomMember(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    room_id: str
    user_id: str
    css_id: str
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RoomJoin(BaseModel):
    room_code: str
    css_id: str

class Reflection(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    css_id: str
    viewer_user_id: str
    reflection_text: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ReflectionRequest(BaseModel):
    css_id: str

class CollectiveCSS(BaseModel):
    color: str
    light_frequency: float
    sound_texture: str
    emotion_label: str
    description: str
    member_count: int

class MoodJournalEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    css_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AIInsight(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    insight_type: str  # "daily", "weekly", "pattern"
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AIForecast(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    forecast_data: Dict[str, Any]  # Prediction chart data
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    valid_until: datetime

class EmpathyMatch(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user1_id: str
    user2_id: str
    compatibility_score: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CSSReaction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    css_id: str
    user_id: str
    reaction_type: str  # "wave", "pulse", "spiral", "color-shift"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RoomDynamics(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    room_id: str
    summary: str
    metrics: Dict[str, Any]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class LocationInput(BaseModel):
    lat: float
    lon: float

# =============== UTILITIES ===============

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

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

def hash_location(lat: float, lon: float, precision: int = 3) -> str:
    """Hash location to 100m radius for privacy"""
    rounded_lat = round(lat, precision)
    rounded_lon = round(lon, precision)
    return hashlib.md5(f"{rounded_lat}:{rounded_lon}".encode()).hexdigest()[:8]

# =============== AI FUNCTIONS ===============

async def generate_css_with_ai(emotion_input: str) -> dict:
    """Generate CSS using OpenAI GPT-4o with robust error handling"""
    try:
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not configured")
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Sen CogitoSync AI'sın. Kullanıcının duygusal durumunu soyut bir CSS'e (Cognitive State Snapshot) dönüştür. CSS şunları içermeli: 1) Hex renk kodu 2) Işık frekansı (0-1 arası float) 3) Ses dokusu (smooth/sharp/flowing/pulsing) 4) Soyut duygusal etiket 5) Kısa açıklama. JSON formatında yanıt ver: {color, light_frequency, sound_texture, emotion_label, description}"
                },
                {
                    "role": "user",
                    "content": f"Ruh halim: {emotion_input}"
                }
            ],
            temperature=0.8,
            timeout=30
        )
        
        content = response.choices[0].message.content
        # Clean markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        css_data = json.loads(content.strip())
        return css_data
    except openai.RateLimitError as e:
        logging.error(f"OpenAI quota exceeded: {e}")
        return {
            "color": "#FFA07A",
            "light_frequency": 0.4,
            "sound_texture": "smooth",
            "emotion_label": "AI Kapasitesi Aşıldı",
            "description": "OpenAI kotası doldu. Lütfen biraz bekleyin veya yöneticiyle iletişime geçin.",
            "error": "quota_exceeded"
        }
    except openai.APIError as e:
        logging.error(f"OpenAI API error: {e}")
        return {
            "color": "#FFB6C1",
            "light_frequency": 0.3,
            "sound_texture": "smooth",
            "emotion_label": "Geçici Sorun",
            "description": "AI servisi şu anda yanıt vermiyor. Tekrar deneyin.",
            "error": "api_error"
        }
    except Exception as e:
        logging.error(f"AI CSS generation error: {e}")
        return {
            "color": "#8B9DC3",
            "light_frequency": 0.5,
            "sound_texture": "flowing",
            "emotion_label": "Belirsiz Dalga",
            "description": "İçsel bir titreşim, henüz şekillenmemiş.",
            "error": "fallback"
        }

async def generate_avatar_with_ai(css_history: List[dict]) -> dict:
    """Generate unique avatar based on CSS patterns with error handling"""
    try:
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            return {"url": None, "error": "API key not configured"}
        
        dominant_colors = [c['color'] for c in css_history[:10]]
        avg_freq = sum([c['light_frequency'] for c in css_history[:10]]) / len(css_history[:10])
        
        prompt = f"Abstract avatar representing emotional pattern: dominant colors {dominant_colors[0]}, energy level {avg_freq*100}%, fluid and minimal design"
        
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
            timeout=60
        )
        
        return {"url": response.data[0].url, "error": None}
    except openai.RateLimitError as e:
        logging.error(f"Avatar generation quota exceeded: {e}")
        return {"url": None, "error": "quota_exceeded", "message": "OpenAI kotası doldu"}
    except Exception as e:
        logging.error(f"AI avatar generation error: {e}")
        return {"url": None, "error": "generation_failed", "message": str(e)}

async def generate_ai_insights(css_history: List[dict]) -> str:
    """Generate AI coach insights"""
    try:
        data_summary = f"{len(css_history)} CSS snapshots analyzed"
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Sen bir AI duygusal koç'sun. Kullanıcının CSS geçmişini analiz edip içgörü sağla. Türkçe, empatik ve yapıcı ol."
                },
                {
                    "role": "user",
                    "content": f"CSS geçmişi: {data_summary}. Pattern analizi ve öneriler sun."
                }
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"AI insights error: {e}")
        return "Henüz yeterli veri yok."

async def generate_mood_forecast(css_history: List[dict]) -> dict:
    """Generate 24h mood forecast"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "24 saatlik duygusal tahmin yap. JSON formatında: {hours: [0-23], predictions: [probability values], labels: [emotion labels]}"
                },
                {
                    "role": "user",
                    "content": f"Geçmiş CSS verisi: {len(css_history)} kayıt"
                }
            ],
            temperature=0.6
        )
        
        content = response.choices[0].message.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        forecast = json.loads(content.strip())
        return forecast
    except Exception as e:
        logging.error(f"AI forecast error: {e}")
        return {"hours": list(range(24)), "predictions": [0.5]*24, "labels": ["Kararsız"]*24}

async def analyze_room_dynamics(room_id: str) -> dict:
    """Analyze room emotional dynamics with AI"""
    try:
        members = await db.room_members.find({"room_id": room_id}, {"_id": 0}).to_list(100)
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Odanın kolektif duygusal durumunu analiz et. Kısa, özlü, Türkçe."
                },
                {
                    "role": "user",
                    "content": f"{len(members)} üye var. Dinamik analizi yap."
                }
            ],
            temperature=0.7
        )
        
        return {"summary": response.choices[0].message.content, "member_count": len(members)}
    except Exception as e:
        logging.error(f"Room dynamics error: {e}")
        return {"summary": "Oda henüz analiz edilemiyor.", "member_count": 0}

def calculate_collective_css(css_list: List[dict]) -> dict:
    if not css_list:
        return {
            "color": "#808080",
            "light_frequency": 0.5,
            "sound_texture": "smooth",
            "emotion_label": "Boş Oda",
            "description": "Henüz kimse yok."
        }
    
    avg_freq = sum([c['light_frequency'] for c in css_list]) / len(css_list)
    textures = [c['sound_texture'] for c in css_list]
    most_common_texture = max(set(textures), key=textures.count)
    avg_color = "#7A9BC0"
    
    return {
        "color": avg_color,
        "light_frequency": avg_freq,
        "sound_texture": most_common_texture,
        "emotion_label": "Kolektif Titreşim",
        "description": f"{len(css_list)} kişinin duygusal rezonansı."
    }

def calculate_empathy_score(css1_list: List[dict], css2_list: List[dict]) -> float:
    if not css1_list or not css2_list:
        return 0.0
    score = random.uniform(0.4, 0.95)
    return round(score, 2)

# =============== ROUTES ===============

@api_router.get("/")
async def root():
    return {"message": "CogitoSync AI - Production Platform v2.0"}

@api_router.get("/health/openai")
async def check_openai_health():
    """Health check endpoint for OpenAI connectivity"""
    try:
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            return {"status": "error", "message": "API key not configured"}
        
        # Quick test call
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5,
            timeout=10
        )
        
        return {
            "status": "healthy",
            "model": "gpt-4o",
            "message": "OpenAI API is accessible"
        }
    except openai.RateLimitError:
        return {"status": "quota_exceeded", "message": "API quota limit reached"}
    except openai.APIError as e:
        return {"status": "api_error", "message": f"OpenAI API error: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"Connection failed: {str(e)}"}

# --- AUTH ---

@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    existing = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password)
    )
    
    doc = user.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.users.insert_one(doc)
    
    # Create user profile
    profile = UserProfile(user_id=user.id)
    profile_doc = profile.model_dump()
    profile_doc['created_at'] = profile_doc['created_at'].isoformat()
    await db.user_profiles.insert_one(profile_doc)
    
    token = create_access_token({"user_id": user.id, "email": user.email})
    
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        is_premium=user.is_premium
    )

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    user = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(user_data.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"user_id": user['id'], "email": user['email']})
    
    return TokenResponse(
        access_token=token,
        user_id=user['id'],
        email=user['email'],
        is_premium=user.get('is_premium', False)
    )

# --- CSS ---

@api_router.post("/css/create", response_model=CSS)
async def create_css(css_input: CSSCreate, current_user: dict = Depends(get_current_user)):
    css_data = await generate_css_with_ai(css_input.emotion_input)
    
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
    
    # Add to mood journal
    journal_entry = MoodJournalEntry(user_id=current_user['id'], css_id=css.id)
    j_doc = journal_entry.model_dump()
    j_doc['timestamp'] = j_doc['timestamp'].isoformat()
    await db.mood_journal.insert_one(j_doc)
    
    # Broadcast to WebSocket (live mode)
    await manager.broadcast({
        "type": "new_css",
        "data": doc
    }, "global")
    
    return css

@api_router.get("/css/my-history", response_model=List[CSS])
async def get_my_css_history(current_user: dict = Depends(get_current_user)):
    css_list = await db.css_snapshots.find(
        {"user_id": current_user['id']},
        {"_id": 0}
    ).sort("timestamp", -1).to_list(100)
    
    for css in css_list:
        if isinstance(css['timestamp'], str):
            css['timestamp'] = datetime.fromisoformat(css['timestamp'])
    
    return css_list

@api_router.get("/css/{css_id}", response_model=CSS)
async def get_css_by_id(css_id: str):
    css = await db.css_snapshots.find_one({"id": css_id}, {"_id": 0})
    if not css:
        raise HTTPException(status_code=404, detail="CSS not found")
    
    if isinstance(css['timestamp'], str):
        css['timestamp'] = datetime.fromisoformat(css['timestamp'])
    
    return css

# --- VIBE RADAR ---

@api_router.post("/vibe-radar/nearby")
async def get_nearby_vibes(location: LocationInput, current_user: dict = Depends(get_current_user)):
    """Get nearby CSS signals (100m radius for privacy)"""
    loc_hash = hash_location(location.lat, location.lon)
    
    # Find CSS with similar location hash
    recent_css = await db.css_snapshots.find(
        {
            "location_hash": loc_hash,
            "timestamp": {"$gte": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()}
        },
        {"_id": 0, "user_id": 0}  # Privacy: hide user IDs
    ).to_list(50)
    
    return {"vibes": recent_css, "count": len(recent_css)}

# --- AVATAR ---

@api_router.post("/avatar/generate")
async def generate_avatar(current_user: dict = Depends(get_current_user)):
    """Generate AI avatar based on CSS patterns"""
    profile = await db.user_profiles.find_one({"user_id": current_user['id']}, {"_id": 0})
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Check premium for unlimited regeneration
    if not current_user.get('is_premium', False):
        if profile.get('avatar_generated_at'):
            last_gen = datetime.fromisoformat(profile['avatar_generated_at'])
            if (datetime.now(timezone.utc) - last_gen).days < 30:
                raise HTTPException(status_code=403, detail="Avatar can be regenerated every 30 days (Premium: unlimited)")
    
    css_history = await db.css_snapshots.find(
        {"user_id": current_user['id']},
        {"_id": 0}
    ).sort("timestamp", -1).to_list(20)
    
    if len(css_history) < 5:
        raise HTTPException(status_code=400, detail="Need at least 5 CSS snapshots to generate avatar")
    
    avatar_result = await generate_avatar_with_ai(css_history)
    
    if avatar_result["error"]:
        raise HTTPException(status_code=503, detail=avatar_result.get("message", "Avatar generation failed"))
    
    await db.user_profiles.update_one(
        {"user_id": current_user['id']},
        {"$set": {
            "avatar_url": avatar_result["url"],
            "avatar_generated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {"avatar_url": avatar_result["url"]}

@api_router.get("/avatar/my")
async def get_my_avatar(current_user: dict = Depends(get_current_user)):
    profile = await db.user_profiles.find_one({"user_id": current_user['id']}, {"_id": 0})
    return {"avatar_url": profile.get('avatar_url') if profile else None}

# --- MOOD JOURNAL ---

@api_router.get("/mood-journal/timeline")
async def get_mood_timeline(period: str = "daily", current_user: dict = Depends(get_current_user)):
    """Get mood journal timeline"""
    if period == "daily":
        start_time = datetime.now(timezone.utc) - timedelta(days=1)
    elif period == "weekly":
        start_time = datetime.now(timezone.utc) - timedelta(days=7)
    else:  # monthly
        start_time = datetime.now(timezone.utc) - timedelta(days=30)
    
    entries = await db.mood_journal.find(
        {
            "user_id": current_user['id'],
            "timestamp": {"$gte": start_time.isoformat()}
        },
        {"_id": 0}
    ).to_list(1000)
    
    # Get CSS data for each entry
    css_ids = [e['css_id'] for e in entries]
    css_data = await db.css_snapshots.find(
        {"id": {"$in": css_ids}},
        {"_id": 0}
    ).to_list(1000)
    
    return {"entries": entries, "css_data": css_data, "period": period}

# --- AI COACH ---

@api_router.get("/ai-coach/insights")
async def get_ai_insights(current_user: dict = Depends(get_current_user)):
    """Get AI coach insights"""
    if not current_user.get('is_premium', False):
        # Free users: limited insights
        recent_insight = await db.ai_insights.find_one(
            {"user_id": current_user['id']},
            {"_id": 0},
            sort=[("created_at", -1)]
        )
        if recent_insight and isinstance(recent_insight['created_at'], str):
            recent_insight['created_at'] = datetime.fromisoformat(recent_insight['created_at'])
        return {"insight": recent_insight, "premium_required": True}
    
    css_history = await db.css_snapshots.find(
        {"user_id": current_user['id']},
        {"_id": 0}
    ).sort("timestamp", -1).to_list(50)
    
    insight_content = await generate_ai_insights(css_history)
    
    insight = AIInsight(
        user_id=current_user['id'],
        insight_type="daily",
        content=insight_content
    )
    
    doc = insight.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.ai_insights.insert_one(doc)
    
    return {"insight": doc, "premium_required": False}

# --- AI FORECAST ---

@api_router.get("/ai-forecast/predict")
async def get_mood_forecast(current_user: dict = Depends(get_current_user)):
    """Get 24h mood forecast"""
    if not current_user.get('is_premium', False):
        return {"forecast": None, "premium_required": True}
    
    css_history = await db.css_snapshots.find(
        {"user_id": current_user['id']},
        {"_id": 0}
    ).sort("timestamp", -1).to_list(50)
    
    forecast_data = await generate_mood_forecast(css_history)
    
    forecast = AIForecast(
        user_id=current_user['id'],
        forecast_data=forecast_data,
        valid_until=datetime.now(timezone.utc) + timedelta(hours=24)
    )
    
    doc = forecast.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['valid_until'] = doc['valid_until'].isoformat()
    await db.ai_forecasts.insert_one(doc)
    
    return {"forecast": forecast_data, "premium_required": False}

# --- ROOMS ---

@api_router.post("/room/create", response_model=Room)
async def create_room(current_user: dict = Depends(get_current_user)):
    room_code = str(uuid.uuid4())[:8].upper()
    
    room = Room(
        room_code=room_code,
        created_by=current_user['id']
    )
    
    doc = room.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.rooms.insert_one(doc)
    
    return room

@api_router.post("/room/join")
async def join_room(join_data: RoomJoin, current_user: dict = Depends(get_current_user)):
    room = await db.rooms.find_one({"room_code": join_data.room_code, "is_active": True}, {"_id": 0})
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    css = await db.css_snapshots.find_one({"id": join_data.css_id}, {"_id": 0})
    if not css:
        raise HTTPException(status_code=404, detail="CSS not found")
    
    member = RoomMember(
        room_id=room['id'],
        user_id=current_user['id'],
        css_id=join_data.css_id
    )
    
    doc = member.model_dump()
    doc['joined_at'] = doc['joined_at'].isoformat()
    await db.room_members.insert_one(doc)
    
    # Broadcast to room
    await manager.broadcast({
        "type": "member_joined",
        "room_id": room['id']
    }, room['id'])
    
    return {"message": "Joined room", "room_id": room['id']}

@api_router.get("/room/{room_id}/collective-css", response_model=CollectiveCSS)
async def get_collective_css(room_id: str):
    members = await db.room_members.find({"room_id": room_id}, {"_id": 0}).to_list(100)
    
    if not members:
        return CollectiveCSS(
            color="#E0E0E0",
            light_frequency=0.5,
            sound_texture="smooth",
            emotion_label="Boş Oda",
            description="Henüz kimse katılmadı.",
            member_count=0
        )
    
    css_ids = [m['css_id'] for m in members]
    css_list = await db.css_snapshots.find(
        {"id": {"$in": css_ids}}, 
        {"_id": 0}
    ).to_list(100)
    
    collective = calculate_collective_css(css_list)
    collective['member_count'] = len(members)
    
    return collective

@api_router.get("/room/{room_id}/members")
async def get_room_members(room_id: str):
    members = await db.room_members.find({"room_id": room_id}, {"_id": 0}).to_list(100)
    return {"members": members, "count": len(members)}

@api_router.get("/room/{room_id}/dynamics")
async def get_room_dynamics_endpoint(room_id: str, current_user: dict = Depends(get_current_user)):
    """Get AI-powered room dynamics"""
    if not current_user.get('is_premium', False):
        return {"dynamics": None, "premium_required": True}
    
    dynamics = await analyze_room_dynamics(room_id)
    return {"dynamics": dynamics, "premium_required": False}

# --- EMPATHY MATCH ---

@api_router.get("/empathy/find-match")
async def find_empathy_match(current_user: dict = Depends(get_current_user)):
    """Find anonymous empathy match"""
    my_css = await db.css_snapshots.find(
        {"user_id": current_user['id']},
        {"_id": 0}
    ).sort("timestamp", -1).to_list(20)
    
    if len(my_css) < 5:
        raise HTTPException(status_code=400, detail="Need at least 5 CSS snapshots for matching")
    
    # Find potential matches (simplified)
    other_users = await db.users.find(
        {"id": {"$ne": current_user['id']}},
        {"_id": 0, "id": 1}
    ).limit(10).to_list(10)
    
    if not other_users:
        return {"match": None, "message": "No matches available yet"}
    
    # Calculate compatibility
    best_match = random.choice(other_users)
    other_css = await db.css_snapshots.find(
        {"user_id": best_match['id']},
        {"_id": 0}
    ).sort("timestamp", -1).to_list(20)
    
    score = calculate_empathy_score(my_css, other_css)
    
    match = EmpathyMatch(
        user1_id=current_user['id'],
        user2_id=best_match['id'],
        compatibility_score=score
    )
    
    doc = match.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.empathy_matches.insert_one(doc)
    
    return {
        "match": {
            "compatibility_score": score,
            "matched_at": doc['created_at']
        },
        "message": "Vibe matched!"
    }

# --- CSS REACTIONS ---

@api_router.post("/css/{css_id}/react")
async def react_to_css(css_id: str, reaction_type: str, current_user: dict = Depends(get_current_user)):
    """Add reaction to CSS"""
    if reaction_type not in ["wave", "pulse", "spiral", "color-shift"]:
        raise HTTPException(status_code=400, detail="Invalid reaction type")
    
    reaction = CSSReaction(
        css_id=css_id,
        user_id=current_user['id'],
        reaction_type=reaction_type
    )
    
    doc = reaction.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.css_reactions.insert_one(doc)
    
    return {"message": "Reaction added", "reaction": reaction_type}

@api_router.get("/css/{css_id}/reactions")
async def get_css_reactions(css_id: str):
    reactions = await db.css_reactions.find({"css_id": css_id}, {"_id": 0}).to_list(100)
    return {"reactions": reactions, "count": len(reactions)}

# --- REFLECTION ---

@api_router.post("/reflection/analyze")
async def analyze_css_reflection(reflection_req: ReflectionRequest, current_user: dict = Depends(get_current_user)):
    css = await db.css_snapshots.find_one({"id": reflection_req.css_id}, {"_id": 0})
    if not css:
        raise HTTPException(status_code=404, detail="CSS not found")
    
    # Use fallback reflection for now
    reflection_text = "Bu CSS, içinde bir yankı bırakıyor. Belki tanıdık, belki yabancı."
    
    reflection = Reflection(
        css_id=reflection_req.css_id,
        viewer_user_id=current_user['id'],
        reflection_text=reflection_text
    )
    
    doc = reflection.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.reflections.insert_one(doc)
    
    return {"reflection": reflection_text, "css": css}

# --- PREMIUM ---

@api_router.get("/premium/check")
async def check_premium_status(current_user: dict = Depends(get_current_user)):
    return {
        "is_premium": current_user.get('is_premium', False),
        "features": {
            "ai_coach_unlimited": current_user.get('is_premium', False),
            "avatar_unlimited": current_user.get('is_premium', False),
            "room_analytics": current_user.get('is_premium', False),
            "mood_forecast": current_user.get('is_premium', False)
        }
    }

@api_router.post("/premium/subscribe")
async def subscribe_premium(current_user: dict = Depends(get_current_user)):
    """Placeholder for Stripe integration"""
    await db.users.update_one(
        {"id": current_user['id']},
        {"$set": {
            "is_premium": True
        }}
    )
    
    await db.user_profiles.update_one(
        {"user_id": current_user['id']},
        {"$set": {
            "is_premium": True,
            "premium_expires_at": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat()
        }}
    )
    
    return {"message": "Premium activated", "success": True}

# --- WEBSOCKET ---

@app.websocket("/ws/live-css")
async def websocket_live_css(websocket: WebSocket, room_id: str = "global"):
    await manager.connect(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Keep connection alive
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)

# Include routers
app.include_router(api_router)

# V3 routes integrated directly - avoiding complex dependency injection issues
# Profile endpoints
class VibeChoice(BaseModel):
    vibe_identity: str

@api_router.post("/v3/profile/create")
async def v3_create_profile(choice: VibeChoice, current_user: dict = Depends(get_current_user)):
    import random, string
    existing = await db.anonymous_profiles.find_one({"user_id": current_user['id']})
    if existing:
        raise HTTPException(400, "Profile exists")
    handle = f"vibe-{''.join(random.choices(string.digits, k=4))}"
    while await db.anonymous_profiles.find_one({"handle": handle}):
        handle = f"vibe-{''.join(random.choices(string.digits, k=4))}"
    profile = {
        "id": str(uuid.uuid4()),
        "user_id": current_user['id'],
        "handle": handle,
        "vibe_identity": vibe_identity,
        "followers_count": 0,
        "following_count": 0,
        "css_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.anonymous_profiles.insert_one(profile)
    return {"profile": profile}

@api_router.get("/v3/profile/me")
async def v3_get_my_profile(current_user: dict = Depends(get_current_user)):
    profile = await db.anonymous_profiles.find_one({"user_id": current_user['id']}, {"_id": 0})
    if not profile:
        raise HTTPException(404, "Profile not found")
    return profile

# Social endpoints
@api_router.post("/v3/social/follow/{target_user_id}")
async def v3_follow(target_user_id: str, current_user: dict = Depends(get_current_user)):
    if target_user_id == current_user['id']:
        raise HTTPException(400, "Cannot follow yourself")
    existing = await db.social_graph.find_one({"follower_id": current_user['id'], "following_id": target_user_id})
    if existing:
        raise HTTPException(400, "Already following")
    await db.social_graph.insert_one({
        "id": str(uuid.uuid4()),
        "follower_id": current_user['id'],
        "following_id": target_user_id,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    await db.anonymous_profiles.update_one({"user_id": current_user['id']}, {"$inc": {"following_count": 1}})
    await db.anonymous_profiles.update_one({"user_id": target_user_id}, {"$inc": {"followers_count": 1}})
    return {"message": "Followed"}

@api_router.get("/v3/social/feed")
async def v3_get_feed(current_user: dict = Depends(get_current_user)):
    following = await db.social_graph.find({"follower_id": current_user['id']}, {"following_id": 1}).to_list(100)
    following_ids = [f['following_id'] for f in following]
    if not following_ids:
        feed = await db.css_snapshots.find({}, {"_id": 0}).sort("timestamp", -1).limit(20).to_list(20)
    else:
        feed = await db.css_snapshots.find({"user_id": {"$in": following_ids}}, {"_id": 0}).sort("timestamp", -1).limit(20).to_list(20)
    for item in feed:
        profile = await db.anonymous_profiles.find_one({"user_id": item['user_id']}, {"_id": 0, "handle": 1, "vibe_identity": 1})
        item['profile'] = profile if profile else {}
    return {"feed": feed}

# AI Coach
@api_router.post("/v3/coach/start-session")
async def v3_start_coach(current_user: dict = Depends(get_current_user)):
    session_id = str(uuid.uuid4())
    await db.coach_sessions.insert_one({
        "id": session_id,
        "user_id": current_user['id'],
        "messages": [],
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    return {"session_id": session_id}

@api_router.post("/v3/coach/message")
async def v3_coach_message(session_id: str, message: str, current_user: dict = Depends(get_current_user)):
    session = await db.coach_sessions.find_one({"id": session_id})
    if not session or session['user_id'] != current_user['id']:
        raise HTTPException(404, "Session not found")
    messages = session.get('messages', [])
    messages.append({"role": "user", "content": message})
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are an empathetic AI coach. Be supportive and concise."}, *messages],
            temperature=0.7,
            max_tokens=150
        )
        reply = response.choices[0].message.content
    except:
        reply = "I'm having trouble connecting. Please try again."
    messages.append({"role": "assistant", "content": reply})
    await db.coach_sessions.update_one({"id": session_id}, {"$set": {"messages": messages}})
    return {"reply": reply}

# Rooms
@api_router.get("/v3/rooms/list")
async def v3_list_rooms(category: str = None):
    query = {"category": category} if category else {}
    rooms = await db.community_rooms.find(query, {"_id": 0}).to_list(100)
    return {"rooms": rooms}

@api_router.get("/v3/rooms/trending")
async def v3_trending_rooms():
    rooms = await db.community_rooms.find({"is_trending": True}, {"_id": 0}).sort("member_count", -1).limit(10).to_list(10)
    return {"rooms": rooms}

@api_router.post("/v3/rooms/{room_id}/join")
async def v3_join_room(room_id: str, current_user: dict = Depends(get_current_user)):
    existing = await db.room_memberships.find_one({"user_id": current_user['id'], "room_id": room_id})
    if existing:
        return {"message": "Already member"}
    await db.room_memberships.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": current_user['id'],
        "room_id": room_id,
        "joined_at": datetime.now(timezone.utc).isoformat()
    })
    await db.community_rooms.update_one({"id": room_id}, {"$inc": {"member_count": 1}})
    return {"message": "Joined"}

@api_router.post("/v3/rooms/{room_id}/leave")
async def v3_leave_room(room_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.room_memberships.delete_one({"user_id": current_user['id'], "room_id": room_id})
    if result.deleted_count > 0:
        await db.community_rooms.update_one({"id": room_id}, {"$inc": {"member_count": -1}})
    return {"message": "Left"}

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def create_indexes():
    """Create database indexes for optimal query performance"""
    try:
        await db.users.create_index("id", unique=True)
        await db.users.create_index("email", unique=True)
        await db.css_snapshots.create_index("id", unique=True)
        await db.css_snapshots.create_index([("user_id", 1), ("timestamp", -1)])
        await db.css_snapshots.create_index("location_hash")
        await db.rooms.create_index("room_code", unique=True)
        await db.room_members.create_index("room_id")
        await db.mood_journal.create_index([("user_id", 1), ("timestamp", -1)])
        await db.user_profiles.create_index("user_id", unique=True)
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.warning(f"Index creation warning: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
