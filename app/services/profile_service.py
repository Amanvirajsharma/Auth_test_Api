from app.database import db_client
from app.models import ProfileCreate, ProfileUpdate
from typing import Optional
from uuid import UUID


class ProfileService:
    """
    Profile CRUD operations
    ✔ ONLY user_id based
    ✔ 1 user = 1 profile
    ✔ email allowed (but NOT for linking)
    ✔ soft delete
    """

    def __init__(self):
        self.client = db_client
        self.table = "profiles"

    # ------------------ HELPERS ------------------
    def _convert_enums(self, data: dict) -> dict:
        for key, value in data.items():
            if hasattr(value, "value"):
                data[key] = value.value
            elif key == "date_of_birth" and value is not None:
                data[key] = str(value)
        return data

    # ------------------ CREATE ------------------
    def create_profile(
        self,
        profile_data: ProfileCreate,
        user_id: UUID
    ) -> Optional[dict]:

        # ❌ Prevent duplicate profile for same user
        existing = self.client.from_(self.table)\
            .select("id")\
            .eq("user_id", str(user_id))\
            .execute()

        if existing.data:
            raise Exception("Profile already exists for this user")

        data = profile_data.model_dump(exclude_none=True)
        data = self._convert_enums(data)

        # 🔑 ONLY LINK
        data["user_id"] = str(user_id)

        res = self.client.from_(self.table).insert(data).execute()
        return res.data[0] if res.data else None

    # ------------------ GET (BY USER) ------------------
    def get_profile_by_user_id(self, user_id: UUID) -> Optional[dict]:
        res = self.client.from_(self.table)\
            .select("*")\
            .eq("user_id", str(user_id))\
            .execute()

        return res.data[0] if res.data else None

    # ------------------ LIST ------------------
    def get_all_profiles(
        self,
        page: int = 1,
        limit: int = 10,
        is_active: Optional[bool] = None,
        role: Optional[str] = None,
        city: Optional[str] = None,
        gender: Optional[str] = None
    ) -> tuple[list, int]:

        offset = (page - 1) * limit
        query = self.client.from_(self.table).select("*", count="exact")

        if is_active is not None:
            query = query.eq("is_active", is_active)
        if role:
            query = query.eq("role", role)
        if city:
            query = query.eq("city", city)
        if gender:
            query = query.eq("gender", gender)

        res = query\
            .order("created_at", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()

        total = res.count if res.count else len(res.data)
        return res.data, total

    # ------------------ UPDATE ------------------
    def update_profile(
        self,
        user_id: UUID,
        update_data: ProfileUpdate
    ) -> Optional[dict]:

        data = update_data.model_dump(exclude_none=True)
        if not data:
            return self.get_profile_by_user_id(user_id)

        data = self._convert_enums(data)

        res = self.client.from_(self.table)\
            .update(data)\
            .eq("user_id", str(user_id))\
            .execute()

        return res.data[0] if res.data else None

    # ------------------ DELETE (SOFT) ------------------
    def delete_profile(self, user_id: UUID) -> bool:
        res = self.client.from_(self.table)\
            .update({"is_active": False})\
            .eq("user_id", str(user_id))\
            .execute()

        return len(res.data) > 0

    # ------------------ STATS ------------------
    def get_users(self, page: int = 1, limit: int = 10):
        return self.get_all_profiles(page, limit, role="user")

    def get_institutions(self, page: int = 1, limit: int = 10):
        return self.get_all_profiles(page, limit, role="institution")

    def get_role_stats(self) -> dict:
        users = self.client.from_(self.table)\
            .select("id", count="exact")\
            .eq("role", "user")\
            .execute()

        institutions = self.client.from_(self.table)\
            .select("id", count="exact")\
            .eq("role", "institution")\
            .execute()

        u = users.count or 0
        i = institutions.count or 0

        return {
            "total_users": u,
            "total_institutions": i,
            "total_profiles": u + i
        }


# Singleton
profile_service = ProfileService()
