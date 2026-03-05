import os
import requests
from dotenv import load_dotenv

# ================== 加载环境变量 ==================
load_dotenv()

# 提取配置参数
RAGFLOW_URL = os.getenv("RAGFLOW_URL")
RAGFLOW_API_KEY = os.getenv("RAGFLOW_API_KEY")
DIFY_URL = os.getenv("DIFY_URL")

# 登录信息
DIFY_LOGIN_EMAIL = os.getenv("DIFY_LOGIN_EMAIL")
DIFY_LOGIN_PASSWORD = os.getenv("DIFY_LOGIN_PASSWORD")

# 外部知识库配置
EXTERNAL_KB_TOP_K = int(os.getenv("EXTERNAL_KB_TOP_K", "2"))
EXTERNAL_KB_SCORE_THRESHOLD = float(os.getenv("EXTERNAL_KB_SCORE_THRESHOLD", "0.5"))
EXTERNAL_KB_SCORE_THRESHOLD_ENABLED = os.getenv(
    "EXTERNAL_KB_SCORE_THRESHOLD_ENABLED", "False"
)

# 构建 URL
DIFY_LOGIN_URL = f"{DIFY_URL}/console/api/login"
DIFY_EXTERNAL_KB_API_LIST_URL = f"{DIFY_URL}/console/api/datasets/external-knowledge-api"
DIFY_EXTERNAL_KB_CREATE_URL = f"{DIFY_URL}/console/api/datasets/external"
DIFY_EXTERNAL_KB_LIST_URL = f"{DIFY_URL}/console/api/datasets"
RAGFLOW_KB_URL = f"{RAGFLOW_URL}/api/v1/datasets/"


def login_and_get_token():
    """向 dify 登录接口发送请求，获取 access_token"""
    payload = {
        "email": DIFY_LOGIN_EMAIL,
        "password": DIFY_LOGIN_PASSWORD
    }

    try:
        response = requests.post(DIFY_LOGIN_URL, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            access_token = data["data"]["access_token"]
            print("✅ 登录成功，获取到 access_token")
            return access_token
        else:
            raise Exception(f"登录失败: {response.text}")
    except Exception as e:
        print(f"⚠️ 登录失败: {e}")
        return None


def get_dify_external_knowledge_api(dify_token):
    """查询 Dify 中的外部知识库 API 列表，并查找是否已注册 RAGFlow"""
    headers = {
        "Authorization": f"Bearer {dify_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(DIFY_EXTERNAL_KB_API_LIST_URL, headers=headers, timeout=10)
        if response.status_code == 200:
            external_apis = response.json().get("data", [])
            for api in external_apis:
                if api["settings"]["endpoint"] == f"{RAGFLOW_URL}/api/v1/dify":
                    print("✅ 找到已注册的 RAGFlow 外部知识库 API")
                    return api["id"]
            print("❌ 未找到 RAGFlow 的外部知识库 API，请在 Dify 中注册后再继续")
            return None
        else:
            raise Exception(f"获取 Dify 外部知识库 API 列表失败: {response.text}")
    except Exception as e:
        print(f"⚠️ 网络请求失败: {e}")
        return None


def get_ragflow_knowledge_bases(ragflow_api_key):
    """获取 RAGFlow 中的所有知识库 ID 和名称"""
    headers = {
        "Authorization": f"Bearer {ragflow_api_key}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(RAGFLOW_KB_URL, headers=headers, timeout=10)
        if response.status_code == 200:
            return [(kb["id"], kb["name"]) for kb in response.json()["data"]]
        else:
            raise Exception(f"获取 RAGFlow 知识库失败: {response.text}")
    except Exception as e:
        print(f"⚠️ 网络请求失败: {e}")
        return []


def create_dify_external_knowledge_base(kb_name, ragflow_kb_id, external_api_id, dify_token):
    """在 Dify 中创建外部知识库关联"""
    headers = {
        "Authorization": f"Bearer {dify_token}",
        "Content-Type": "application/json"
    }
    data = {
        "name": kb_name,
        "description": "",
        "external_knowledge_api_id": external_api_id,
        "external_knowledge_id": ragflow_kb_id,
        "external_retrieval_model": {
            "top_k": EXTERNAL_KB_TOP_K,
            "score_threshold": EXTERNAL_KB_SCORE_THRESHOLD,
            "score_threshold_enabled": EXTERNAL_KB_SCORE_THRESHOLD_ENABLED.lower() == "true"
        },
        "provider": "external"
    }

    try:
        response = requests.post(DIFY_EXTERNAL_KB_CREATE_URL, headers=headers, json=data, timeout=10)
        if response.status_code in [200, 201]:
            print(f"✅ 成功关联知识库: {kb_name} (ID: {ragflow_kb_id})")
        else:
            print(f"❌ 关联知识库失败: {kb_name}, 错误信息: {response.text}")
    except Exception as e:
        print(f"⚠️ 创建知识库时出错: {e}")


def get_dify_external_knowledge_bases(external_api_id, dify_token):
    """
    获取 Dify 中所有已注册关联的外部知识库（用于去重）
    只筛选当前指定的 external_knowledge_api_id 下的知识库
    """
    headers = {
        "Authorization": f"Bearer {dify_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(DIFY_EXTERNAL_KB_LIST_URL, headers=headers, timeout=10)
        if response.status_code == 200:
            external_kbs = response.json().get("data", [])
            existing_names = set()
            existing_ids = set()

            for kb in external_kbs:
                kb_info = kb.get("external_knowledge_info")
                if kb_info and kb_info.get("external_knowledge_api_id") == external_api_id:
                    kb_name = kb["name"]
                    kb_ragflow_id = kb_info["external_knowledge_id"]

                    existing_names.add(kb_name)
                    existing_ids.add(kb_ragflow_id)

            print(f"🔍 在 Dify 中找到 {len(existing_names)} 个已关联的外部知识库")
            return existing_names, existing_ids

        else:
            raise Exception(f"获取 Dify 外部知识库失败: {response.text}")
    except Exception as e:
        print(f"⚠️ 获取 Dify 外部知识库失败: {e}")
        return set(), set()


if __name__ == "__main__":
    # 1. 自动登录并获取 token
    dify_token = login_and_get_token()
    if not dify_token:
        exit(1)  # 如果登录失败，退出程序

    # 2. 获取 Dify 外部知识库 API ID
    external_api_id = get_dify_external_knowledge_api(dify_token)
    if not external_api_id:
        exit(1)

    # 3. 获取 RAGFlow 知识库列表
    try:
        ragflow_kbs = get_ragflow_knowledge_bases(RAGFLOW_API_KEY)
        print(f"🔍 共找到 {len(ragflow_kbs)} 个 RAGFlow 知识库")
    except Exception as e:
        print(f"⚠️ 获取 RAGFlow 知识库失败: {e}")
        exit(1)

    # 4. 获取 Dify 已有外部知识库（按id 去重）
    existing_names, existing_ids = get_dify_external_knowledge_bases(external_api_id, dify_token)

    # 5. 遍历并关联到 Dify（跳过已存在的）
    for kb_id, kb_name in ragflow_kbs:
        if kb_id in existing_ids:
            print(f"🟨 跳过已关联的知识库（ID 匹配）: {kb_name} (ID: {kb_id})")
            continue
        create_dify_external_knowledge_base(kb_name, kb_id, external_api_id, dify_token)