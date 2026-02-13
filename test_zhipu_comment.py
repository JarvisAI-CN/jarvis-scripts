#!/usr/bin/env python3
"""测试智谱API评论生成"""

import requests
import json

def test_generate_comment():
    """测试评论生成"""
    prompt = """你是一个积极参与AI社区讨论的成员。请阅读以下帖子并生成一个高质量的评论。

**帖子标题**: 测试标题
**作者**: 测试作者
**内容**: 这是一个测试内容。

**要求**:
1. 评论必须与帖子内容直接相关
2. 评论长度要在100字以上
3. 评论要有价值、有见地、友好积极
4. 使用中文，语气自然友好
5. 不要泛泛而谈，要具体到帖子内容

**请直接输出评论内容，不要有任何前缀或说明。"""

    try:
        # 智谱AI专属编程端点
        api_key = "9e65ece2efa781c15ecf344f62a8cf01.7BKc7Gj88ePbY74W"
        base_url = "https://open.bigmodel.cn/api/coding/paas/v4/chat/completions"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "glm-4.7",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }

        print("🔍 调用智谱API...")
        response = requests.post(
            base_url,
            headers=headers,
            json=payload,
            timeout=60
        )

        print(f"📊 状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"🔍 完整响应:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print()

            comment = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

            print(f"\n✅ 评论生成成功！")
            print(f"📏 长度: {len(comment)} 字")
            print(f"\n📝 内容:")
            print("="*60)
            print(comment)
            print("="*60)
            return comment
        else:
            print(f"❌ API调用失败: {response.text}")
            return None

    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_generate_comment()
