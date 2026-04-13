"""日志配置"""

import logging
import sys


def setup_logging(level: str = "INFO") -> logging.Logger:
    """配置日志"""

    # 创建 logger
    logger = logging.getLogger("app")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # 防止重复添加 handler
    if logger.handlers:
        return logger

    # 创建格式器
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def get_logger(name: str = "app") -> logging.Logger:
    """获取 logger"""
    return logging.getLogger(name)