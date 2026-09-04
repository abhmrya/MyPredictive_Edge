import asyncio

from app.services.supabase_client import AsyncSupabase
from app.modules.rbac.service import get_user_role_data


async def main():
    await AsyncSupabase.init()

    result = await get_user_role_data(
        "a09f5a2f-a9d5-4120-9875-5a23c517b520",
        "71795fa3-b01d-489b-a8aa-60f6b342116c",
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())