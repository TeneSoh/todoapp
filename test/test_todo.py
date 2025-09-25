# from sqlalchemy import text
# from sqlalchemy.engine import create_engine
# from sqlalchemy.pool import StaticPool
# from sqlalchemy.orm import sessionmaker
# from fastapi.testclient import TestClient
# from fastapi import status


from routers.todo import get_db, get_current_user
# from todoapp.database import Base
# from todoapp.main import app
# from todoapp.models import Todos

from .utilities import *

# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL,
#     connect_args={"check_same_thread": False},
#     poolclass=StaticPool
# )

# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base.metadata.create_all(bind=engine)

# def override_get_db():
#     db = TestingSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close() 

# def override_get_current_user():
#     return {'username':'lyonnel', 'id':1, 'role':'admin'}


app.dependency_overrides[get_db] = override_get_db 
app.dependency_overrides[get_current_user] = override_get_current_user

# client = TestClient(app)

@pytest.fixture
def test_todo():
    # car apres creation on a besoin d'une table vide
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM todos"))
        conn.commit()

    todo = Todos(
        title="test todo",
        description="description test todo",
        priority=1,
        complete=False,
        owner_id=1
    )
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    db.refresh(todo)
    yield todo
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM todos"))
        conn.commit()


# Test read all todos
def test_read_all_authenticated(test_todo):
    response = client.get("/todo/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        "title": "test todo",
        "description": "description test todo",
        "priority": 1,
        "complete": False,
        "owner_id": 1,
        'id': 1
    }]

# Test read one todo
def test_read_one_authenticated(test_todo):
    response = client.get("/todo/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "title": "test todo",
        "description": "description test todo",
        "priority": 1,
        "complete": False,
        "owner_id": 1,
        'id': 1
    }

# Test create todo
def test_create_todo_authenticated(test_todo):
    data = {
        "title": "test new todo",
        "description": "description test new todo",
        "priority": 1,
        "complete": False,
    }
    response = client.post('/todo/create-todo', json=data)
    assert response.status_code == status.HTTP_201_CREATED
    db = TestingSessionLocal()
    todo = db.query(Todos).filter(Todos.id == response.json().get('id')).first()
    assert todo.title == data.get('title') # type: ignore
    assert todo.description == data.get('description') # type: ignore
    assert todo.priority == data.get('priority') # type: ignore
    assert todo.complete is False # type: ignore
    assert todo.owner_id == 1 # type: ignore

# Test to delete todo
def test_delete_todo_authenticated(test_todo):
    response = client.delete('/todo/delete/1')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    todo = db.query(Todos).filter(Todos.id == 1).first()
    assert todo is None

def test_edit_todo_authenticate(test_todo):
    data = {
        "title": "test edited todo",
        "description": "description test edited todo",
        "priority": 1,
        "complete": False,
    }
    response = client.put("todo/todo-edit/1", json=data)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    todo = db.query(Todos).filter(Todos.id == 1).first()
    assert todo is not None
    assert todo.title == data.get('title') # type: ignore
    assert todo.description == data.get('description') # type: ignore
    assert todo.priority == data.get('priority') # type: ignore