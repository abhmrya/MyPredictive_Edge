import asyncio

from app.services.supabase_client import AsyncSupabase


async def main():
    client = await AsyncSupabase.init()

    response = await client.auth.sign_in_with_password(
        {
            "email": "abhaymaurya54321@gmail.com",
            "password": "admin",
        }
    )

    if response.session:
        print("LOGIN SUCCESS")
        print("USER ID:", response.user.id)
        print("EMAIL:", response.user.email)
        print("ACCESS TOKEN:")
        print(response.session.access_token)
    else:
        print("LOGIN FAILED")


asyncio.run(main())