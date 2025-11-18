from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid

# V3.0 Models

class AnonymousProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    handle: str  # @vibe-xxxx
    vibe_identity: str  # Ember, Mist, Flux, Nova, Echo, Drift, Prism
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    followers_count: int = 0
    following_count: int = 0
    css_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SocialGraph(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    follower_id: str  # user following
    following_id: str  # user being followed
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CoachSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    messages: List[Dict[str, str]] = []  # [{"role": "user/assistant", "content": "..."}]
    context_summary: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CoachMessage(BaseModel):
    session_id: str
    message: str

class CommunityRoom(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str  # Focus, Chill, Overthinking, Students, Night Owls, Creators
    description: str
    member_count: int = 0
    collective_vibe: Optional[Dict[str, Any]] = None
    is_trending: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RoomMembership(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    room_id: str
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AvatarEvolution(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    stage: int = 0
    evolution_snapshots: List[Dict[str, Any]] = []  # [{"stage": 0, "url": "...", "trigger": "..."}]
    current_avatar_url: Optional[str] = None
    last_evolved_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class FeedItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    profile_handle: str
    item_type: str  # "css", "avatar_evolution", "coach_insight"
    content: Dict[str, Any]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class VibeIdentityChoice(BaseModel):
    vibe_identity: str  # Ember, Mist, Flux, Nova, Echo, Drift, Prism

class FollowRequest(BaseModel):
    target_user_id: str
