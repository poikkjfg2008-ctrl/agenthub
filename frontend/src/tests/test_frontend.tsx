/**
 * AI Portal 前端基础功能测试
 * 运行在浏览器控制台或通过测试框架
 */

// 测试结果存储
const testResults: Array<{
  name: string;
  status: string;
  message: string;
  duration: number;
}> = [];

// 日志函数
function logResult(name: string, status: string, message: string, duration: number) {
  testResults.push({ name, status, message, duration });
  const icon = status === '通过' ? '✅' : '❌';
  console.log(`${icon} ${name}: ${status} - ${message} (${duration.toFixed(2)}ms)`);
}

// API 测试类
class FrontendTests {
  private baseUrl: string;
  private cookies: Map<string, string>;

  constructor() {
    this.baseUrl = 'http://localhost:8000';
    this.cookies = new Map();
  }

  // 获取 Cookie
  private getCookies(): string {
    return Array.from(this.cookies.entries())
      .map(([k, v]) => `${k}=${v}`)
      .join('; ');
  }

  // 通用请求方法
  private async request(
    method: string,
    url: string,
    data?: any,
    includeCookies: boolean = true
  ): Promise<{ status: number; data: any; duration: number }> {
    const start = performance.now();

    try {
      const options: RequestInit = {
        method,
        credentials: includeCookies ? 'include' : 'omit',
        headers: {
          'Content-Type': 'application/json',
        },
      };

      if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
      }

      const response = await fetch(url, options);
      const duration = performance.now() - start;

      let responseData;
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        responseData = await response.json();
      } else {
        responseData = await response.text();
      }

