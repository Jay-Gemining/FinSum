
# FinSum

FinSum 是一个旨在提供每日金融市场摘要的应用程序。它通过抓取路透社和雅虎财经等来源的最新新闻和市场数据，然后利用大型语言模型 (LLM) 生成简洁的摘要、市场情绪分析和头条新闻。

## 功能

- **执行摘要**: 当日市场活动的简明概述。
- **市场情绪**: 基于新闻和数据的整体市场情绪（例如，乐观、悲观、中性、复杂）及其原因。
- **关键指数**: 主要市场指数（例如，标普 500 指数、纳斯达克综合指数）的价格、变动和变动百分比。
- **头条新闻**: 从主要金融新闻来源中选出的最重要的三条新闻及其摘要。
- **数据缓存**: 后端缓存报告数据以提高性能并减少对外部服务的重复调用。
- **响应式前端**: 使用 React 构建的用户友好界面，用于显示财务摘要。

## 技术栈

### 后端 (`finsum_backend`)

- **Python**: 主要编程语言。
- **FastAPI**: 用于构建 API 的现代、快速（高性能）的 Web 框架。
- **httpx**: 用于发出异步 HTTP 请求以抓取数据。
- **BeautifulSoup4**: 用于解析 HTML 内容。
- **Uvicorn**: ASGI 服务器，用于运行 FastAPI 应用程序。
- **（模拟的）LLM 服务**: 目前，LLM 交互被模拟以进行开发和测试，而无需实际的 API 密钥。

### 前端 (`frontend`)

- **React**: 用于构建用户界面的 JavaScript 库。
- **Vite**: 快速的前端构建工具和开发服务器。
- **Axios**: 用于从前端发出 API 请求的基于 Promise 的 HTTP 客户端。
- **CSS**: 用于样式化组件。

## 项目结构

```
.
├── finsum_backend        # 后端 FastAPI 应用程序
│   ├── core              # 核心逻辑（缓存、LLM 服务、报告生成器、爬虫）
│   │   ├── cache.py
│   │   ├── llm_service.py
│   │   ├── report_generator.py
│   │   └── scraper.py
│   ├── main.py           # FastAPI 应用程序入口点
│   └── requirements.txt  # Python 依赖项
├── frontend              # 前端 React 应用程序
│   ├── public            # 静态资源
│   ├── src               # React 源代码
│   │   ├── components    # React 组件
│   │   ├── App.jsx       # 主要应用程序组件
│   │   ├── main.jsx      # React 应用程序入口点
│   │   └── index.css     # 全局样式
│   ├── index.html        # HTML 入口文件
│   ├── package.json      # Node.js 依赖项和脚本
│   └── vite.config.js    # Vite 配置文件
└── README.md             # 本文件
```

## 安装和运行

### 先决条件

- Python 3.8+
- Node.js 和 npm (或 yarn)

### 后端设置

1.  **克隆仓库**:
    ```bash
    git clone <repository_url>
    cd <repository_name>/finsum_backend
    ```

2.  **创建并激活虚拟环境** (推荐):
    ```bash
    python -m venv venv
    source venv/bin/activate  # 在 Windows 上使用 `venv\Scripts\activate`
    ```

3.  **安装依赖项**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **运行后端服务器**:
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
    后端将在 `http://localhost:8000` 上可用。

### 前端设置

1.  **导航到前端目录**:
    ```bash
    cd ../frontend
    ```

2.  **安装依赖项**:
    ```bash
    npm install
    # 或者，如果您使用 yarn:
    # yarn install
    ```

3.  **运行前端开发服务器**:
    ```bash
    npm run dev
    # 或者，如果您使用 yarn:
    # yarn dev
    ```
    前端将在 `http://localhost:5173` (或 Vite 指示的其他端口) 上可用，并将代理 API 请求到后端。

## API 端点

-   `GET /api/report`: 获取最新的金融市场摘要报告。如果缓存中存在当天的有效报告，则返回缓存的报告；否则，生成新报告，缓存并返回。

## 未来可能的改进

-   **集成真实的 LLM**: 将模拟的 LLM 服务替换为对真实 LLM API (例如 OpenAI GPT 系列) 的实际调用。
-   **更强大的抓取**: 实施更可靠和更具弹性的抓取逻辑，以应对网站结构的变化。考虑使用 Scrapy 或类似的框架。
-   **用户身份验证**: 为个性化功能或 API 访问控制添加用户身份验证。
-   **数据库集成**: 将报告数据存储在数据库中以进行历史分析和更持久的缓存。
-   **扩展新闻来源**: 从更多金融新闻来源抓取数据。
-   **高级错误处理和日志记录**: 在后端和前端实施更全面的错误处理和日志记录。
-   **单元测试和集成测试**: 为后端和前端代码编写测试。
-   **CI/CD 流水线**: 设置持续集成和持续交付/部署。
-   **可配置性**: 允许通过配置文件或环境变量配置 LLM 模型、抓取目标等。
-   **实时更新**: 考虑使用 WebSockets 或类似技术进行更实时的市场数据更新。

## 贡献

欢迎贡献！请随时提交问题或拉取请求。

## 许可证

该项目根据 [MIT 许可证](LICENSE) (如果适用) 获得许可。
