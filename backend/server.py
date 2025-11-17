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
    """Generate CSS using OpenAI GPT-4o"""
    try:
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
            temperature=0.8
        )
        
        content = response.choices[0].message.content
        css_data = json.loads(content)
        return css_data
    except Exception as e:
        logging.error(f"AI CSS generation error: {e}")
        return {
            "color": "#8B9DC3",
            "light_frequency": 0.5,
            "sound_texture": "flowing",
            "emotion_label": "Belirsiz Dalga",
            "description": "İçsel bir titreşim, henüz şekillenmemiş."
        }

async def generate_avatar_with_ai(css_history: List[dict]) -> str:
    """Generate unique avatar based on CSS patterns"""
    try:
        # Analyze pattern
        dominant_colors = [c['color'] for c in css_history[:10]]
        avg_freq = sum([c['light_frequency'] for c in css_history[:10]]) / len(css_history[:10])
        
        prompt = f"Abstract avatar representing emotional pattern: dominant colors {dominant_colors[0]}, energy level {avg_freq*100}%, fluid and minimal design"
        
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        return response.data[0].url
    except Exception as e:
        logging.error(f"AI avatar generation error: {e}")
        return None

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
        
        forecast = json.loads(response.choices[0].message.content)
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

# ... [REST OF SERVER.PY CODE WILL CONTINUE IN NEXT FILE]
