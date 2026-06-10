import bcrypt
import pytest

from src.application.exceptions import EmailAlreadyTakenError
from src.application.usecases.register_user import RegisterUser
from tests.conftest import FakeUnitOfWork


@pytest.mark.asyncio
async def test_register_creates_user(fake_uow: FakeUnitOfWork) -> None:
    usecase = RegisterUser(fake_uow)

    user_id = await usecase.execute(
        name="Alice", email="alice@test.com", password="securepass"
    )

    assert user_id == 1
    user = await fake_uow.users.get_by_id(user_id)
    assert user is not None
    assert user.name == "Alice"
    assert user.email == "alice@test.com"
    assert fake_uow.committed


@pytest.mark.asyncio
async def test_register_hashes_password(fake_uow: FakeUnitOfWork) -> None:
    usecase = RegisterUser(fake_uow)

    user_id = await usecase.execute(
        name="Alice", email="alice@test.com", password="securepass"
    )

    user = await fake_uow.users.get_by_id(user_id)
    assert user is not None
    assert user.password != "securepass"
    assert bcrypt.checkpw(b"securepass", user.password.encode())


@pytest.mark.asyncio
async def test_register_duplicate_email_raises(fake_uow: FakeUnitOfWork) -> None:
    usecase = RegisterUser(fake_uow)
    await usecase.execute(name="Alice", email="alice@test.com", password="securepass")

    with pytest.raises(EmailAlreadyTakenError):
        await usecase.execute(name="Bob", email="alice@test.com", password="otherpass")
