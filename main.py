from aiohttp import web
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from config import PG_DSN
from typing import Callable, Awaitable
from models import Base, User, Token, Ads
from auth import hash_password, check_password

engine = create_async_engine(PG_DSN)
Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@web.middleware
async def session_middleware(request: web.Request, handler: Callable[[web.Request], Awaitable[web.Response]]):
    async with Session() as session:
        request['session'] = session
        response = await handler(request)
        # await session.commit()
        return response


async def app_context(app: web.Application):
    async with engine.begin() as conn:
        async with Session() as session:
            await session.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
            await session.commit()
        await conn.run_sync(Base.metadata.create_all)
    print('START')
    yield
    print('FINISH')
    await engine.dispose()


async def login(request: web.Request):
    return web.json_response({})


class UsersView(web.View):
    ''' GET, CREATE, PATCH, DELETE users '''

    async def get(self, user_id: int):
        return web.json_response({})

    async def post(self):
        user_data = self.request.json()
        user_data['password'] = hash_password(user_data['password'])
        new_user = User(**user_data)
        self.request['session'].add(new_user)
        await self.request['session'].commit()
        return web.json_response({
            'status': 'OK',
            'id': new_user.id
        })

    async def patch(self, user_id):
        return web.json_response({})

    async def delete(self, user_id: int):
        return web.json_response({})


my_app = web.Application(middlewares=[session_middleware])
my_app.cleanup_ctx.append(app_context)


my_app.add_routes([
    web.post('/users/', UsersView)])

if __name__ == '__main__':
    web.run_app(my_app, host='127.0.0.1', port=8080, shutdown_timeout=10.0)
