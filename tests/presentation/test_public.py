from httpx import AsyncClient


async def test_register_success(client: AsyncClient) -> None:
    resp = await client.post(
        "/auth/register",
        json={"name": "Alice", "email": "alice@test.com", "password": "password123"},
    )

    assert resp.status_code == 201
    assert resp.json()["user_id"] == 1


async def test_register_duplicate_email(client: AsyncClient) -> None:
    await client.post(
        "/auth/register",
        json={"name": "Alice", "email": "alice@test.com", "password": "password123"},
    )
    resp = await client.post(
        "/auth/register",
        json={"name": "Bob", "email": "alice@test.com", "password": "password123"},
    )

    assert resp.status_code == 409
    assert resp.json()["detail"] == "Email already taken"


async def test_register_short_password(client: AsyncClient) -> None:
    resp = await client.post(
        "/auth/register",
        json={"name": "Alice", "email": "alice@test.com", "password": "short"},
    )

    assert resp.status_code == 422


async def test_login_success(client: AsyncClient) -> None:
    await client.post(
        "/auth/register",
        json={"name": "Alice", "email": "alice@test.com", "password": "password123"},
    )
    resp = await client.post(
        "/auth/login",
        json={"email": "alice@test.com", "password": "password123"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_credentials(client: AsyncClient) -> None:
    await client.post(
        "/auth/register",
        json={"name": "Alice", "email": "alice@test.com", "password": "password123"},
    )
    resp = await client.post(
        "/auth/login",
        json={"email": "alice@test.com", "password": "wrongpass"},
    )

    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid credentials"


async def test_login_nonexistent_email(client: AsyncClient) -> None:
    resp = await client.post(
        "/auth/login",
        json={"email": "nobody@test.com", "password": "password123"},
    )

    assert resp.status_code == 401


async def test_refresh_success(client: AsyncClient) -> None:
    await client.post(
        "/auth/register",
        json={"name": "Alice", "email": "alice@test.com", "password": "password123"},
    )
    login_resp = await client.post(
        "/auth/login",
        json={"email": "alice@test.com", "password": "password123"},
    )
    refresh_token = login_resp.json()["refresh_token"]

    resp = await client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


async def test_refresh_with_invalid_token(client: AsyncClient) -> None:
    resp = await client.post(
        "/auth/refresh",
        json={"refresh_token": "garbage"},
    )

    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid or expired refresh token"


async def test_refresh_with_access_token(client: AsyncClient) -> None:
    await client.post(
        "/auth/register",
        json={"name": "Alice", "email": "alice@test.com", "password": "password123"},
    )
    login_resp = await client.post(
        "/auth/login",
        json={"email": "alice@test.com", "password": "password123"},
    )
    access_token = login_resp.json()["access_token"]

    resp = await client.post(
        "/auth/refresh",
        json={"refresh_token": access_token},
    )

    assert resp.status_code == 401


async def test_users_me_success(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    resp = await client.get("/auth/users/me", headers=auth_headers)

    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Auth User"
    assert data["email"] == "auth@test.com"


async def test_users_me_no_token(client: AsyncClient) -> None:
    resp = await client.get("/auth/users/me")

    assert resp.status_code == 401


async def test_users_me_invalid_token(client: AsyncClient) -> None:
    resp = await client.get(
        "/auth/users/me",
        headers={"Authorization": "Bearer invalid"},
    )

    assert resp.status_code == 401


async def test_users_me_refresh_token_rejected(client: AsyncClient) -> None:
    await client.post(
        "/auth/register",
        json={"name": "Alice", "email": "alice@test.com", "password": "password123"},
    )
    login_resp = await client.post(
        "/auth/login",
        json={"email": "alice@test.com", "password": "password123"},
    )
    refresh_token = login_resp.json()["refresh_token"]

    resp = await client.get(
        "/auth/users/me",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )

    assert resp.status_code == 401
