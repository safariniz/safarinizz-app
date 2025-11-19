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
            "name": "Derin Fokus Alanı",
            "category": "Fokus",
            "description": "Akış halindeki zihinler için",
            "member_count": 0,
            "is_trending": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Rahatlama Odası",
            "category": "Rahatlama",
            "description": "Gevşe ve rahatla",
            "member_count": 0,
            "is_trending": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Düşünce Durağı",
            "category": "Kaygı",
            "description": "Hiç durmayan zihinler için",
            "member_count": 0,
            "is_trending": False
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Çalışma Modu",
            "category": "Öğrenciler",
            "description": "Sadece öğrenci enerjisi",
            "member_count": 0,
            "is_trending": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Gece Kuşları",
            "category": "Gece",
            "description": "Sabahın 3'ü ekibi",
            "member_count": 0,
            "is_trending": False
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Yaratıcı Akış",
            "category": "Yaratıcılar",
            "description": "Sanatçılar, yazarlar, üretenler için",
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
