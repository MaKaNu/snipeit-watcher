from typing import Literal

from pydantic import BaseModel, EmailStr


class NotificationPayload(BaseModel):
    title: str
    message: str
    recipient: EmailStr | None = None
    body_format: Literal["text", "html"] = "text"


class SnipeUser(BaseModel):
    id: int
    name: str
    username: str = ""
    email: EmailStr | None = None
    assets_count: int = 0


class SnipeUsers(BaseModel):
    total: int
    rows: list[SnipeUser]

    def apply_whitelist(self, whitelist: set[int], invert: bool = False):
        """Removes users not on whitelist. This can be inverted.

        Args:
            whitelist (set[int]): List of ids of users.
            invert (bool, optional): Determines if the function should be inverted. Defaults to False.
        """
        self.rows = [user for user in self.rows if (user.id in whitelist) ^ invert]
        self.total = len(self.rows)


class SnipeItem(BaseModel, frozen=True):
    id: int
    name: str
    type: str


class SnipeAsset(BaseModel):
    id: int
    name: str
    asset_tag: str
    assigned_to: SnipeUser | None = None

    def __hash__(self):
        return hash((self.id, self.name, self.asset_tag))


class SnipeAssets(BaseModel):
    total: int
    rows: list[SnipeAsset]


class SnipeHistory(BaseModel, frozen=True):
    id: int
    created_by: SnipeUser
    action_type: str
    item: SnipeItem


class SnipeHistories(BaseModel):
    total: int
    rows: list[SnipeHistory]

    def by_action(self, action_type: str):
        self.rows = [hist for hist in self.rows if hist.action_type == action_type]
        self.total = len(self.rows)


class AssetManager(BaseModel):
    asset_manager: SnipeUser
    assets: list[SnipeAsset]

    def __hash__(self) -> int:
        return hash(tuple(self.assets))
