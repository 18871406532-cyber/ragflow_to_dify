# 📚 RAGFlow 与 Dify 知识库同步脚本说明文档

本脚本用于自动将 RAGFlow 中的知识库同步到 Dify 平台，作为外部知识库使用。每次运行时会自动登录获取 token，并执行知识库的关联操作。

## 🧩 功能概述

* ✅ 使用 .env 中配置的邮箱和密码自动登录 Dify。

* 🔐 获取 access_token 用于后续请求。

* 🔍 查询 Dify 是否已注册 RAGFlow 的外部知识库接口。

* 🗂️ 获取 RAGFlow 所有知识库列表。

* 🔄 将每个知识库关联至 Dify 外部知识库中（避免重复）。

* ⚙️ 支持自定义检索参数：top_k、score_threshold、score_threshold_enabled。

## 📁 .env 配置说明

```js
RAGFLOW_API_KEY=your_api_key #配置自己的api key
RAGFLOW_URL=http://127.0.0.1:9380  #注意ip的更换，端口默认是9380
DIFY_EXTERNAL_KB_URL=http://127.0.0.1/console/api #注意ip的更换
# 登录信息
DIFY_LOGIN_EMAIL=your_email
DIFY_LOGIN_PASSWORD=your_password
#检索参数配置（可选，默认值已预设）
EXTERNAL_KB_TOP_K=2
EXTERNAL_KB_SCORE_THRESHOLD=0.5
EXTERNAL_KB_SCORE_THRESHOLD_ENABLED=False
```
## ⚠️ 注意： 

*不要在版本控制中提交 .env 文件，建议加入 .gitignore。
不要暴露你的账号密码或 API Key。*

# 🛠️ 运行环境依赖
*Python >= 3.8*
安装依赖包：
```js
pip install -r requirements.txt
```
# 输出示例
```js
✅ 登录成功，获取到 access_token
✅ 找到已注册的 RAGFlow 外部知识库 API
🔍 共找到 5 个 RAGFlow 知识库
🔍 在 Dify 中找到 2 个已关联的外部知识库
🟨 跳过已关联的知识库（ID 匹配）: sample_kb_1 (ID: kb_001)
✅ 成功关联知识库: sample_kb_2 (ID: kb_002)
✅ 成功关联知识库: sample_kb_3 (ID: kb_003)
...
```

# 📦 可选扩展功能（未来增强方向）
* ✅ 自动刷新 refresh_token。

* 🔄 增加定时任务自动同步。