from pydantic import BaseModel, EmailStr


class NotificationPayload(BaseModel):
    title: str
    message: str
    recipient: EmailStr | None = None


class SnipeUser(BaseModel):
    id: int
    name: str
    username: str
    email: EmailStr | None = None
    assets_count: int = 0


class SnipeUsers(BaseModel):
    total: int
    rows: list[SnipeUser]
    current_page: int
    per_page: int
    total_pages: int
    prev_page_url: str | None = None
    next_page_url: str | None = None

    def apply_whitelist(self, whitelist: set[int], invert: bool = False):
        """Removes users not on whitelist. This can be inverted.

        Args:
            whitelist (set[int]): List of ids of users.
            invert (bool, optional): Determines if the function should be inverted. Defaults to False.
        """
        self.rows = [user for user in self.rows if (user.id in whitelist) ^ invert]
        self.total = len(self.rows)
