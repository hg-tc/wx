# 贡献指南

感谢你考虑为本项目做出贡献！

## 如何贡献

### 报告 Bug

如果你发现了 Bug，请在 GitHub Issues 中创建一个新的 Issue，包含以下信息：

- **标题**: 简明扼要地描述问题
- **描述**: 详细描述问题，包括：
  - 预期行为
  - 实际行为
  - 复现步骤
  - 错误日志
  - 环境信息（OS、Python 版本、依赖版本等）

### 提出新功能

如果你有新功能的想法：

1. 在 GitHub Issues 中创建一个 Feature Request
2. 详细描述功能需求和使用场景
3. 等待维护者反馈
4. 获得批准后，可以开始开发

### 提交代码

#### 准备工作

1. **Fork 项目**
   ```bash
   # 访问 GitHub 页面点击 Fork
   ```

2. **克隆你的 Fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/wx.git
   cd wx
   ```

3. **添加上游仓库**
   ```bash
   git remote add upstream https://github.com/hg-tc/wx.git
   ```

4. **创建开发环境**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

#### 开发流程

1. **创建特性分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **进行开发**
   - 编写代码
   - 添加测试
   - 更新文档

3. **代码检查**
   ```bash
   # 格式化代码
   black app/
   
   # 检查代码风格
   flake8 app/
   
   # 运行测试
   pytest
   ```

4. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加新功能"
   ```

5. **同步上游更改**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

6. **推送到你的 Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **创建 Pull Request**
   - 访问 GitHub 页面
   - 点击 "New Pull Request"
   - 填写 PR 描述

## 代码规范

### Python 代码风格

遵循 PEP 8 规范，使用 Black 进行格式化：

```bash
black app/ --line-length 100
```

### 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型（type）**:
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

**示例**:
```
feat(wecom): 添加客服会话状态管理

- 实现自动检测会话状态
- 添加状态转换逻辑
- 更新相关文档

Closes #123
```

### 文档规范

- 所有公开的函数、类都需要添加 docstring
- 使用 Google 风格的 docstring

```python
def function_name(param1: str, param2: int) -> bool:
    """函数的简短描述。

    更详细的描述（如果需要）。

    Args:
        param1: 参数1的描述
        param2: 参数2的描述

    Returns:
        返回值的描述

    Raises:
        ValueError: 异常情况的描述
    """
    pass
```

## 测试

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_specific.py

# 查看覆盖率
pytest --cov=app tests/
```

### 编写测试

- 为新功能编写单元测试
- 确保测试覆盖率不低于现有水平
- 测试文件命名: `test_*.py`

```python
import pytest
from app.your_module import your_function

def test_your_function():
    """测试 your_function 的基本功能"""
    result = your_function(param1, param2)
    assert result == expected_value

def test_your_function_edge_case():
    """测试 your_function 的边界情况"""
    with pytest.raises(ValueError):
        your_function(invalid_param)
```

## Pull Request 检查清单

在提交 PR 之前，请确认：

- [ ] 代码通过所有测试
- [ ] 添加了必要的测试
- [ ] 代码通过 linter 检查（flake8, black）
- [ ] 更新了相关文档
- [ ] 提交信息符合规范
- [ ] PR 描述清晰，说明了更改的内容和原因
- [ ] 关联了相关的 Issue（如果有）

## 代码审查

PR 提交后：

1. 维护者会进行代码审查
2. 可能会提出修改建议
3. 根据反馈进行修改
4. 审查通过后会合并到主分支

## 开发环境设置

### PostgreSQL 和 pgvector

```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib
sudo apt install postgresql-14-pgvector

# 创建数据库
sudo -u postgres createdb wecom_agent_dev
sudo -u postgres psql -d wecom_agent_dev -c "CREATE EXTENSION vector;"
```

### Redis

```bash
# Ubuntu/Debian
sudo apt install redis-server

# 启动 Redis
sudo systemctl start redis-server
```

### 运行开发服务器

```bash
# 方式 1: 直接运行
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 方式 2: 使用脚本
./scripts/start_dev.sh
```

## 获取帮助

如果有任何问题：

- 查看 [README](README.md)
- 查看 [文档](docs/)
- 在 GitHub Issues 中提问
- 查看现有的 PR 和 Issue

## 行为准则

- 尊重所有贡献者
- 提供建设性的反馈
- 保持专业和友好
- 关注代码质量和项目目标

---

再次感谢你的贡献！ 🎉

