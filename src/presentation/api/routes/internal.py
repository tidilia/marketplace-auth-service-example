from fastapi import APIRouter, HTTPException, Response, status

from src.application.exceptions import UserNotFoundError
from src.presentation.api.dependencies import DeleteUserDep, GetUserDep
from src.presentation.api.schemas import UserResponse

router = APIRouter(prefix="/internal", tags=["internal"])


@router.get("/users/{user_id}")
async def get_user(user_id: int, usecase: GetUserDep) -> UserResponse:
    try:
        user = await usecase.execute(user_id)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return UserResponse(user_id=user.id, name=user.name, email=user.email)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, usecase: DeleteUserDep) -> Response:
    try:
        await usecase.execute(user_id)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