      return { status: response.status, data: responseData, duration };
    } catch (error: any) {
      const duration = performance.now() - start;
      return { status: 0, data: { error: error.message }, duration };
    }
  }

  // 测试 1: 健康检查
  async testHealthCheck() {
    const start = performance.now();
    const result = await this.request('GET', `${this.baseUrl}/api/health`, false);

    if (result.status === 200 && result.data.status === 'healthy') {
      logResult('健康检查', '通过', '后端服务正常', result.duration);
      return true;
    } else {
      logResult('健康检查', '失败', `状态: ${result.status}`, result.duration);
      return false;
    }
  }

  // 测试 2: 模拟登录
  async testMockLogin() {
    const start = performance.now();
    const response = await fetch(`${this.baseUrl}/api/auth/mock-login?emp_no=E10001`, {
      credentials: 'include',
      redirect: 'manual',
    });
    const duration = performance.now() - start;

    if (response.status === 302 || response.status === 307) {
      logResult('模拟登录', '通过', '登录成功，已设置 Cookie', duration);
      return true;
    } else {
      logResult('模拟登录', '失败', `HTTP ${response.status}`, duration);
      return false;
    }
  }

  // 测试 3: 获取当前用户
  async testGetCurrentUser() {
    const result = await this.request('GET', `${this.baseUrl}/api/auth/me`);

    if (result.status === 200 && result.data.emp_no === 'E10001') {
      logResult('获取当前用户', '通过', `用户: ${result.data.name}`, result.duration);
      return true;
    } else if (result.status === 401) {
      logResult('获取当前用户', '失败', '未登录或登录已过期', result.duration);
      return false;
    } else {
      logResult('获取当前用户', '失败', `HTTP ${result.status}`, result.duration);
      return false;
    }
  }

  // 测试 4: 列出资源
  async testListResources() {
    const result = await this.request('GET', `${this.baseUrl}/api/resources`);

    if (result.status === 200 && Array.isArray(result.data) && result.data.length > 0) {
      logResult('列出资源', '通过', `找到 ${result.data.length} 个资源`, result.duration);
      return true;
    } else {
      logResult('列出资源', '失败', `HTTP ${result.status}`, result.duration);
      return false;
    }
  }

  // 测试 5: 列出分组资源
  async testListGroupedResources() {
    const result = await this.request('GET', `${this.baseUrl}/api/resources/grouped`);

    if (result.status === 200 && typeof result.data === 'object' && Object.keys(result.data).length > 0) {
      const groups = Object.keys(result.data);
      logResult('列出分组资源', '通过', `找到 ${groups.length} 个分组`, result.duration);
      return true;
    } else {
      logResult('列出分组资源', '失败', `HTTP ${result.status}`, result.duration);
      return false;
    }
  }

  // 测试 6: 获取单个资源
  async testGetResource() {
    const result = await this.request('GET', `${this.baseUrl}/api/resources/general-chat`);

    if (result.status === 200 && result.data.id === 'general-chat') {
      logResult('获取单个资源', '通过', `资源: ${result.data.name}`, result.duration);
      return true;
    } else {
      logResult('获取单个资源', '失败', `HTTP ${result.status}`, result.duration);
      return false;
    }
  }

  // 测试 7: 启动资源
  async testLaunchResource() {
    const result = await this.request('POST', `${this.baseUrl}/api/resources/general-chat/launch`);

    if (result.status === 200 && result.data.kind === 'native') {
      const sessionId = result.data.portal_session_id;
      logResult('启动原生资源', '通过', `会话ID: ${sessionId?.substring(0, 8)}...`, result.duration);
      return true;
    } else if (result.status === 500) {
      logResult('启动原生资源', '失败', 'OpenCode 服务未运行或配置错误', result.duration);
      return false;
    } else {
      logResult('启动原生资源', '失败', `HTTP ${result.status}`, result.duration);
      return false;
    }
  }

  // 测试 8: 列出技能
  async testListSkills() {
    const result = await this.request('GET', `${this.baseUrl}/api/skills`);

    if (result.status === 200 && Array.isArray(result.data)) {
      logResult('列出技能', '通过', `找到 ${result.data.length} 个技能`, result.duration);
      return true;
    } else {
      logResult('列出技能', '失败', `HTTP ${result.status}`, result.duration);
      return false;
    }
  }

  // 测试 9: 未授权访问保护
  async testUnauthorizedAccess() {
    // 使用 fetch 不带 credentials
    const start = performance.now();
    try {
      const response = await fetch(`${this.baseUrl}/api/resources`, {
        credentials: 'omit',
      });
      const duration = performance.now() - start;

      if (response.status === 401) {
        logResult('未授权访问保护', '通过', '正确拦截未授权请求', duration);
        return true;
      } else {
        logResult('未授权访问保护', '失败', `应该返回401，实际: ${response.status}`, duration);
        return false;
      }
    } catch (error: any) {
      logResult('未授权访问保护', '失败', `异常: ${error.message}`, 0);
      return false;
    }
  }

  // 测试 10: CORS 配置
  async testCORS() {
    const start = performance.now();
    try {
      const response = await fetch(`${this.baseUrl}/api/health`, {
        method: 'OPTIONS',
      });
      const duration = performance.now() - start;

      const corsHeaders = response.headers.get('access-control-allow-origin');
      if (corsHeaders) {
        logResult('CORS 配置', '通过', `CORS 头: ${corsHeaders}`, duration);
        return true;
      } else {
        logResult('CORS 配置', '警告', '未检测到 CORS 头', duration);
        return true; // 不影响通过
      }
    } catch (error: any) {
      logResult('CORS 配置', '失败', `异常: ${error.message}`, 0);
      return false;
    }
  }

  // 运行所有测试
  async runAllTests() {
    console.log('\n' + '='.repeat(60));
    console.log('🧪 AI Portal 前端功能测试');
    console.log('='.repeat(60) + '\n');

    const tests = [
      ['健康检查', () => this.testHealthCheck()],
      ['模拟登录', () => this.testMockLogin()],
      ['获取当前用户', () => this.testGetCurrentUser()],
      ['列出资源', () => this.testListResources()],
      ['列出分组资源', () => this.testListGroupedResources()],
      ['获取单个资源', () => this.testGetResource()],
      ['启动原生资源', () => this.testLaunchResource()],
      ['列出技能', () => this.testListSkills()],
      ['未授权访问保护', () => this.testUnauthorizedAccess()],
      ['CORS 配置', () => this.testCORS()],
    ];

    for (const [name, testFunc] of tests) {
      await testFunc();
      await new Promise(resolve => setTimeout(resolve, 500)); // 避免请求过快
    }

    return testResults;
  }
}

// 主测试函数
export async function runFrontendTests() {
  const tester = new FrontendTests();
  const results = await tester.runAllTests();

  console.log('\n' + '='.repeat(60));
  console.log('📊 测试结果汇总');
  console.log('='.repeat(60) + '\n');

  const total = results.length;
  const passed = results.filter(r => r.status === '通过').length;
  const failed = total - passed;
  const passRate = total > 0 ? (passed / total) * 100 : 0;

  console.log(`总计: ${total} | 通过: ${passed} | 失败: ${failed} | 通过率: ${passRate.toFixed(1)}%\n`);

  return results;
}

// 如果直接运行此脚本
if (typeof window !== 'undefined') {
  // 在浏览器环境中
  (window as any).runFrontendTests = runFrontendTests;
  console.log('💡 提示: 在浏览器控制台运行 runFrontendTests() 来执行测试');
}

export default FrontendTests;
