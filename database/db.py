from motor.motor_asyncio import AsyncIOMotorClient
from config import config as cfg
from utils import structs


class UserDatabase:
    """Asyncio mongo database"""

    def __init__(self, collection_name: structs.CollectionName):
        self.client = AsyncIOMotorClient(
            f"mongodb://{cfg.db_username}:{cfg.db_password}@127.0.0.1:27017"
        )
        self.db = self.client["TelegramUsers"]
        self.users = self.db[collection_name]

    async def get_one(self, user_id: int) -> dict:
        """Return userdata for once user"""

        result = await self.users.find_one({"user_id": user_id})
        return result

    async def get_all(self) -> AsyncIOMotorClient:
        """Return userdata for all users"""

        return self.users.find({})

    async def exists(self, user_id: int) -> bool:
        """Method check user for exists in database"""

        return True if await self.users.find_one({"user_id": user_id}) else False

    async def report_count(self, user_id: int) -> int:
        """Method return report count by user"""

        _user = await self.users.find_one({"user_id": user_id})
        return _user["reports"]

    async def insert_private_user(
        self, user_data: structs.NewPrivateUserStruct
    ) -> None:
        """Method creating new user in database"""

        _user_data = {"user_id": user_data.user_id, "username": user_data.username}
        await self.users.insert_one(_user_data)

    async def insert_user(self, user_data: structs.NewUserStruct) -> None:
        """Method creating newprivate user in database"""

        _user_data = {
            "user_id": user_data.user_id,
            "username": user_data.username,
            "chat_id": user_data.chat_id,
            "chat_title": user_data.chat_title,
            "chat_username": user_data.chat_username,
        }
        await self.users.insert_one(_user_data)

    async def update_one(self, user_id: int, key: str, value: int or str) -> dict:
        """Method update userdata for ince user"""

        return await self.users.update_one({"user_id": user_id}, {"$set": {key: value}})

    async def delete_one(self, user_id: int) -> None:
        """Method delete userdata for once user from database"""

        await self.users.delete_one({"user_id": user_id})

    @staticmethod
    async def init_users_db() -> "UserDatabase":
        """Initiate users database"""

        return UserDatabase(structs.CollectionName.users)

    @staticmethod
    async def init_private_db() -> "UserDatabase":
        """Initiate users database"""

        return UserDatabase(structs.CollectionName.private_users)


class Rules:
    """
    Chat Rules Database
    """

    def __init__(self):
        self.client = AsyncIOMotorClient(
            f"mongodb://{cfg.db_username}:{cfg.db_password}@127.0.0.1:27017"
        )
        self.db = self.client["TelegramUsers"]
        self.rules = self.db["rules"]

    async def exists(self, chat_id: int) -> bool:
        """Method check rules for once a chat in database"""

        return True if await self.rules.find_one({"chat_id": chat_id}) else False

    async def get_rules(self, chat_id: int) -> structs.RulesInfo:
        """Return rules by chat"""

        _rules = await self.rules.find_one({"chat_id": chat_id})
        return structs.RulesInfo(chat_id=_rules["chat_id"], rules=_rules["rules"])

    async def set_rules(self, rules_data: structs.RulesInfo) -> None:
        """Creating rules for chat"""

        _rules_data = {"chat_id": rules_data.chat_id, "rules": rules_data.rules}
        await self.rules.insert_one(_rules_data)

    async def delete_rules(self, chat_id: int) -> None:
        """Method delete userdata for once user from database"""

        await self.rules.delete_one({"chat_id": chat_id})
