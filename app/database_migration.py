"""数据库迁移脚本"""

from sqlalchemy import text
import sys
import os

# 添加当前目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine
from datetime import datetime

def migrate_database():
    """执行数据库迁移"""
    with engine.connect() as conn:
        # 1. 添加用户表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone VARCHAR(20) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                nickname VARCHAR(50),
                email VARCHAR(100),
                is_active BOOLEAN DEFAULT TRUE,
                is_verified BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """))

        # 2. 添加用户会话表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token VARCHAR(255) NOT NULL UNIQUE,
                expires_at DATETIME NOT NULL,
                device_info TEXT,
                ip_address VARCHAR(45),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
        """))

        # 3. 检查并修改user_posts表
        try:
            # 检查列是否存在
            result = conn.execute(text("""
                SELECT name FROM pragma_table_info('user_posts')
            """))
            existing_columns = [row[0] for row in result.fetchall()]

            columns_to_add = []
            if 'user_id' not in existing_columns:
                columns_to_add.append('user_id INTEGER')
            if 'is_public' not in existing_columns:
                columns_to_add.append('is_public BOOLEAN DEFAULT 0')
            if 'view_count' not in existing_columns:
                columns_to_add.append('view_count INTEGER DEFAULT 0')

            if columns_to_add:
                for column in columns_to_add:
                    conn.execute(text(f"ALTER TABLE user_posts ADD COLUMN {column};"))
                conn.commit()
                print("✅ 添加了新列到 user_posts 表")
            else:
                print("✅ user_posts 表已有所有需要的列")

            # 添加外键约束
            try:
                conn.execute(text("""
                    ALTER TABLE user_posts ADD CONSTRAINT fk_user_posts_user
                    FOREIGN KEY (user_id) REFERENCES users (id);
                """))
                conn.commit()
                print("✅ 添加了外键约束")
            except:
                print("✅ 外键约束已存在")
        except Exception as e:
            print(f"⚠️ 处理 user_posts 表时出错: {e}")

        # 4. 检查并修改style_profile表
        try:
            # 检查表的所有列
            result = conn.execute(text("""
                SELECT name FROM pragma_table_info('style_profile')
            """))
            existing_columns = [row[0] for row in result.fetchall()]

            columns_to_add = []
            if 'user_id' not in existing_columns:
                columns_to_add.append('user_id INTEGER')
            if 'model_used' not in existing_columns:
                columns_to_add.append('model_used VARCHAR(50)')
            if 'confidence_score' not in existing_columns:
                columns_to_add.append('confidence_score VARCHAR(10)')

            if columns_to_add:
                for column in columns_to_add:
                    conn.execute(text(f"ALTER TABLE style_profile ADD COLUMN {column};"))
                conn.commit()
                print(f"✅ 添加了新列到 style_profile 表: {columns_to_add}")
            else:
                print("✅ style_profile 表已有所有需要的列")

            # 添加外键约束
            try:
                conn.execute(text("""
                    ALTER TABLE style_profile ADD CONSTRAINT fk_style_profile_user
                    FOREIGN KEY (user_id) REFERENCES users (id);
                """))
                conn.commit()
                print("✅ 添加了外键约束")
            except:
                print("✅ 外键约束已存在")
        except Exception as e:
            print(f"⚠️ 处理 style_profile 表时出错: {e}")

        # 5. 添加密码重置令牌表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token VARCHAR(255) NOT NULL UNIQUE,
                expires_at DATETIME NOT NULL,
                is_used BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
        """))
        print("✅ 创建了密码重置令牌表")

        # 6. 为user表的updated_at添加默认值（如果还没有）
        conn.execute(text("""
            CREATE TRIGGER IF NOT EXISTS update_users_timestamp
            AFTER UPDATE ON users
            FOR EACH ROW
            BEGIN
                UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
        """))
        print("✅ 创建了更新触发器")

        conn.commit()
        print("\n✅ 数据库迁移完成")

if __name__ == "__main__":
    migrate_database()