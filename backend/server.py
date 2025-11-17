from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import jwt
from passlib.context import CryptContext
import openai
import json
import random

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

# =============== MODELS ===============

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

class CSS(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    color: str  # hex color
    light_frequency: float  # 0-1
    sound_texture: str  # "smooth", "sharp", "flowing", "pulsing"
    emotion_label: str  # AI-generated abstract label
    description: str  # AI-generated description
    image_url: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CSSCreate(BaseModel):
    emotion_input: str  # User's current state description

class Room(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    room_code: str
    created_by: str  # user_id
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

# =============== AI FUNCTIONS ===============

async def generate_css_with_ai(emotion_input: str) -> dict:
    """Generate CSS (Cognitive State Snapshot) using OpenAI GPT-5"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",  # Will use gpt-5 when available
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
        # Parse JSON response
        css_data = json.loads(content)
        return css_data
    except Exception as e:
        logging.error(f"AI CSS generation error: {e}")
        # Fallback
        return {
            "color": "#8B9DC3",
            "light_frequency": 0.5,
            "sound_texture": "flowing",
            "emotion_label": "Belirsiz Dalga",
            "description": "İçsel bir titreşim, henüz şekillenmemiş."
        }

async def generate_reflection_with_ai(css_data: dict) -> str:
    """Generate empathic reflection using OpenAI GPT-5"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Sen CogitoSync AI'sın. Bir CSS'i (Cognitive State Snapshot) yorumla ve izleyiciye bu durumun nasıl yankılanacağını soyut ve empatik bir dille anlat. 2-3 cümle, duygusal ve şiirsel."
                },
                {
                    "role": "user",
                    "content": f"CSS: Renk {css_data['color']}, Işık Frekansı {css_data['light_frequency']}, Ses Dokusu {css_data['sound_texture']}, Etiket: {css_data['emotion_label']}, Açıklama: {css_data['description']}"
                }
            ],
            temperature=0.9
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"AI reflection error: {e}")
        return "Bu CSS, içinde bir yankı bırakıyor. Belki tanıdık, belki yabancı."

async def generate_image_with_ai(css_data: dict) -> str:
    """Generate abstract visual metaphor using OpenAI DALL-E"""
    try:
        prompt = f"Abstract visual metaphor: {css_data['emotion_label']}. Color palette: {css_data['color']}. Style: flowing light patterns, wave forms, ethereal, minimalist, digital art."
        
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        logging.error(f"AI image generation error: {e}")
        return None

def calculate_collective_css(css_list: List[dict]) -> dict:
    """Calculate collective CSS from multiple CSS snapshots"""
    if not css_list:
        return {
            "color": "#808080",
            "light_frequency": 0.5,
            "sound_texture": "smooth",
            "emotion_label": "Boş Oda",
            "description": "Henüz kimse yok."
        }
    
    # Average light frequency
    avg_freq = sum([c['light_frequency'] for c in css_list]) / len(css_list)
    
    # Most common sound texture
    textures = [c['sound_texture'] for c in css_list]
    most_common_texture = max(set(textures), key=textures.count)
    
    # Blend colors (simplified - take average RGB)
    colors = [c['color'] for c in css_list]
    avg_color = "#7A9BC0"  # Simplified collective color
    
    return {
        "color": avg_color,
        "light_frequency": avg_freq,
        "sound_texture": most_common_texture,
        "emotion_label": "Kolektif Titreşim",
        "description": f"{len(css_list)} kişinin duygusal rezonansı."
    }

# =============== ROUTES ===============

@api_router.get("/")
async def root():
    return {"message": "CogitoSync AI - Duygusal Senkronizasyon Platformu"}

# --- AUTH ---

@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    # Check if user exists
    existing = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password)
    )
    
    doc = user.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.users.insert_one(doc)
    
    # Create token
    token = create_access_token({"user_id": user.id, "email": user.email})
    
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email
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
        email=user['email']
    )

# --- CSS ---

@api_router.post("/css/create", response_model=CSS)
async def create_css(css_input: CSSCreate, current_user: dict = Depends(get_current_user)):
    # Generate CSS with AI
    css_data = await generate_css_with_ai(css_input.emotion_input)
    
    # Generate image (optional, can be async background task)
    image_url = await generate_image_with_ai(css_data)
    
    css = CSS(
        user_id=current_user['id'],
        color=css_data['color'],
        light_frequency=css_data['light_frequency'],
        sound_texture=css_data['sound_texture'],
        emotion_label=css_data['emotion_label'],
        description=css_data['description'],
        image_url=image_url
    )
    
    doc = css.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.css_snapshots.insert_one(doc)
    
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
    
    # Check if CSS exists
    css = await db.css_snapshots.find_one({"id": join_data.css_id}, {"_id": 0})
    if not css:
        raise HTTPException(status_code=404, detail="CSS not found")
    
    # Add member
    member = RoomMember(
        room_id=room['id'],
        user_id=current_user['id'],
        css_id=join_data.css_id
    )
    
    doc = member.model_dump()
    doc['joined_at'] = doc['joined_at'].isoformat()
    await db.room_members.insert_one(doc)
    
    return {"message": "Joined room", "room_id": room['id']}

@api_router.get("/room/{room_id}/collective-css", response_model=CollectiveCSS)
async def get_collective_css(room_id: str):
    members = await db.room_members.find({"room_id": room_id}, {"_id": 0}).to_list(100)
    
    # Return empty collective CSS if no members (instead of 404)
    if not members:
        return CollectiveCSS(
            color="#E0E0E0",
            light_frequency=0.5,
            sound_texture="smooth",
            emotion_label="Boş Oda",
            description="Henüz kimse katılmadı.",
            member_count=0
        )
    
    # Get all CSS snapshots
    css_ids = [m['css_id'] for m in members]
    css_list = []
    for css_id in css_ids:
        css = await db.css_snapshots.find_one({"id": css_id}, {"_id": 0})
        if css:
            css_list.append(css)
    
    collective = calculate_collective_css(css_list)
    collective['member_count'] = len(members)
    
    return collective

@api_router.get("/room/{room_id}/members")
async def get_room_members(room_id: str):
    members = await db.room_members.find({"room_id": room_id}, {"_id": 0}).to_list(100)
    return {"members": members, "count": len(members)}

# --- REFLECTION ---

@api_router.post("/reflection/analyze")
async def analyze_css_reflection(reflection_req: ReflectionRequest, current_user: dict = Depends(get_current_user)):
    css = await db.css_snapshots.find_one({"id": reflection_req.css_id}, {"_id": 0})
    if not css:
        raise HTTPException(status_code=404, detail="CSS not found")
    
    # Generate reflection with AI
    reflection_text = await generate_reflection_with_ai(css)
    
    reflection = Reflection(
        css_id=reflection_req.css_id,
        viewer_user_id=current_user['id'],
        reflection_text=reflection_text
    )
    
    doc = reflection.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.reflections.insert_one(doc)
    
    return {"reflection": reflection_text, "css": css}

# Include router
app.include_router(api_router)

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

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()