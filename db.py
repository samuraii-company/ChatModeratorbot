from motor.motor_asyncio import AsyncIOMotorClient


class Database:
    """Asyncio mongo database"""
    def __init__(self):
        self.client = AsyncIOMotorClient('mongodb://localhost:27017')
        self.db = self.client["TelegramUsers"]
        self.users = self.db['users']

    async def get_one(self, user_id: int) -> dict:
        """Return userdata for once user"""
        result = await self.users.find_one({"user_id": user_id})
        return result

    async def get_all(self) -> AsyncIOMotorClient:
        """Return userdata for all users"""
        return self.users.find({})

    async def exists(self, user_id: int) -> bool:
        """Method check user for exists in database"""
        if await self.users.find_one({"user_id": user_id}):
            return True
        return False

    async def insert_one(self, user_data: dict) -> None:
        """Method creating new user in database"""
        await self.users.insert_one(user_data)

    async def update_one(self, user_id: int, key: str, value: int or str) -> dict:
        """Method update userdata for ince user"""
        return await self.users.update_one(
            {'user_id': user_id},
            {'$set': {key: value}}
        )

    async def delete_one(self, user_id: int) -> None:
        """Method delete userdata for once user from database"""
        await self.users.delete_one({"user_id": user_id})
