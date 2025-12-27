# 术语检索增强翻译工具

一个基于Streamlit的术语检索增强翻译工具，利用牛津词典术语库和DeepSeek大模型实现精准翻译。

## 功能特点

- 基于词袋模型的术语检索
- 余弦相似度Top-K匹配
- 增强型翻译Prompt
- DeepSeek API集成
- 直观易用的Web界面

## 项目结构

```
├── app.py                    # 主应用文件
├── simple_app.py             # 简化版应用
├── translation_service.py    # 翻译服务
├── retrieval_engine.py       # 检索引擎
├── data_processor.py         # 数据处理
├── rebuild_model.py          # 模型重建
├── terms.db                  # 术语数据库
├── vectorizer.pkl            # 向量器模型
├── term_matrix.npz           # 术语矩阵
├── oxford.mdx                # 牛津词典数据
└── requirements.txt          # 项目依赖
```

## 部署指南

### 1. 本地运行

#### 1.1 安装依赖

```bash
pip install -r requirements.txt
```

#### 1.2 设置环境变量

创建 `.env` 文件，添加DeepSeek API密钥：

```
DEEPSEEK_API_KEY=your_deepseek_api_key
```

#### 1.3 运行应用

```bash
# 运行主应用
streamlit run app.py

# 或运行简化版应用
streamlit run simple_app.py
```

应用将在浏览器中打开，默认地址为 `http://localhost:8501`

### 2. 部署到Streamlit Cloud

Streamlit Cloud是部署Streamlit应用最简单的方式，免费且无需服务器配置。

#### 2.1 准备工作

1. 将项目代码上传到GitHub仓库
2. 确保仓库包含 `requirements.txt` 文件
3. 在GitHub仓库中添加 `.env` 文件到 `.gitignore`（不要将API密钥提交到代码库）

#### 2.2 部署步骤

1. 访问 [Streamlit Cloud](https://streamlit.io/cloud)
2. 登录并点击 "New app"
3. 选择你的GitHub仓库、分支和主应用文件（`app.py`）
4. 点击 "Advanced settings"
5. 在 "Secrets" 中添加环境变量：
   ```
   DEEPSEEK_API_KEY=your_deepseek_api_key
   ```
6. 点击 "Deploy"

部署完成后，你将获得一个可访问的URL，例如 `https://your-app.streamlit.app`

### 3. 部署到Vercel

#### 3.1 准备工作

1. 安装Vercel CLI：
   ```bash
   npm install -g vercel
   ```
2. 创建 `vercel.json` 配置文件：
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "app.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "app.py"
       }
     ]
   }
   ```
3. 创建 `wsgi.py` 文件：
   ```python
   from streamlit.runtime.websocket import WebSocketHandler
   from streamlit.web.server.server import Server
   
   import sys
   import os
   
   # Add the current directory to the path
   sys.path.insert(0, os.path.dirname(__file__))
   
   # Import the Streamlit app
   import app
   
   def app(environ, start_response):
       # This is a placeholder for Vercel's WSGI interface
       # Streamlit doesn't support WSGI directly, so we'll redirect to Streamlit Cloud instead
       start_response('302 Found', [('Location', 'https://your-app.streamlit.app')])
       return [b'']
   ```

#### 3.2 部署步骤

```bash
# 登录Vercel
vercel login

# 部署应用
vercel
```

### 4. 部署到自己的服务器

#### 4.1 安装依赖

```bash
pip install -r requirements.txt
```

#### 4.2 启动应用

```bash
# 使用nohup在后台运行
nohup streamlit run app.py --server.port 80 --server.address 0.0.0.0 &

# 或使用systemd管理服务
# 创建 /etc/systemd/system/translation-tool.service
```

#### 4.3 配置反向代理（可选）

使用Nginx配置反向代理，添加SSL证书：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## 5. 注意事项

1. **API密钥安全**：不要将API密钥直接写入代码，使用环境变量或 secrets 管理
2. **数据库文件**：确保 `terms.db` 文件在部署时被正确包含
3. **资源限制**：根据部署平台调整Streamlit的资源使用设置
4. **隐私保护**：考虑添加访问控制，防止未授权使用
5. **定期更新**：定期更新依赖和模型文件

## 6. 访问应用

部署完成后，你可以通过以下方式访问应用：

- Streamlit Cloud: `https://your-app.streamlit.app`
- 自有服务器: `https://your-domain.com`
- 本地测试: `http://localhost:8501`

## 7. 自定义配置

### 7.1 修改检索参数

在 `app.py` 中修改：
- `ngram_range`: 调整n-gram范围
- `stop_words`: 设置停用词
- `k_value`: 默认检索数量

### 7.2 修改翻译模板

在 `translation_service.py` 中修改 `generate_enhanced_prompt` 函数，调整翻译提示模板。

## 技术栈

- Python 3.7+
- Streamlit
- Scikit-learn
- SQLite
- Requests
- DeepSeek API

## 许可证

MIT License
