from unittest.mock import MagicMock

from contacts_book.database.models import User
from contacts_book.conf import messages


def test_create_user(client, user, monkeypatch):
    moc_send_client = MagicMock()
    monkeypatch.setattr("contacts_book.routes.auth.send_email", moc_send_client)
    response = client.post("/api/auth/signup", json=user)
    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["user"]["email"] == user.get("email")


def test_repeat_user(client, user, monkeypatch):
    moc_send_client = MagicMock()
    monkeypatch.setattr("contacts_book.routes.auth.send_email", moc_send_client)
    response = client.post("/api/auth/signup", json=user)
    assert response.status_code == 409, response.text
    payload = response.json()
    # print("+++++++++++++", payload)
    assert payload["detail"] == messages.ACCOUNT_ALREADY_EXISTS


def test_login_user_not_confirmed_email(client, user, monkeypatch):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get("email"), "password": user.get("password")},
    )
    assert response.status_code == 401, response.text
    payload = response.json()
    # print("+++++++++++++", payload)
    assert payload["detail"] == messages.EMAIL_NOT_CONFIRMED


def test_login_user(client, user, session):
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get("email"), "password": user.get("password")},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    # print("+++++++++++++", payload)
    assert payload["token_type"] == "bearer"


def test_login_user_with_wrong_password(client, user, session):
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get("email"), "password": "password"},
    )
    assert response.status_code == 401, response.text
    payload = response.json()
    # print("+++++++++++++", payload)
    assert payload["detail"] == messages.INVALID_PASSWORD


def test_login_user_with_wrong_email(client, user, session):
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": "someemail@ex.ua", "password": user.get("password")},
    )
    assert response.status_code == 401, response.text
    payload = response.json()
    # print("+++++++++++++", payload)
    assert payload["detail"] == messages.INVALID_EMAIL

