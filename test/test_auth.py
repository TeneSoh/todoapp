from routers.auth import get_db
from .utilities import *
from passlib.context import CryptContext
from routers.auth import authenticate_user, create_access_token, create_refresh_token, get_current_user, SECRET_KEY, ALGORITHM
from datetime import timedelta
from jose import jwt
import pytest

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def test_user():
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM users"))
        conn.commit()

    user = Users(
        email="lyonnel@example.com",
        username="lyonnel",
        first_name="Lyonel",
        last_name="Messi",
        hashed_password=bcrypt_context.hash("lyonnel123"),
        role="admin",
        is_active = True
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM users"))
        conn.commit()

# Test create user
def test_create_user(test_user):
    data = {
        "email": "lyonneltest@example.com",
        "username": "Lyonnel test",
        "first_name": "Lyonnel test",
        "last_name": "Messi test",
        "password": "testlyonnel123",
        "role": "admin"
    }
    response = client.post("/auth/", json=data)
    assert response.status_code == status.HTTP_201_CREATED
    db = TestingSessionLocal()
    user = db.query(Users).filter(Users.id == response.json().get('user').get('id')).first()
    assert user is not None
    assert user.username == data.get('username') # type: ignore
    assert user.email == data.get('email') # type: ignore
    assert user.first_name == data.get('first_name') # type: ignore
    assert user.last_name == data.get('last_name') # type: ignore
    assert bcrypt_context.verify(data.get('password'), user.hashed_password) # type: ignore
    assert user.role == data.get('role') # type: ignore
    assert user.is_active is True # type: ignore

# Test login user
def test_login_user(test_user):

    # response = client.post("/auth/login/", data={"username": test_user.username, "password": "lyonnel123"})
    db = TestingSessionLocal()
    user = authenticate_user(test_user.username, "lyonnel123", db)
    assert user is not False
    assert user.username == test_user.username # type: ignore
    assert user.email == test_user.email # type: ignore
    assert user.first_name == test_user.first_name # type: ignore
    assert user.last_name == test_user.last_name # type: ignore


# Test access token creation
@pytest.mark.asyncio
async def test_create_access_token(test_user):
    username = test_user.username
    user_id = test_user.id
    expired_minutes = timedelta(minutes=30)
    access_token = await create_access_token(username, user_id, expire_minutes=30)

    decode_token = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False})
    token_exp = decode_token.get("exp")
    assert token_exp is not None
    assert decode_token.get("sub") == username
    assert decode_token.get("id") == user_id
    assert decode_token.get("scope") == "access_token"


# Test refresh token creation
@pytest.mark.asyncio
async def test_create_refresh_token(test_user):
    username = test_user.username
    user_id = test_user.id
    refresh_token = await create_refresh_token(username, user_id)

    decode_token = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False})
    token_exp = decode_token.get("exp")
    assert token_exp is not None
    assert decode_token.get("sub") == username
    assert decode_token.get("id") == user_id
    assert decode_token.get("scope") == "refresh_token"

# Test get current user
@pytest.mark.asyncio
async def test_get_current_user(test_user):
    username = test_user.username
    user_id = test_user.id
    access_token = await create_access_token(username, user_id, expire_minutes=30)
    current_user = await get_current_user(token=access_token)
    assert current_user is not None
    assert current_user.get('username') == username
    assert current_user.get('id') == user_id