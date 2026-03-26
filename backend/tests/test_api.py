"""AI Portal 后端 API 基础功能测试"""

import httpx
import asyncio
from typing import Dict, Optional


class TestAPI:
    """API 测试类"""

    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.cookies = {}
        self.test_results = []

    def log_result(self, test_name: str, status: str, message: str, response_time: float = 0):
        """记录测试结果"""
        self.test_results.append({
            "测试名称": test_name,
            "状态": status,
            "说明": message,
            "响应时间": f"{response_time:.2f}ms"
        })
        status_icon = "✅" if status == "通过" else "❌"
        print(f"{status_icon} {test_name}: {status} - {message} ({response_time:.2f}ms)")

    async def test_health_check(self):
        """测试健康检查"""
        try:
            async with httpx.AsyncClient() as client:
                import time
                start = time.time()
                response = await client.get(f"{self.base_url}/api/health")
                elapsed = (time.time() - start) * 1000

                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "healthy":
                        self.log_result("健康检查", "通过", "系统状态正常", elapsed)
                        return True
                    else:
                        self.log_result("健康检查", "失败", f"状态异常: {data}", elapsed)
                        return False
                else:
                    self.log_result("健康检查", "失败", f"HTTP {response.status_code}", elapsed)
                    return False
        except Exception as e:
            self.log_result("健康检查", "失败", f"异常: {str(e)}", 0)
            return False

    async def test_mock_login(self):
        """测试模拟登录"""
        try:
            async with httpx.AsyncClient() as client:
                import time
                start = time.time()
                response = await client.get(
                    f"{self.base_url}/api/auth/mock-login",
                    params={"emp_no": "E10001"},
                    follow_redirects=False
                )
                elapsed = (time.time() - start) * 1000

                # 检查是否有重定向
                if response.status_code in [302, 307]:
                    # 保存 cookies 到客户端
                    self.client = httpx.AsyncClient()
                    for cookie in response.cookies:
                        self.client.cookies.set(cookie.name, cookie.value)
                    self.log_result("模拟登录", "通过", "登录成功，获得token", elapsed)
                    return True
                else:
                    self.log_result("模拟登录", "失败", f"未重定向: HTTP {response.status_code}", elapsed)
                    return False
        except Exception as e:
            self.log_result("模拟登录", "失败", f"异常: {str(e)}", 0)
            return False

    async def test_get_current_user(self):
        """测试获取当前用户信息"""
        if not hasattr(self, 'client'):
            self.log_result("获取用户信息", "跳过", "未登录", 0)
            return False

        try:
            import time
            start = time.time()
            response = await self.client.get(f"{self.base_url}/api/auth/me")
            elapsed = (time.time() - start) * 1000

            if response.status_code == 200:
                data = response.json()
                if data.get("emp_no") == "E10001":
                    self.log_result("获取用户信息", "通过", f"用户: {data.get('name')}", elapsed)
                    return True
                else:
                    self.log_result("获取用户信息", "失败", f"用户信息异常: {data}", elapsed)
                    return False
            else:
                self.log_result("获取用户信息", "失败", f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            self.log_result("获取用户信息", "失败", f"异常: {str(e)}", 0)
            return False

    async def test_list_resources(self):
        """测试列出资源"""
        if not hasattr(self, 'client'):
            self.log_result("列出资源", "跳过", "未登录", 0)
            return False

        try:
            import time
            start = time.time()
            response = await self.client.get(f"{self.base_url}/api/resources")
            elapsed = (time.time() - start) * 1000

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.log_result("列出资源", "通过", f"找到 {len(data)} 个资源", elapsed)
                    return True
                else:
                    self.log_result("列出资源", "失败", "资源列表为空或格式错误", elapsed)
                    return False
            else:
                self.log_result("列出资源", "失败", f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            self.log_result("列出资源", "失败", f"异常: {str(e)}", 0)
            return False

    async def test_list_grouped_resources(self):
        """测试列出分组资源"""
        if not hasattr(self, 'client'):
            self.log_result("列出分组资源", "跳过", "未登录", 0)
            return False

        try:
            import time
            start = time.time()
            response = await self.client.get(f"{self.base_url}/api/resources/grouped")
            elapsed = (time.time() - start) * 1000

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and len(data) > 0:
                    groups = list(data.keys())
                    self.log_result("列出分组资源", "通过", f"找到 {len(groups)} 个分组: {', '.join(groups)}", elapsed)
                    return True
                else:
                    self.log_result("列出分组资源", "失败", "分组数据为空或格式错误", elapsed)
                    return False
            else:
                self.log_result("列出分组资源", "失败", f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            self.log_result("列出分组资源", "失败", f"异常: {str(e)}", 0)
            return False

    async def test_get_resource(self):
        """测试获取单个资源"""
        if not hasattr(self, 'client'):
            self.log_result("获取单个资源", "跳过", "未登录", 0)
            return False

        try:
            import time
            start = time.time()
            response = await self.client.get(f"{self.base_url}/api/resources/general-chat")
            elapsed = (time.time() - start) * 1000

            if response.status_code == 200:
                data = response.json()
                if data.get("id") == "general-chat":
                    self.log_result("获取单个资源", "通过", f"资源: {data.get('name')}", elapsed)
                    return True
                else:
                    self.log_result("获取单个资源", "失败", f"资源ID不匹配: {data}", elapsed)
                    return False
            else:
                self.log_result("获取单个资源", "失败", f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            self.log_result("获取单个资源", "失败", f"异常: {str(e)}", 0)
            return False

    async def test_launch_native_resource(self):
        """测试启动原生资源"""
        if not hasattr(self, 'client'):
            self.log_result("启动原生资源", "跳过", "未登录", 0)
            return False

        try:
            import time
            start = time.time()
            response = await self.client.post(f"{self.base_url}/api/resources/general-chat/launch")
            elapsed = (time.time() - start) * 1000

            if response.status_code == 200:
                data = response.json()
                if data.get("kind") == "native" and data.get("portal_session_id"):
                    self.session_id = data.get("portal_session_id")
                    self.log_result("启动原生资源", "通过", f"会话ID: {self.session_id[:8]}...", elapsed)
                    return True
                else:
                    self.log_result("启动原生资源", "失败", f"响应格式错误: {data}", elapsed)
                    return False
            else:
                detail = response.json().get("detail", "未知错误") if response.headers.get("content-type", "").startswith("application/json") else response.text
                self.log_result("启动原生资源", "失败", f"HTTP {response.status_code}: {detail}", elapsed)
                return False
        except Exception as e:
            self.log_result("启动原生资源", "失败", f"异常: {str(e)}", 0)
            return False

    async def test_list_sessions(self):
        """测试列出会话"""
        if not hasattr(self, 'client'):
            self.log_result("列出会话", "跳过", "未登录", 0)
            return False

        try:
            import time
            start = time.time()
            response = await self.client.get(f"{self.base_url}/api/sessions")
            elapsed = (time.time() - start) * 1000

            if response.status_code == 200:
                data = response.json()
                sessions = data.get("sessions", [])
                if isinstance(sessions, list):
                    self.log_result("列出会话", "通过", f"找到 {len(sessions)} 个会话", elapsed)
                    return True
                else:
                    self.log_result("列出会话", "失败", "会话列表格式错误", elapsed)
                    return False
            else:
                self.log_result("列出会话", "失败", f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            self.log_result("列出会话", "失败", f"异常: {str(e)}", 0)
            return False

    async def test_send_message(self):
        """测试发送消息"""
        if not hasattr(self, 'session_id'):
            self.log_result("发送消息", "跳过", "没有可用的会话", 0)
            return False

        if not hasattr(self, 'client'):
            self.log_result("发送消息", "跳过", "未登录", 0)
            return False

        try:
            import time
            start = time.time()
            response = await self.client.post(
                f"{self.base_url}/api/sessions/{self.session_id}/messages",
                json={"text": "你好，这是一个测试消息"},
                timeout=30.0
            )
            elapsed = (time.time() - start) * 1000

            if response.status_code == 200:
                data = response.json()
                if "response" in data:
                    self.log_result("发送消息", "通过", f"收到回复: {data['response'][:50]}...", elapsed)
                    return True
                else:
                    self.log_result("发送消息", "失败", f"响应格式错误: {data}", elapsed)
                    return False
            else:
                detail = response.json().get("detail", "未知错误") if response.headers.get("content-type", "").startswith("application/json") else response.text
                self.log_result("发送消息", "失败", f"HTTP {response.status_code}: {detail}", elapsed)
                return False
        except Exception as e:
            self.log_result("发送消息", "失败", f"异常: {str(e)}", 0)
            return False

    async def test_list_skills(self):
        """测试列出技能"""
        if not hasattr(self, 'client'):
            self.log_result("列出技能", "跳过", "未登录", 0)
            return False

        try:
            import time
            start = time.time()
            response = await self.client.get(f"{self.base_url}/api/skills")
            elapsed = (time.time() - start) * 1000

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("列出技能", "通过", f"找到 {len(data)} 个技能", elapsed)
                    return True
                else:
                    self.log_result("列出技能", "失败", "技能列表格式错误", elapsed)
                    return False
            else:
                self.log_result("列出技能", "失败", f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            self.log_result("列出技能", "失败", f"异常: {str(e)}", 0)
            return False

    async def test_unauthorized_access(self):
        """测试未授权访问"""
        try:
            async with httpx.AsyncClient() as client:
                import time
                start = time.time()
                response = await client.get(
                    f"{self.base_url}/api/resources"
                )
                elapsed = (time.time() - start) * 1000

                if response.status_code == 401:
                    self.log_result("未授权访问保护", "通过", "正确拦截未授权访问", elapsed)
                    return True
                else:
                    self.log_result("未授权访问保护", "失败", f"应该返回401，实际: {response.status_code}", elapsed)
                    return False
        except Exception as e:
            self.log_result("未授权访问保护", "失败", f"异常: {str(e)}", 0)
            return False

    async def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*60)
        print("🧪 AI Portal 后端 API 测试")
        print("="*60 + "\n")

        tests = [
            ("健康检查", self.test_health_check),
            ("模拟登录", self.test_mock_login),
            ("获取用户信息", self.test_get_current_user),
            ("列出资源", self.test_list_resources),
            ("列出分组资源", self.test_list_grouped_resources),
            ("获取单个资源", self.test_get_resource),
            ("启动原生资源", self.test_launch_native_resource),
            ("列出会话", self.test_list_sessions),
            ("发送消息", self.test_send_message),
            ("列出技能", self.test_list_skills),
            ("未授权访问保护", self.test_unauthorized_access),
        ]

        for test_name, test_func in tests:
            await test_func()
            await asyncio.sleep(0.5)  # 避免请求过快

        # 关闭客户端
        if hasattr(self, 'client'):
            await self.client.aclose()

        return self.test_results


async def main():
    """主函数"""
    tester = TestAPI()
    results = await tester.run_all_tests()

    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60 + "\n")

    # 统计
    total = len(results)
    passed = sum(1 for r in results if r["状态"] == "通过")
    failed = total - passed
    pass_rate = (passed / total * 100) if total > 0 else 0

    print(f"总计: {total} | 通过: {passed} | 失败: {failed} | 通过率: {pass_rate:.1f}%\n")

    return results


if __name__ == "__main__":
    results = asyncio.run(main())
