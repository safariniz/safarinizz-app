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

def calculate_collective_css(css_list: List[dict]) -> dict:
    \"\"\"Calculate collective CSS from multiple snapshots\"\"\"\n    if not css_list:\n        return {\n            \"color\": \"#808080\",\n            \"light_frequency\": 0.5,\n            \"sound_texture\": \"smooth\",\n            \"emotion_label\": \"Boş Oda\",\n            \"description\": \"Henüz kimse yok.\"\n        }\n    \n    avg_freq = sum([c['light_frequency'] for c in css_list]) / len(css_list)\n    textures = [c['sound_texture'] for c in css_list]\n    most_common_texture = max(set(textures), key=textures.count)\n    avg_color = \"#7A9BC0\"\n    \n    return {\n        \"color\": avg_color,\n        \"light_frequency\": avg_freq,\n        \"sound_texture\": most_common_texture,\n        \"emotion_label\": \"Kolektif Titreşim\",\n        \"description\": f\"{len(css_list)} kişinin duygusal rezonansı.\"\n    }\n\ndef calculate_empathy_score(css1_list: List[dict], css2_list: List[dict]) -> float:\n    \"\"\"Calculate empathy match score between two users\"\"\"\n    if not css1_list or not css2_list:\n        return 0.0\n    \n    # Simple similarity based on color and frequency patterns\n    score = random.uniform(0.4, 0.95)  # Simplified for MVP\n    return round(score, 2)\n\n# =============== ROUTES ===============\n\n@api_router.get(\"/\")\nasync def root():\n    return {\"message\": \"CogitoSync AI - Production Platform v2.0\"}\n\n# --- AUTH ---\n\n@api_router.post(\"/auth/register\", response_model=TokenResponse)\nasync def register(user_data: UserRegister):\n    existing = await db.users.find_one({\"email\": user_data.email}, {\"_id\": 0})\n    if existing:\n        raise HTTPException(status_code=400, detail=\"Email already registered\")\n    \n    user = User(\n        email=user_data.email,\n        password_hash=hash_password(user_data.password)\n    )\n    \n    doc = user.model_dump()\n    doc['created_at'] = doc['created_at'].isoformat()\n    await db.users.insert_one(doc)\n    \n    # Create user profile\n    profile = UserProfile(user_id=user.id)\n    profile_doc = profile.model_dump()\n    profile_doc['created_at'] = profile_doc['created_at'].isoformat()\n    await db.user_profiles.insert_one(profile_doc)\n    \n    token = create_access_token({\"user_id\": user.id, \"email\": user.email})\n    \n    return TokenResponse(\n        access_token=token,\n        user_id=user.id,\n        email=user.email,\n        is_premium=user.is_premium\n    )\n\n@api_router.post(\"/auth/login\", response_model=TokenResponse)\nasync def login(user_data: UserLogin):\n    user = await db.users.find_one({\"email\": user_data.email}, {\"_id\": 0})\n    if not user:\n        raise HTTPException(status_code=401, detail=\"Invalid credentials\")\n    \n    if not verify_password(user_data.password, user['password_hash']):\n        raise HTTPException(status_code=401, detail=\"Invalid credentials\")\n    \n    token = create_access_token({\"user_id\": user['id'], \"email\": user['email']})\n    \n    return TokenResponse(\n        access_token=token,\n        user_id=user['id'],\n        email=user['email'],\n        is_premium=user.get('is_premium', False)\n    )\n\n# --- CSS ---\n\n@api_router.post(\"/css/create\", response_model=CSS)\nasync def create_css(css_input: CSSCreate, current_user: dict = Depends(get_current_user)):\n    css_data = await generate_css_with_ai(css_input.emotion_input)\n    \n    location_hash = None\n    if css_input.location:\n        location_hash = hash_location(css_input.location['lat'], css_input.location['lon'])\n    \n    css = CSS(\n        user_id=current_user['id'],\n        color=css_data['color'],\n        light_frequency=css_data['light_frequency'],\n        sound_texture=css_data['sound_texture'],\n        emotion_label=css_data['emotion_label'],\n        description=css_data['description'],\n        location_hash=location_hash\n    )\n    \n    doc = css.model_dump()\n    doc['timestamp'] = doc['timestamp'].isoformat()\n    await db.css_snapshots.insert_one(doc)\n    \n    # Add to mood journal\n    journal_entry = MoodJournalEntry(user_id=current_user['id'], css_id=css.id)\n    j_doc = journal_entry.model_dump()\n    j_doc['timestamp'] = j_doc['timestamp'].isoformat()\n    await db.mood_journal.insert_one(j_doc)\n    \n    # Broadcast to WebSocket (live mode)\n    await manager.broadcast({\n        \"type\": \"new_css\",\n        \"data\": doc\n    }, \"global\")\n    \n    return css\n\n@api_router.get(\"/css/my-history\", response_model=List[CSS])\nasync def get_my_css_history(current_user: dict = Depends(get_current_user)):\n    css_list = await db.css_snapshots.find(\n        {\"user_id\": current_user['id']},\n        {\"_id\": 0}\n    ).sort(\"timestamp\", -1).to_list(100)\n    \n    for css in css_list:\n        if isinstance(css['timestamp'], str):\n            css['timestamp'] = datetime.fromisoformat(css['timestamp'])\n    \n    return css_list\n\n@api_router.get(\"/css/{css_id}\", response_model=CSS)\nasync def get_css_by_id(css_id: str):\n    css = await db.css_snapshots.find_one({\"id\": css_id}, {\"_id\": 0})\n    if not css:\n        raise HTTPException(status_code=404, detail=\"CSS not found\")\n    \n    if isinstance(css['timestamp'], str):\n        css['timestamp'] = datetime.fromisoformat(css['timestamp'])\n    \n    return css\n\n# --- VIBE RADAR ---\n\n@api_router.post(\"/vibe-radar/nearby\")\nasync def get_nearby_vibes(location: LocationInput, current_user: dict = Depends(get_current_user)):\n    \"\"\"Get nearby CSS signals (100m radius for privacy)\"\"\"\n    loc_hash = hash_location(location.lat, location.lon)\n    \n    # Find CSS with similar location hash\n    recent_css = await db.css_snapshots.find(\n        {\n            \"location_hash\": loc_hash,\n            \"timestamp\": {\"$gte\": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()}\n        },\n        {\"_id\": 0, \"user_id\": 0}  # Privacy: hide user IDs\n    ).to_list(50)\n    \n    return {\"vibes\": recent_css, \"count\": len(recent_css)}\n\n# --- AVATAR ---\n\n@api_router.post(\"/avatar/generate\")\nasync def generate_avatar(current_user: dict = Depends(get_current_user)):\n    \"\"\"Generate AI avatar based on CSS patterns\"\"\"\n    profile = await db.user_profiles.find_one({\"user_id\": current_user['id']}, {\"_id\": 0})\n    \n    if not profile:\n        raise HTTPException(status_code=404, detail=\"Profile not found\")\n    \n    # Check premium for unlimited regeneration\n    if not current_user.get('is_premium', False):\n        if profile.get('avatar_generated_at'):\n            last_gen = datetime.fromisoformat(profile['avatar_generated_at'])\n            if (datetime.now(timezone.utc) - last_gen).days < 30:\n                raise HTTPException(status_code=403, detail=\"Avatar can be regenerated every 30 days (Premium: unlimited)\")\n    \n    css_history = await db.css_snapshots.find(\n        {\"user_id\": current_user['id']},\n        {\"_id\": 0}\n    ).sort(\"timestamp\", -1).to_list(20)\n    \n    if len(css_history) < 5:\n        raise HTTPException(status_code=400, detail=\"Need at least 5 CSS snapshots to generate avatar\")\n    \n    avatar_url = await generate_avatar_with_ai(css_history)\n    \n    await db.user_profiles.update_one(\n        {\"user_id\": current_user['id']},\n        {\"$set\": {\n            \"avatar_url\": avatar_url,\n            \"avatar_generated_at\": datetime.now(timezone.utc).isoformat()\n        }}\n    )\n    \n    return {\"avatar_url\": avatar_url}\n\n@api_router.get(\"/avatar/my\")\nasync def get_my_avatar(current_user: dict = Depends(get_current_user)):\n    profile = await db.user_profiles.find_one({\"user_id\": current_user['id']}, {\"_id\": 0})\n    return {\"avatar_url\": profile.get('avatar_url') if profile else None}\n\n# --- MOOD JOURNAL ---\n\n@api_router.get(\"/mood-journal/timeline\")\nasync def get_mood_timeline(period: str = \"daily\", current_user: dict = Depends(get_current_user)):\n    \"\"\"Get mood journal timeline\"\"\"\n    if period == \"daily\":\n        start_time = datetime.now(timezone.utc) - timedelta(days=1)\n    elif period == \"weekly\":\n        start_time = datetime.now(timezone.utc) - timedelta(days=7)\n    else:  # monthly\n        start_time = datetime.now(timezone.utc) - timedelta(days=30)\n    \n    entries = await db.mood_journal.find(\n        {\n            \"user_id\": current_user['id'],\n            \"timestamp\": {\"$gte\": start_time.isoformat()}\n        },\n        {\"_id\": 0}\n    ).to_list(1000)\n    \n    # Get CSS data for each entry\n    css_ids = [e['css_id'] for e in entries]\n    css_data = await db.css_snapshots.find(\n        {\"id\": {\"$in\": css_ids}},\n        {\"_id\": 0}\n    ).to_list(1000)\n    \n    return {\"entries\": entries, \"css_data\": css_data, \"period\": period}\n\n# --- AI COACH ---\n\n@api_router.get(\"/ai-coach/insights\")\nasync def get_ai_insights(current_user: dict = Depends(get_current_user)):\n    \"\"\"Get AI coach insights\"\"\"\n    if not current_user.get('is_premium', False):\n        # Free users: limited insights\n        recent_insight = await db.ai_insights.find_one(\n            {\"user_id\": current_user['id']},\n            {\"_id\": 0},\n            sort=[(\"created_at\", -1)]\n        )\n        if recent_insight and isinstance(recent_insight['created_at'], str):\n            recent_insight['created_at'] = datetime.fromisoformat(recent_insight['created_at'])\n        return {\"insight\": recent_insight, \"premium_required\": True}\n    \n    css_history = await db.css_snapshots.find(\n        {\"user_id\": current_user['id']},\n        {\"_id\": 0}\n    ).sort(\"timestamp\", -1).to_list(50)\n    \n    insight_content = await generate_ai_insights(css_history)\n    \n    insight = AIInsight(\n        user_id=current_user['id'],\n        insight_type=\"daily\",\n        content=insight_content\n    )\n    \n    doc = insight.model_dump()\n    doc['created_at'] = doc['created_at'].isoformat()\n    await db.ai_insights.insert_one(doc)\n    \n    return {\"insight\": doc, \"premium_required\": False}\n\n# --- AI FORECAST ---\n\n@api_router.get(\"/ai-forecast/predict\")\nasync def get_mood_forecast(current_user: dict = Depends(get_current_user)):\n    \"\"\"Get 24h mood forecast\"\"\"\n    if not current_user.get('is_premium', False):\n        return {\"forecast\": None, \"premium_required\": True}\n    \n    css_history = await db.css_snapshots.find(\n        {\"user_id\": current_user['id']},\n        {\"_id\": 0}\n    ).sort(\"timestamp\", -1).to_list(50)\n    \n    forecast_data = await generate_mood_forecast(css_history)\n    \n    forecast = AIForecast(\n        user_id=current_user['id'],\n        forecast_data=forecast_data,\n        valid_until=datetime.now(timezone.utc) + timedelta(hours=24)\n    )\n    \n    doc = forecast.model_dump()\n    doc['created_at'] = doc['created_at'].isoformat()\n    doc['valid_until'] = doc['valid_until'].isoformat()\n    await db.ai_forecasts.insert_one(doc)\n    \n    return {\"forecast\": forecast_data, \"premium_required\": False}\n\n# --- ROOMS ---\n\n@api_router.post(\"/room/create\", response_model=Room)\nasync def create_room(current_user: dict = Depends(get_current_user)):\n    room_code = str(uuid.uuid4())[:8].upper()\n    \n    room = Room(\n        room_code=room_code,\n        created_by=current_user['id']\n    )\n    \n    doc = room.model_dump()\n    doc['created_at'] = doc['created_at'].isoformat()\n    await db.rooms.insert_one(doc)\n    \n    return room\n\n@api_router.post(\"/room/join\")\nasync def join_room(join_data: RoomJoin, current_user: dict = Depends(get_current_user)):\n    room = await db.rooms.find_one({\"room_code\": join_data.room_code, \"is_active\": True}, {\"_id\": 0})\n    if not room:\n        raise HTTPException(status_code=404, detail=\"Room not found\")\n    \n    css = await db.css_snapshots.find_one({\"id\": join_data.css_id}, {\"_id\": 0})\n    if not css:\n        raise HTTPException(status_code=404, detail=\"CSS not found\")\n    \n    member = RoomMember(\n        room_id=room['id'],\n        user_id=current_user['id'],\n        css_id=join_data.css_id\n    )\n    \n    doc = member.model_dump()\n    doc['joined_at'] = doc['joined_at'].isoformat()\n    await db.room_members.insert_one(doc)\n    \n    # Broadcast to room\n    await manager.broadcast({\n        \"type\": \"member_joined\",\n        \"room_id\": room['id']\n    }, room['id'])\n    \n    return {\"message\": \"Joined room\", \"room_id\": room['id']}\n\n@api_router.get(\"/room/{room_id}/collective-css\", response_model=CollectiveCSS)\nasync def get_collective_css(room_id: str):\n    members = await db.room_members.find({\"room_id\": room_id}, {\"_id\": 0}).to_list(100)\n    \n    if not members:\n        return CollectiveCSS(\n            color=\"#E0E0E0\",\n            light_frequency=0.5,\n            sound_texture=\"smooth\",\n            emotion_label=\"Boş Oda\",\n            description=\"Henüz kimse katılmadı.\",\n            member_count=0\n        )\n    \n    css_ids = [m['css_id'] for m in members]\n    css_list = await db.css_snapshots.find(\n        {\"id\": {\"$in\": css_ids}}, \n        {\"_id\": 0}\n    ).to_list(100)\n    \n    collective = calculate_collective_css(css_list)\n    collective['member_count'] = len(members)\n    \n    return collective\n\n@api_router.get(\"/room/{room_id}/members\")\nasync def get_room_members(room_id: str):\n    members = await db.room_members.find({\"room_id\": room_id}, {\"_id\": 0}).to_list(100)\n    return {\"members\": members, \"count\": len(members)}\n\n@api_router.get(\"/room/{room_id}/dynamics\")\nasync def get_room_dynamics_endpoint(room_id: str, current_user: dict = Depends(get_current_user)):\n    \"\"\"Get AI-powered room dynamics\"\"\"\n    if not current_user.get('is_premium', False):\n        return {\"dynamics\": None, \"premium_required\": True}\n    \n    dynamics = await analyze_room_dynamics(room_id)\n    return {\"dynamics\": dynamics, \"premium_required\": False}\n\n# --- EMPATHY MATCH ---\n\n@api_router.get(\"/empathy/find-match\")\nasync def find_empathy_match(current_user: dict = Depends(get_current_user)):\n    \"\"\"Find anonymous empathy match\"\"\"\n    my_css = await db.css_snapshots.find(\n        {\"user_id\": current_user['id']},\n        {\"_id\": 0}\n    ).sort(\"timestamp\", -1).to_list(20)\n    \n    if len(my_css) < 5:\n        raise HTTPException(status_code=400, detail=\"Need at least 5 CSS snapshots for matching\")\n    \n    # Find potential matches (simplified)\n    other_users = await db.users.find(\n        {\"id\": {\"$ne\": current_user['id']}},\n        {\"_id\": 0, \"id\": 1}\n    ).limit(10).to_list(10)\n    \n    if not other_users:\n        return {\"match\": None, \"message\": \"No matches available yet\"}\n    \n    # Calculate compatibility\n    best_match = random.choice(other_users)\n    other_css = await db.css_snapshots.find(\n        {\"user_id\": best_match['id']},\n        {\"_id\": 0}\n    ).sort(\"timestamp\", -1).to_list(20)\n    \n    score = calculate_empathy_score(my_css, other_css)\n    \n    match = EmpathyMatch(\n        user1_id=current_user['id'],\n        user2_id=best_match['id'],\n        compatibility_score=score\n    )\n    \n    doc = match.model_dump()\n    doc['created_at'] = doc['created_at'].isoformat()\n    await db.empathy_matches.insert_one(doc)\n    \n    return {\n        \"match\": {\n            \"compatibility_score\": score,\n            \"matched_at\": doc['created_at']\n        },\n        \"message\": \"Vibe matched!\"\n    }\n\n# --- CSS REACTIONS ---\n\n@api_router.post(\"/css/{css_id}/react\")\nasync def react_to_css(css_id: str, reaction_type: str, current_user: dict = Depends(get_current_user)):\n    \"\"\"Add reaction to CSS\"\"\"\n    if reaction_type not in [\"wave\", \"pulse\", \"spiral\", \"color-shift\"]:\n        raise HTTPException(status_code=400, detail=\"Invalid reaction type\")\n    \n    reaction = CSSReaction(\n        css_id=css_id,\n        user_id=current_user['id'],\n        reaction_type=reaction_type\n    )\n    \n    doc = reaction.model_dump()\n    doc['timestamp'] = doc['timestamp'].isoformat()\n    await db.css_reactions.insert_one(doc)\n    \n    return {\"message\": \"Reaction added\", \"reaction\": reaction_type}\n\n@api_router.get(\"/css/{css_id}/reactions\")\nasync def get_css_reactions(css_id: str):\n    reactions = await db.css_reactions.find({\"css_id\": css_id}, {\"_id\": 0}).to_list(100)\n    return {\"reactions\": reactions, \"count\": len(reactions)}\n\n# --- REFLECTION ---\n\n@api_router.post(\"/reflection/analyze\")\nasync def analyze_css_reflection(reflection_req: ReflectionRequest, current_user: dict = Depends(get_current_user)):\n    css = await db.css_snapshots.find_one({\"id\": reflection_req.css_id}, {\"_id\": 0})\n    if not css:\n        raise HTTPException(status_code=404, detail=\"CSS not found\")\n    \n    # Use fallback reflection for now\n    reflection_text = \"Bu CSS, içinde bir yankı bırakıyor. Belki tanıdık, belki yabancı.\"\n    \n    reflection = Reflection(\n        css_id=reflection_req.css_id,\n        viewer_user_id=current_user['id'],\n        reflection_text=reflection_text\n    )\n    \n    doc = reflection.model_dump()\n    doc['timestamp'] = doc['timestamp'].isoformat()\n    await db.reflections.insert_one(doc)\n    \n    return {\"reflection\": reflection_text, \"css\": css}\n\n# --- PREMIUM ---\n\n@api_router.get(\"/premium/check\")\nasync def check_premium_status(current_user: dict = Depends(get_current_user)):\n    return {\n        \"is_premium\": current_user.get('is_premium', False),\n        \"features\": {\n            \"ai_coach_unlimited\": current_user.get('is_premium', False),\n            \"avatar_unlimited\": current_user.get('is_premium', False),\n            \"room_analytics\": current_user.get('is_premium', False),\n            \"mood_forecast\": current_user.get('is_premium', False)\n        }\n    }\n\n@api_router.post(\"/premium/subscribe\")\nasync def subscribe_premium(current_user: dict = Depends(get_current_user)):\n    \"\"\"Placeholder for Stripe integration\"\"\"\n    await db.users.update_one(\n        {\"id\": current_user['id']},\n        {\"$set\": {\n            \"is_premium\": True\n        }}\n    )\n    \n    await db.user_profiles.update_one(\n        {\"user_id\": current_user['id']},\n        {\"$set\": {\n            \"is_premium\": True,\n            \"premium_expires_at\": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat()\n        }}\n    )\n    \n    return {\"message\": \"Premium activated\", \"success\": True}\n\n# --- WEBSOCKET ---\n\n@app.websocket(\"/ws/live-css\")\nasync def websocket_live_css(websocket: WebSocket, room_id: str = \"global\"):\n    await manager.connect(websocket, room_id)\n    try:\n        while True:\n            data = await websocket.receive_text()\n            # Keep connection alive\n            await asyncio.sleep(1)\n    except WebSocketDisconnect:\n        manager.disconnect(websocket, room_id)\n\n# Include router\napp.include_router(api_router)\n\napp.add_middleware(\n    CORSMiddleware,\n    allow_credentials=True,\n    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),\n    allow_methods=[\"*\"],\n    allow_headers=[\"*\"],\n)\n\nlogging.basicConfig(\n    level=logging.INFO,\n    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'\n)\nlogger = logging.getLogger(__name__)\n\n@app.on_event(\"startup\")\nasync def create_indexes():\n    \"\"\"Create database indexes for optimal query performance\"\"\"\n    try:\n        await db.users.create_index(\"id\", unique=True)\n        await db.users.create_index(\"email\", unique=True)\n        await db.css_snapshots.create_index(\"id\", unique=True)\n        await db.css_snapshots.create_index([(\"user_id\", 1), (\"timestamp\", -1)])\n        await db.css_snapshots.create_index(\"location_hash\")\n        await db.rooms.create_index(\"room_code\", unique=True)\n        await db.room_members.create_index(\"room_id\")\n        await db.mood_journal.create_index([(\"user_id\", 1), (\"timestamp\", -1)])\n        await db.user_profiles.create_index(\"user_id\", unique=True)\n        logger.info(\"Database indexes created successfully\")\n    except Exception as e:\n        logger.warning(f\"Index creation warning: {e}\")\n\n@app.on_event(\"shutdown\")\nasync def shutdown_db_client():\n    client.close()"
