from motor.motor_asyncio import AsyncIOMotorClient
import config as cfg


class UserDatabase:
    """Asyncio mongo database"""
    def __init__(self):
        self.client = AsyncIOMotorClient(f"mongodb://{cfg.db_username}:{cfg.db_password}@mongodb:27017")
        # self.client = AsyncIOMotorClient("mongodb://localhost:27017")
        self.db = self.client["TelegramUsers"]
        self.users = self.db['chat_users']

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
    
    async def report_count(self, user_id: int) -> int:
        """Method return report count by user"""
        _user = await self.users.find_one({"user_id": user_id})
        return _user["reports"]

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


class PrivateUserDatabase(UserDatabase):
    """
    Private User Database Interface
    """
    def __init__(self):
        super().__init__()
        self.users = self.db['private_users']


class Rules:
    """
    Chat Rules Database
    """
    def __init__(self):
        self.client = AsyncIOMotorClient(f"mongodb://{cfg.db_username}:{cfg.db_password}@mongodb:27017")
        # self.client = AsyncIOMotorClient("mongodb://localhost:27017")
        self.db = self.client["TelegramUsers"]
        self.rules = self.db['rules']
        
    async def exists(self, chat_id: int) -> bool:
        """Method check rules for once a chat in database"""
        if await self.rules.find_one({"chat_id": chat_id}):
            return True
        return False
    
    async def get_rules(self, chat_id: int) -> dict:
        """Return rules by chat"""
        return await self.rules.find_one({"chat_id": chat_id})
    
    async def set_rules(self, rules_data: dict) -> None:
        """Creating rules for chat"""
        await self.rules.insert_one(rules_data)
        
    async def update_rules(self, chat_id: int, key: str, value: int or str) -> dict:
        """Method update rules for chat"""
        return await self.rules.update_one(
            {'chat_id': chat_id},
            {'$set': {key: value}}
        )

    async def delete_rules(self, chat_id: int) -> None:
        """Method delete userdata for once user from database"""
        await self.rules.delete_one({"chat_id": chat_id})
