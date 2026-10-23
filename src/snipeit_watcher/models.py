from pydantic import BaseModel, EmailStr


class NotificationPayload(BaseModel):
    title: str
    message: str
    recipient: EmailStr | None = None


class SnipeUser(BaseModel):
    id: int
    name: str
    username: str
    assets_count: int = 0
