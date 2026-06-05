#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一推送接口 - 支持企业微信和飞书双渠道
根据配置自动选择推送方式，提供统一的API
"""

import os
import logging
from typing import Optional, Union, Dict, Any, List
import pandas as pd

logger = logging.getLogger(__name__)

# 推送方式枚举
PUSH_METHOD_WECHAT = "wechat"  # 企业微信
PUSH_METHOD_FEISHU = "feishu"  # 飞书
PUSH_METHOD_BOTH = "both"      # 同时推送

# 获取推送方式配置
def get_push_method() -> str:
    """
    从环境变量获取推送方式
    优先级：环境变量 > 配置文件 > 默认值
    """
    push_method = os.getenv("PUSH_METHOD", "").lower()
    
    if push_method in [PUSH_METHOD_WECHAT, PUSH_METHOD_FEISHU, PUSH_METHOD_BOTH]:
        return push_method
    
    # 默认逻辑：如果配置了飞书，用飞书；否则用企业微信
    if os.getenv("FEISHU_APP_ID") and os.getenv("FEISHU_APP_SECRET"):
        logger.info("检测到飞书配置，将使用飞书作为默认推送方式")
        return PUSH_METHOD_FEISHU
    
    logger.info("未找到飞书配置，将使用企业微信作为默认推送方式")
    return PUSH_METHOD_WECHAT


def send_unified_message(message: Union[str, pd.DataFrame, Dict],
                        message_type: str = "default",
                        push_method: Optional[str] = None) -> bool:
    """
    统一推送消息接口
    
    Args:
        message: 消息内容（字符串、DataFrame或字典）
        message_type: 消息类型（task, discount, premium, position, error等）
        push_method: 推送方式（wechat, feishu, both），不指定则使用默认配置
    
    Returns:
        bool: 是否发送成功
    """
    try:
        # 检查是否为空消息
        if message is None:
            logger.warning("尝试发送空消息，已忽略")
            return False
        
        # 确定推送方式
        if push_method is None:
            push_method = get_push_method()
        
        logger.info(f"使用 [{push_method}] 推送消息，类型: {message_type}")
        
        # 根据推送方式调用对应的推送函数
        if push_method == PUSH_METHOD_WECHAT:
            return _send_via_wechat(message, message_type)
        
        elif push_method == PUSH_METHOD_FEISHU:
            return _send_via_feishu(message, message_type)
        
        elif push_method == PUSH_METHOD_BOTH:
            # 同时推送到两个渠道
            wechat_success = _send_via_wechat(message, message_type)
            feishu_success = _send_via_feishu(message, message_type)
            return wechat_success or feishu_success
        
        else:
            logger.error(f"未知的推送方式: {push_method}")
            return False
    
    except Exception as e:
        logger.error(f"统一推送消息失败: {str(e)}", exc_info=True)
        return False


def _send_via_wechat(message: Union[str, pd.DataFrame, Dict], 
                     message_type: str = "default") -> bool:
    """通过企业微信推送"""
    try:
        from wechat_push.push import send_wechat_message
        return send_wechat_message(message, message_type)
    except Exception as e:
        logger.error(f"企业微信推送失败: {str(e)}", exc_info=True)
        return False


def _send_via_feishu(message: Union[str, pd.DataFrame, Dict],
                     message_type: str = "default") -> bool:
    """通过飞书推送"""
    try:
        from wechat_push.feishu_push import send_feishu_message
        
        # 将消息转换为字符串（如果需要）
        if isinstance(message, pd.DataFrame):
            if message.empty:
                logger.warning("尝试发送空DataFrame，已忽略")
                return False
            # 简单处理：转换为文本表示
            msg_str = message.to_string()
        elif isinstance(message, dict):
            msg_str = str(message)
        else:
            msg_str = str(message)
        
        return send_feishu_message(msg_str)
    except Exception as e:
        logger.error(f"飞书推送失败: {str(e)}", exc_info=True)
        return False


def send_task_completion_notification(task: str, result: Dict[str, Any],
                                     push_method: Optional[str] = None) -> bool:
    """
    发送任务完成通知
    
    Args:
        task: 任务名称
        result: 任务执行结果
        push_method: 推送方式
    
    Returns:
        bool: 是否发送成功
    """
    try:
        if push_method is None:
            push_method = get_push_method()
        
        if push_method == PUSH_METHOD_WECHAT:
            from wechat_push.push import send_task_completion_notification as wechat_notify
            return wechat_notify(task, result)
        
        elif push_method == PUSH_METHOD_FEISHU:
            from wechat_push.feishu_push import send_task_completion_notification as feishu_notify
            return feishu_notify(task, result)
        
        elif push_method == PUSH_METHOD_BOTH:
            try:
                from wechat_push.push import send_task_completion_notification as wechat_notify
                wechat_notify(task, result)
            except:
                pass
            
            try:
                from wechat_push.feishu_push import send_task_completion_notification as feishu_notify
                return feishu_notify(task, result)
            except:
                return False
        
        return False
    
    except Exception as e:
        logger.error(f"发送任务完成通知失败: {str(e)}", exc_info=True)
        return False


# 为了向后兼容，保留原有函数名
def send_wechat_message(message: Union[str, pd.DataFrame, Dict],
                       message_type: str = "default",
                       webhook: Optional[str] = None) -> bool:
    """
    向后兼容的包装函数
    自动使用统一推送接口
    """
    return send_unified_message(message, message_type)


# 初始化
try:
    push_method = get_push_method()
    logger.info(f"推送模块初始化完成，默认推送方式: {push_method}")
except Exception as e:
    logger.error(f"推送模块初始化失败: {str(e)}", exc_info=True)
