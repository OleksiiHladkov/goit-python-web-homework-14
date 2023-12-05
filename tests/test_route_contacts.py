from unittest.mock import MagicMock, patch, AsyncMock

import pytest

from contacts_book.database.models import User
from contacts_book.services.auth import auth_service
from contacts_book.conf import messages


@pytest.fixture()
def token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("contacts_book.routes.auth.send_email", mock_send_email)
    client.post("/api/auth/signup", json=user)
    current_user: User = (
        session.query(User).filter(User.email == user.get("email")).first()
    )
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get("email"), "password": user.get("password")},
    )
    data = response.json()
    return data["access_token"]


def test_create_contact(client, contact, token, monkeypatch):
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
    response = client.post(
        "/api/contacts", json=contact, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["firstname"] == contact.get("firstname")
    assert "id" in data


def test_create_contact_second_time(client, contact, token, monkeypatch):
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
    response = client.post(
        "/api/contacts", json=contact, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == messages.CONTACT_ALREADY_AXISTS


def test_get_contacts(client, contact, token, monkeypatch):
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
    response = client.get("/api/contacts", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert type(data) == list
    assert data[0]["firstname"] == contact.get("firstname")


def test_get_contact(client, token, contact, monkeypatch):
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
    response = client.get(
        "/api/contacts/1", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["firstname"] == contact.get("firstname")
    assert "id" in data


def test_get_contact_not_found(client, token, monkeypatch):
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
    response = client.get(
        "/api/contacts/2", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == messages.CONTACT_NOT_FOUND


def test_update_contact(client, token, contact, monkeypatch):
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
    new_contact = contact.copy()
    new_contact["email"] = "someemail@ex.ua"
    response = client.put(
        "/api/contacts/1",
        json=new_contact,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == new_contact["email"]
    assert "id" in data


def test_update_contact_not_found(client, token, contact, monkeypatch):
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
    new_contact = contact.copy()
    new_contact["email"] = "someemail22@ex.ua"
    new_contact["phone"] = "+38066123456"
    response = client.put(
        "/api/contacts/2",
        json=new_contact,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == messages.CONTACT_NOT_FOUND


def test_delete_contact(client, token, monkeypatch):
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text


def test_repeat_delete_contact(client, token, monkeypatch):
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == messages.CONTACT_NOT_FOUND
