import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path
import uuid

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def seed_community_rooms():
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    rooms = [
        {
            "id": str(uuid.uuid4()),
            "name": "Deep Focus Zone",
            "category": "Focus",
            "description": "For those locked in flow state",
            "member_count": 0,
            "is_trending": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Chill Lounge",
            "category": "Chill",
            "description": "Relax and unwind",
            "member_count": 0,
            "is_trending": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Overthinking Anonymous",
            "category": "Overthinking",
            "description": "For minds that never stop",
            "member_count": 0,
            "is_trending": False
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Study Grind",
            "category": "Students",
            "description": "Student vibes only",
            "member_count": 0,
            "is_trending": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Night Owls",
            "category": "Night Owls",
            "description": "3AM crew",
            "member_count": 0,
            "is_trending": False
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Creator's Corner",
            "category": "Creators",
            "description": "For artists, writers, builders",
            "member_count": 0,
            "is_trending": True
        }
    ]
    
    # Clear existing
    await db.community_rooms.delete_many({})
    
    # Insert new rooms
    await db.community_rooms.insert_many(rooms)
    print(f"✅ Seeded {len(rooms)} community rooms")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_community_rooms())
