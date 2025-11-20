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
            "name_en": "Deep Focus Zone",
            "category": "Fokus",
            "description": "Akış halindeki zihinler için",
            "description_en": "For minds in flow state",
            "member_count": 0,
            "is_trending": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Rahatlama Odası",
            "name_en": "Chill Lounge",
            "category": "Rahatlama",
            "description": "Gevşe ve rahatla",
            "description_en": "Relax and unwind",
            "member_count": 0,
            "is_trending": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Düşünce Durağı",
            "name_en": "Overthinking Station",
            "category": "Kaygı",
            "description": "Hiç durmayan zihinler için",
            "description_en": "For minds that never stop",
            "member_count": 0,
            "is_trending": False
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Çalışma Modu",
            "name_en": "Study Grind",
            "category": "Öğrenciler",
            "description": "Sadece öğrenci enerjisi",
            "description_en": "Pure student energy",
            "member_count": 0,
            "is_trending": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Gece Kuşları",
            "name_en": "Night Owls",
            "category": "Gece",
            "description": "Sabahın 3'ü ekibi",
            "description_en": "3 AM crew",
            "member_count": 0,
            "is_trending": False
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Yaratıcı Akış",
            "name_en": "Creators Corner",
            "category": "Yaratıcılar",
            "description": "Sanatçılar, yazarlar, üretenler için",
            "description_en": "For artists, writers, makers",
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
