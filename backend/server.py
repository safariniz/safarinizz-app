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

class ProfileCreate(BaseModel):
    vibe_identity: str
    bio: Optional[str] = None

class ProfileUpdate(BaseModel):
    bio: Optional[str] = None
    vibe_identity: Optional[str] = None

class CoachMessage(BaseModel):
    session_id: str
    message: str

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
async def generate_css_with_ai(emotion_input: str) -> dict:
    try:
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("API key not configured")
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Generate emotional CSS as JSON: {color, light_frequency, sound_texture, emotion_label, description}"},
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
        return json.loads(content.strip())
    except Exception as e:
        logging.error(f"AI CSS error: {e}")
        return {
            "color": "#8B9DC3", "light_frequency": 0.5, "sound_texture": "flowing",
            "emotion_label": "Belirsiz Dalga", "description": "İçsel bir titreşim.",
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
    existing = await db.profiles.find_one({"user_id": current_user['id']})
    if existing:
        raise HTTPException(400, "Profile exists")
    
    handle = generate_handle()
    while await db.profiles.find_one({"handle": handle}):
        handle = generate_handle()
    
    profile = {
        "id": str(uuid.uuid4()), "user_id": current_user['id'], "handle": handle,
        "vibe_identity": profile_data.vibe_identity, "bio": profile_data.bio or "",
        "avatar_url": None, "followers_count": 0, "following_count": 0, "css_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.profiles.insert_one(profile)
    return profile

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
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are an empathetic AI coach. Be supportive."}, *messages],
            temperature=0.7, max_tokens=150
        )
        reply = response.choices[0].message.content
    except Exception as e:
        logging.error(f"Coach AI error: {e}")
        reply = "I'm having trouble connecting. Please try again."
    
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

# WebSocket
@app.websocket("/ws/live")
async def websocket_live(websocket: WebSocket, room_id: str = "global"):
    await manager.connect(websocket, room_id)
    try:
        while True:
            await websocket.receive_text()
            await asyncio.sleep(1)
    except WebSocketDisconnect:
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
    client.close()
