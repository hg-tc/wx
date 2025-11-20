# 更新日志

所有重要的项目更改都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 新增
- 企业微信客服 API 完整集成
- AI 驱动的智能对话系统
- 服务发布与匹配平台
- 商品比价功能
- 多轮对话上下文管理
- 向量语义搜索

### 修复
- 修复客服会话状态 state=3 无法发送消息的问题
- 修复 enter_session 事件 external_userid 提取错误
- 优化 API 频率限制处理

### 改进
- 完善错误日志和调试信息
- 添加详细的 API 错误码说明
- 优化会话状态管理逻辑

## [1.0.0] - 2025-11-20

### 新增
- 初始版本发布
- 基础的企业微信集成
- FastAPI 应用框架
- PostgreSQL + pgvector 数据库
- 基础的 AI 对话能力
- 服务管理 API
- 比价购物功能

### 文档
- 添加完整的 README
- 添加安装配置指南
- 添加 API 文档
- 添加故障排查指南
- 添加贡献指南

### 基础设施
- 配置 CI/CD
- 添加单元测试
- 配置代码检查工具
- 添加 Docker 支持（未来）

---

## 版本说明

### 版本号规则

- **主版本号（Major）**: 不兼容的 API 变更
- **次版本号（Minor）**: 向下兼容的功能新增
- **修订号（Patch）**: 向下兼容的问题修正

### 变更类型

- `新增` - 新功能
- `修复` - Bug 修复
- `改进` - 现有功能优化
- `变更` - 功能变更（可能不兼容）
- `移除` - 移除的功能
- `安全` - 安全相关的修复
- `文档` - 文档更新
- `依赖` - 依赖更新

[Unreleased]: https://github.com/hg-tc/wx/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/hg-tc/wx/releases/tag/v1.0.0

