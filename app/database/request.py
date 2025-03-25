from app.database.database import async_session
from app.database.database import User
from sqlalchemy import select

async def set_user(tg_id: int, name: str, last_name: str) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        user = await session.scalar(select(User).where(User.last_name == last_name))
        user = await session.scalar(select(User).where(User.name == name))


        
        if not user:
            session.add(User(tg_id=tg_id, name=name, last_name=last_name))
            await session.commit()



    