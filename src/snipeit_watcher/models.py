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


class SnipeUsers(BaseModel):
    total: int
    rows: list[SnipeUser]
    current_page: int
    per_page: int
    total_pages: int
    prev_page_url: str | None = None
    next_page_url: str | None = None
