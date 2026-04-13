"""安全相关工具"""

from datetime import datetime, timedelta
import secrets
import hashlib
import bcrypt
from jose import JWTError, jwt
from typing import Optional

# 配置
SECRET_KEY = "your-secret-key-here"  # 实际应该从环境变量获取
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天


def hash_password(password: str) -> str:
    """密码哈希"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建JWT访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """验证JWT令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def generate_password_reset_token() -> str:
    """生成密码重置令牌"""
    return secrets.token_urlsafe(32)


def create_sms_code() -> str:
    """创建6位短信验证码"""
    return f"{secrets.randbelow(900000) + 100000}"  # 100000-999999