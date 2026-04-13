"""用户认证路由"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models_user import User, UserSession
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
    generate_password_reset_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.schemas import UserLogin, UserRegister, UserResponse, TokenResponse
from app.exceptions import AppException

router = APIRouter(prefix="/api/auth", tags=["认证"])
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """获取当前登录用户"""
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌中缺少用户ID",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查手机号是否已存在
    existing_user = db.query(User).filter(User.phone == user_data.phone).first()
    if existing_user:
        raise AppException("PHONE_ALREADY_EXISTS", "该手机号已注册")

    # 创建新用户
    hashed_password = hash_password(user_data.password)
    user = User(
        phone=user_data.phone,
        password_hash=hashed_password,
        nickname=user_data.nickname
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse(
        id=user.id,
        phone=user.phone,
        nickname=user.nickname,
        email=user.email,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at
    )


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    # 查找用户
    user = db.query(User).filter(User.phone == user_data.phone).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise AppException("INVALID_CREDENTIALS", "手机号或密码错误")

    if not user.is_active:
        raise AppException("USER_DISABLED", "账号已被禁用")

    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    # 记录会话
    user_session = UserSession(
        user_id=user.id,
        session_token=access_token,
        expires_at=datetime.utcnow() + access_token_expires,
        device_info={"login_time": datetime.utcnow().isoformat()}
    )
    db.add(user_session)
    db.commit()

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """用户登出"""
    token = credentials.credentials
    payload = verify_token(token)
    if payload:
        user_id = payload.get("sub")
        # 标记会话为已过期（简单处理，实际应该记录登出时间）
        db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.expires_at > datetime.utcnow()
        ).update({"expires_at": datetime.utcnow()})
        db.commit()

    return {"message": "已成功登出"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserResponse(
        id=current_user.id,
        phone=current_user.phone,
        nickname=current_user.nickname,
        email=current_user.email,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at
    )


@router.post("/request-password-reset")
async def request_password_reset(phone: str, db: Session = Depends(get_db)):
    """请求密码重置"""
    user = db.query(User).filter(User.phone == phone).first()
    if not user:
        raise AppException("USER_NOT_FOUND", "该手机号未注册")

    # 生成重置令牌
    reset_token = generate_password_reset_token()
    expires_at = datetime.utcnow() + timedelta(hours=1)  # 1小时后过期

    # 保存令牌
    from app.models_user import PasswordResetToken
    reset_token_record = PasswordResetToken(
        user_id=user.id,
        token=reset_token,
        expires_at=expires_at
    )
    db.add(reset_token_record)
    db.commit()

    # TODO: 这里应该发送短信验证码，暂时返回令牌用于测试
    # 实际项目中应该调用短信API发送重置链接
    return {"message": "密码重置令牌已生成", "reset_token": reset_token}


@router.post("/reset-password")
async def reset_password(
    phone: str,
    new_password: str,
    reset_token: str,
    db: Session = Depends(get_db)
):
    """重置密码"""
    # 验证令牌
    from app.models_user import PasswordResetToken
    token_record = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == reset_token,
        PasswordResetToken.expires_at > datetime.utcnow(),
        PasswordResetToken.is_used == False
    ).first()

    if not token_record:
        raise AppException("INVALID_TOKEN", "重置令牌无效或已过期")

    # 验证手机号
    user = db.query(User).filter(User.id == token_record.user_id, User.phone == phone).first()
    if not user:
        raise AppException("USER_NOT_FOUND", "用户不存在")

    # 更新密码
    user.password_hash = hash_password(new_password)
    token_record.is_used = True
    db.commit()

    return {"message": "密码重置成功"}


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改密码"""
    # 验证旧密码
    if not verify_password(old_password, current_user.password_hash):
        raise AppException("INVALID_PASSWORD", "旧密码错误")

    # 更新密码
    current_user.password_hash = hash_password(new_password)
    db.commit()

    return {"message": "密码修改成功"}