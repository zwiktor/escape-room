# from fastapi import APIRouter, Depends, HTTPException, status
# from users.manager import UserManager
# from sqlalchemy.ext.asyncio import AsyncSession
# from users.schemas import LoginRequest
# from fastapi.security import OAuth2PasswordRequestForm
#
# router = APIRouter()
#
#
# @router.post("/login", tags=["auth"])
# async def login(
#     request: OAuth2PasswordRequestForm, db: AsyncSession = Depends(get_async_session)
# ):
#     """
#     Handle login requests.
#     """
#     user_manager = UserManager()
#     user = await user_manager.authenticate(form_data)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#
#     # Generate and return the token (this assumes you have a token generation function)
#     access_token = create_access_token(data={"sub": user.email})
#     return {"access_token": access_token, "token_type": "bearer"}
