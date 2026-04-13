"""Pytest 配置和共享 fixtures"""

import pytest
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_theme_data():
    """示例主题数据"""
    return {
        "name": "通勤经验分享",
        "post_length": 500
    }


@pytest.fixture
def sample_post_data():
    """示例帖子数据"""
    return {
        "theme_id": 1,
        "summary": "1. 驾驶感受\n2. 油耗表现\n3. 空间体验",
        "requirements": "字数500字左右",
        "content": "这是一篇关于用车体验的完整帖子内容。首先，我想分享我的驾驶感受..."
    }


@pytest.fixture
def sample_corpus_data():
    """示例语料库数据"""
    return {
        "title": "我的第一篇用车贴",
        "content": "今天提车了，心情非常激动...",
        "tags": "提车,新车",
        "note": "记录重要时刻"
    }
