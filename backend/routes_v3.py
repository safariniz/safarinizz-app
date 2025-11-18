from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
import random
import string
import openai
import os
import logging
from typing import List

from models_v3 import (
    AnonymousProfile, SocialGraph, CoachSession, CoachMessage,
    CommunityRoom, RoomMembership, AvatarEvolution, FeedItem,
    VibeIdentityChoice, FollowRequest
)

v3_router = APIRouter(prefix="/v3")

# Helper functions

def generate_anonymous_handle():
    suffix = ''.join(random.choices(string.digits, k=4))
    return f"vibe-{suffix}"

async def get_user_css_history(db, user_id: str, limit: int = 20):
    css_list = await db.css_snapshots.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    return css_list

# ==================== PROFILE ENDPOINTS ====================

@v3_router.post("/profile/create")
async def create_profile(vibe_choice: VibeIdentityChoice, db: AsyncIOMotorDatabase, current_user: dict):
    """Create anonymous profile with vibe identity"""
    # Check if profile exists
    existing = await db.anonymous_profiles.find_one({"user_id": current_user['id']}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists")
    
    handle = generate_anonymous_handle()
    
    # Check handle uniqueness
    while await db.anonymous_profiles.find_one({"handle": handle}):
        handle = generate_anonymous_handle()
    
    profile = AnonymousProfile(
        user_id=current_user['id'],
        handle=handle,
        vibe_identity=vibe_choice.vibe_identity
    )
    
    doc = profile.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.anonymous_profiles.insert_one(doc)
    
    return {"profile": doc, "message": "Profile created"}

@v3_router.get("/profile/me")
async def get_my_profile(db: AsyncIOMotorDatabase, current_user: dict):
    """Get current user's profile"""
    profile = await db.anonymous_profiles.find_one({"user_id": current_user['id']}, {"_id": 0})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@v3_router.get("/profile/{user_id}")
async def get_user_profile(user_id: str, db: AsyncIOMotorDatabase):
    """Get any user's public profile"""
    profile = await db.anonymous_profiles.find_one({"user_id": user_id}, {"_id": 0})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@v3_router.put("/profile/update")
async def update_profile(update_data: dict, db: AsyncIOMotorDatabase, current_user: dict):
    """Update profile (bio, vibe_identity)"""
    allowed_fields = ["bio", "vibe_identity"]
    update_fields = {k: v for k, v in update_data.items() if k in allowed_fields}
    update_fields["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.anonymous_profiles.update_one(
        {"user_id": current_user['id']},
        {"$set": update_fields}
    )
    return {"message": "Profile updated"}

# ==================== SOCIAL ENDPOINTS ====================

@v3_router.post("/social/follow")
async def follow_user(follow_req: FollowRequest, db: AsyncIOMotorDatabase, current_user: dict):
    """Follow another user"""
    if follow_req.target_user_id == current_user['id']:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    
    # Check if already following
    existing = await db.social_graph.find_one({
        "follower_id": current_user['id'],
        "following_id": follow_req.target_user_id
    })
    if existing:
        raise HTTPException(status_code=400, detail="Already following")
    
    # Create follow relationship
    follow = SocialGraph(
        follower_id=current_user['id'],
        following_id=follow_req.target_user_id
    )
    doc = follow.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.social_graph.insert_one(doc)
    
    # Update counts
    await db.anonymous_profiles.update_one(
        {"user_id": current_user['id']},
        {"$inc": {"following_count": 1}}
    )
    await db.anonymous_profiles.update_one(
        {"user_id": follow_req.target_user_id},
        {"$inc": {"followers_count": 1}}
    )
    
    return {"message": "Followed successfully"}

@v3_router.post("/social/unfollow")
async def unfollow_user(follow_req: FollowRequest, db: AsyncIOMotorDatabase, current_user: dict):
    """Unfollow a user"""
    result = await db.social_graph.delete_one({
        "follower_id": current_user['id'],
        "following_id": follow_req.target_user_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not following this user")
    
    # Update counts
    await db.anonymous_profiles.update_one(
        {"user_id": current_user['id']},
        {"$inc": {"following_count": -1}}
    )
    await db.anonymous_profiles.update_one(
        {"user_id": follow_req.target_user_id},
        {"$inc": {"followers_count": -1}}
    )
    
    return {"message": "Unfollowed successfully"}

@v3_router.get("/social/feed")
async def get_personalized_feed(db: AsyncIOMotorDatabase, current_user: dict, limit: int = 20):
    """Get personalized feed from followed users"""
    # Get following list
    following = await db.social_graph.find(
        {"follower_id": current_user['id']},
        {"_id": 0, "following_id": 1}
    ).to_list(100)
    
    following_ids = [f['following_id'] for f in following]
    
    if not following_ids:
        # Return global feed if not following anyone
        return await get_global_feed(db, limit)
    
    # Get recent CSS from followed users
    feed_items = await db.css_snapshots.find(
        {"user_id": {"$in": following_ids}},
        {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    
    # Enrich with profile info
    for item in feed_items:
        profile = await db.anonymous_profiles.find_one(
            {"user_id": item['user_id']},
            {"_id": 0, "handle": 1, "vibe_identity": 1, "avatar_url": 1}
        )
        item['profile'] = profile if profile else {}
    
    return {"feed": feed_items, "count": len(feed_items)}

@v3_router.get("/social/global-feed")
async def get_global_feed(db: AsyncIOMotorDatabase, limit: int = 30):
    """Get global public feed"""
    feed_items = await db.css_snapshots.find(
        {},
        {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    
    # Enrich with profile info
    for item in feed_items:
        profile = await db.anonymous_profiles.find_one(
            {"user_id": item['user_id']},
            {"_id": 0, "handle": 1, "vibe_identity": 1, "avatar_url": 1}
        )
        item['profile'] = profile if profile else {}
    
    return {"feed": feed_items, "count": len(feed_items)}

@v3_router.get("/social/is-following/{target_user_id}")
async def check_following(target_user_id: str, db: AsyncIOMotorDatabase, current_user: dict):
    """Check if current user follows target"""
    existing = await db.social_graph.find_one({
        "follower_id": current_user['id'],
        "following_id": target_user_id
    })
    return {"is_following": existing is not None}

# ==================== AI COACH 2.0 ====================

@v3_router.post("/coach/start-session")
async def start_coach_session(db: AsyncIOMotorDatabase, current_user: dict):
    """Start new AI coach session"""
    session = CoachSession(
        user_id=current_user['id'],
        messages=[]
    )
    doc = session.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.coach_sessions.insert_one(doc)
    
    return {"session_id": session.id, "message": "Session started"}

@v3_router.post("/coach/message")
async def send_coach_message(msg: CoachMessage, db: AsyncIOMotorDatabase, current_user: dict):
    """Send message to AI coach"""
    session = await db.coach_sessions.find_one({"id": msg.session_id}, {"_id": 0})
    if not session or session['user_id'] != current_user['id']:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get user CSS history for context
    css_history = await get_user_css_history(db, current_user['id'], 10)
    
    # Build context
    recent_emotions = [css.get('emotion_label', '') for css in css_history[:5]]
    context = f"User recent emotional states: {', '.join(recent_emotions)}"
    
    # Add user message
    messages = session['messages']
    messages.append({"role": "user", "content": msg.message})
    
    # Call OpenAI
    try:
        api_key = os.environ.get('OPENAI_API_KEY')
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are an empathetic AI coach for CogitoSync, helping users understand their cognitive and emotional patterns. {context}. Be supportive, insightful, and concise."},
                *messages
            ],
            temperature=0.7,
            max_tokens=200
        )
        assistant_reply = response.choices[0].message.content
    except Exception as e:
        logging.error(f"Coach AI error: {e}")
        assistant_reply = "I'm having trouble connecting right now. Please try again."
    
    # Add assistant reply
    messages.append({"role": "assistant", "content": assistant_reply})
    
    # Update session
    await db.coach_sessions.update_one(
        {"id": msg.session_id},
        {
            "$set": {
                "messages": messages,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return {"reply": assistant_reply}

@v3_router.get("/coach/sessions")
async def get_coach_sessions(db: AsyncIOMotorDatabase, current_user: dict):
    """Get user's coach sessions"""
    sessions = await db.coach_sessions.find(
        {"user_id": current_user['id']},
        {"_id": 0}
    ).sort("updated_at", -1).limit(10).to_list(10)
    return {"sessions": sessions}

# ==================== COMMUNITY ROOMS 2.0 ====================

@v3_router.get("/rooms/list")
async def list_rooms(db: AsyncIOMotorDatabase, category: str = None):
    """List all community rooms, optionally filtered by category"""
    query = {}
    if category:
        query['category'] = category
    
    rooms = await db.community_rooms.find(query, {"_id": 0}).to_list(100)
    return {"rooms": rooms}

@v3_router.get("/rooms/trending")
async def get_trending_rooms(db: AsyncIOMotorDatabase):
    """Get trending rooms"""
    rooms = await db.community_rooms.find(
        {"is_trending": True},
        {"_id": 0}
    ).sort("member_count", -1).limit(10).to_list(10)
    return {"rooms": rooms}

@v3_router.post("/rooms/{room_id}/join")
async def join_community_room(room_id: str, db: AsyncIOMotorDatabase, current_user: dict):
    """Join a community room"""
    # Check if already member
    existing = await db.room_memberships.find_one({
        "user_id": current_user['id'],
        "room_id": room_id
    })
    if existing:
        return {"message": "Already a member"}
    
    membership = RoomMembership(
        user_id=current_user['id'],
        room_id=room_id
    )
    doc = membership.model_dump()
    doc['joined_at'] = doc['joined_at'].isoformat()
    await db.room_memberships.insert_one(doc)
    
    # Increment member count
    await db.community_rooms.update_one(
        {"id": room_id},
        {"$inc": {"member_count": 1}}
    )
    
    return {"message": "Joined room"}

@v3_router.post("/rooms/{room_id}/leave")
async def leave_community_room(room_id: str, db: AsyncIOMotorDatabase, current_user: dict):
    """Leave a community room"""
    result = await db.room_memberships.delete_one({
        "user_id": current_user['id'],
        "room_id": room_id
    })
    
    if result.deleted_count > 0:
        await db.community_rooms.update_one(
            {"id": room_id},
            {"$inc": {"member_count": -1}}
        )
    
    return {"message": "Left room"}

@v3_router.get("/rooms/{room_id}/members")
async def get_room_members(room_id: str, db: AsyncIOMotorDatabase):
    """Get room member list"""
    members = await db.room_memberships.find(
        {"room_id": room_id},
        {"_id": 0}
    ).to_list(100)
    
    # Enrich with profiles
    for member in members:
        profile = await db.anonymous_profiles.find_one(
            {"user_id": member['user_id']},
            {"_id": 0, "handle": 1, "vibe_identity": 1, "avatar_url": 1}
        )
        member['profile'] = profile if profile else {}
    
    return {"members": members, "count": len(members)}

# ==================== AVATAR EVOLUTION ====================

@v3_router.post("/avatar/evolve")
async def evolve_avatar(db: AsyncIOMotorDatabase, current_user: dict):
    """Trigger avatar evolution based on CSS history"""
    # Get or create evolution record
    evolution = await db.avatar_evolutions.find_one({"user_id": current_user['id']}, {"_id": 0})
    
    if not evolution:
        evolution = AvatarEvolution(user_id=current_user['id'])
        doc = evolution.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.avatar_evolutions.insert_one(doc)
    
    # Get CSS history
    css_history = await get_user_css_history(db, current_user['id'], 20)
    
    if len(css_history) < 5:
        raise HTTPException(status_code=400, detail="Need at least 5 CSS snapshots for evolution")
    
    # Analyze patterns
    avg_frequency = sum([c.get('light_frequency', 0.5) for c in css_history]) / len(css_history)
    dominant_colors = [c.get('color', '#8B9DC3') for c in css_history[:5]]
    
    # Generate evolved avatar (simplified for now)
    new_stage = evolution.get('stage', 0) + 1
    
    snapshot = {
        "stage": new_stage,
        "url": None,  # Would call DALL-E here
        "trigger": f"Evolved after {len(css_history)} CSS signals",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Update evolution
    await db.avatar_evolutions.update_one(
        {"user_id": current_user['id']},
        {
            "$set": {
                "stage": new_stage,
                "last_evolved_at": datetime.now(timezone.utc).isoformat()
            },
            "$push": {"evolution_snapshots": snapshot}
        }
    )
    
    return {"evolution": snapshot, "message": "Avatar evolved"}

@v3_router.get("/avatar/history")
async def get_avatar_history(db: AsyncIOMotorDatabase, current_user: dict):
    """Get avatar evolution history"""
    evolution = await db.avatar_evolutions.find_one({"user_id": current_user['id']}, {"_id": 0})
    if not evolution:
        return {"evolution": None, "message": "No evolution yet"}
    return evolution
