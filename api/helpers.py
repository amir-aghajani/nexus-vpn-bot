from fastapi import Header, HTTPException, status


async def login_required(authorization: str = Header(None, alias="Authorization", alias_priority=1)):
    if authorization is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="AUTHORIZATION_HEADER_MISSING")

    return True
