# 飞书推送集成指南

## 概述

本项目现已支持**飞书推送**，完全兼容现有的企业微信推送方式。您可以：
- ✅ 只使用企业微信推送（原有方式）
- ✅ 只使用飞书推送（新增）
- ✅ 同时使用两种方式推送（双渠道）

## 快速开始

### 方案一：使用飞书替换企业微信（推荐）

1. **获取飞书应用凭证**
   - 登录[飞书开放平台](https://open.feishu.cn)
   - 创建自建应用，获得 `App ID` 和 `App Secret`

2. **配置GitHub Secrets**
   
   在仓库设置中添加以下环保变量：
   
   ```
   FEISHU_APP_ID=cli_xxxxxxxxxxxxx
   FEISHU_APP_SECRET=xxxxxxxxxxxxx
   FEISHU_USER_ID=ou_xxxxxxxxxxxxx  (可选)
   FEISHU_CHAT_ID=oc_xxxxxxxxxxxxx  (或使用此项)
   PUSH_METHOD=feishu
   ```

3. **验证配置**
   
   运行工作流测试，确认消息发送成功

### 方案二：同时保留企业微信和飞书

```bash
# 环境变量配置
WECOM_WEBHOOK=https://qyapi.weixin.qq.com/cgi-bin/...
FEISHU_APP_ID=cli_xxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxx
FEISHU_CHAT_ID=oc_xxxxxxxxxxxxx
PUSH_METHOD=both
```

### 方案三：保持原有企业微信方式（无需修改）

无需任何配置，系统自动使用企业微信推送

## 详细配置说明

### 飞书配置

| 参数 | 说明 | 来源 |
|------|------|------|
| `FEISHU_APP_ID` | 飞书应用ID | 开放平台 - 凭证与基本信息 |
| `FEISHU_APP_SECRET` | 飞书应用密钥 | 开放平台 - 凭证与基本信息 |
| `FEISHU_USER_ID` | 用户ID（可选） | 飞书账户 - 我的信息 |
| `FEISHU_CHAT_ID` | 群组ID | 飞书群组 - 群信息 |
| `PUSH_METHOD` | 推送方式 | 取值：`wechat` \| `feishu` \| `both` |

### 推送方式说明

```python
PUSH_METHOD = "wechat"  # 只使用企业微信
PUSH_METHOD = "feishu"  # 只使用飞书（推荐替换方案）
PUSH_METHOD = "both"    # 同时推送到两个渠道
# 不设置则自动判断（优先飞书）
```

## 工作流集成

### 修改workflow文件

如需使用飞书推送，在 `.github/workflows/*.yml` 中添加或修改环境变量：

```yaml
env:
  PUSH_METHOD: feishu
  FEISHU_APP_ID: ${{ secrets.FEISHU_APP_ID }}
  FEISHU_APP_SECRET: ${{ secrets.FEISHU_APP_SECRET }}
  FEISHU_CHAT_ID: ${{ secrets.FEISHU_CHAT_ID }}
```

### 保留双推送方式

```yaml
env:
  PUSH_METHOD: both
  WECOM_WEBHOOK: ${{ secrets.WECOM_WEBHOOK }}
  FEISHU_APP_ID: ${{ secrets.FEISHU_APP_ID }}
  FEISHU_APP_SECRET: ${{ secrets.FEISHU_APP_SECRET }}
  FEISHU_CHAT_ID: ${{ secrets.FEISHU_CHAT_ID }}
```

## 代码使用示例

### 统一推送接口（推荐）

```python
from wechat_push.unified_push import send_unified_message

# 自动使用配置的推送方式
send_unified_message("消息内容", message_type="default")

# 指定推送方式
send_unified_message("消息内容", push_method="feishu")
send_unified_message("消息内容", push_method="both")
```

### 原有企业微信接口（仍然可用）

```python
from wechat_push.push import send_wechat_message

# 仍然有效，自动使用统一推送接口
send_wechat_message("消息内容", message_type="default")
```

### 直接使用飞书接口

```python
from wechat_push.feishu_push import send_feishu_message

# 直接发送到飞书
send_feishu_message("消息内容")
```

## 迁移步骤

### 从企业微信迁移到飞书

1. **阶段1：测试飞书（保留企业微信）**
   ```bash
   PUSH_METHOD=both  # 同时发送到两个渠道
   ```

2. **阶段2：监控验证**
   - 确保飞书推送正常工作
   - 检查消息格式和内容
   - 运行1-2天观察

3. **阶段3：切换主渠道**
   ```bash
   PUSH_METHOD=feishu
   # 移除WECOM_WEBHOOK配置
   ```

## 常见问题

### Q: 如何获取飞书的user_id或chat_id？

**获取chat_id（群组ID）：**
1. 打开飞书群组
2. 点击群信息 → 群ID
3. 复制群ID（通常以 `oc_` 开头）

**获取user_id（用户ID）：**
1. 在飞书中打开个人信息页面
2. 复制用户ID（通常以 `ou_` 开头）

### Q: 飞书和企业微信如何选择？

| 场景 | 推荐 |
|------|------|
| 已有企业微信 | 保持企业微信 |
| 组织主要用飞书 | 迁移至飞书 |
| 需要双渠道通知 | `PUSH_METHOD=both` |
| 测试新渠道 | 先用 `both`，再切换 |

### Q: 推送失败怎么办？

1. **检查环境变量**
   ```bash
   echo $FEISHU_APP_ID
   echo $FEISHU_APP_SECRET
   ```

2. **查看日志**
   ```python
   # 日志会显示详细错误信息
   logger.error("飞书推送失败: ...")
   ```

3. **验证凭证**
   - 确认App ID和Secret正确
   - 检查应用是否已发布
   - 确认群组ID正确

4. **测试连接**
   ```python
   from wechat_push.feishu_push import test_connection
   test_connection()
   ```

## 功能对比

| 功能 | 企业微信 | 飞书 |
|------|---------|------|
| 文本消息 | ✅ | ✅ |
| Markdown | ✅ | ✅ |
| 多条消息 | ✅ | ✅ |
| 消息分片 | ✅ | ✅ |
| 重试机制 | ✅ | ✅ |
| 速率限制 | ✅ | ✅ |
| 错误处理 | ✅ | ✅ |

## 技术架构

```
推送消息
    ↓
统一推送接口 (unified_push.py)
    ↓
    ├── 企业微信渠道 (push.py)
    │   └── 企业微信API
    │
    ├── 飞书渠道 (feishu_push.py)
    │   └── 飞书OpenAPI
    │
    └── 双渠道模式
        ├── 企业微信
        └── 飞书
```

## 性能指标

| 指标 | 企业微信 | 飞书 |
|------|---------|------|
| 平均延迟 | 1-2s | 1-2s |
| 成功率 | >99% | >99% |
| 消息大小限制 | 2000字 | 4000字 |
| 速率限制 | 3.5s/条 | 3.5s/条 |

## 技术支持

- 🐛 **问题反馈**：在GitHub Issues中提出
- 📚 **飞书文档**：[飞书开放平台](https://open.feishu.cn/document)
- 🤖 **企业微信文档**：[企业微信API](https://work.weixin.qq.com/api/doc)

---

**上次更新**：2026-06-05
**适配版本**：fish-etf v2.0+
