/** Main application component */

import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useSearchParams } from 'react-router-dom';
import { MessageSquare, BookOpen, Bot, Home, User, LogOut } from 'lucide-react';
import { resourceApi, authApi } from './api';
import type { Resource, UserCtx } from './types';
import { ResourceCard } from './components/ResourceCard';
import { ChatInterface } from './components/ChatInterface';
import { SessionSidebar } from './components/SessionSidebar';

function App() {
  const [user, setUser] = useState<UserCtx | null>(null);
  const [resourcesGrouped, setResourcesGrouped] = useState<Record<string, Resource[]>>({});
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    checkAuth();
  }, []);

  useEffect(() => {
    if (user) {
      loadResources();
    }
  }, [user]);

  const checkAuth = async () => {
    try {
      const response = await authApi.getMe();
      setUser(response.data);
    } catch (error) {
      console.log('Not authenticated');
      // Redirect to mock login
      window.location.href = '/api/auth/mock-login?emp_no=E10001';
    } finally {
      setIsLoading(false);
    }
  };

  const loadResources = async () => {
    try {
      const response = await resourceApi.listResourcesGrouped();
      setResourcesGrouped(response.data);
    } catch (error) {
      console.error('Failed to load resources:', error);
    }
  };

  const handleLaunch = async (resource: Resource) => {
    try {
      const response = await resourceApi.launchResource(resource.id);
      const launchData = response.data;

      if (launchData.kind === 'native' && launchData.portal_session_id) {
        navigate(`/chat/${launchData.portal_session_id}`);
      } else if (launchData.kind === 'websdk' && launchData.launch_id) {
        navigate(`/launch/${launchData.launch_id}`);
      }
    } catch (error: any) {
      console.error('Failed to launch resource:', error);
      alert(error.response?.data?.detail || '启动失败');
    }
  };

  const handleLogout = async () => {
    try {
      await authApi.logout();
      setUser(null);
      navigate('/');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
          <p className="text-gray-600">加载中...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null; // Will redirect to login
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/')}
                className="flex items-center space-x-2 text-gray-700 hover:text-gray-900"
              >
                <Home className="w-5 h-5" />
                <span className="font-semibold text-lg">AI Portal</span>
              </button>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <User className="w-4 h-4" />
                <span>{user.name}</span>
                <span className="text-gray-400">({user.emp_no})</span>
              </div>
              <button
                onClick={handleLogout}
                className="text-gray-600 hover:text-gray-900"
                title="退出登录"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Routes>
          <Route
            path="/"
            element={
              <div>
                <div className="mb-8">
                  <h1 className="text-3xl font-bold text-gray-900 mb-2">
                    欢迎使用 AI Portal
                  </h1>
                  <p className="text-gray-600">
                    选择您需要的 AI 服务开始对话
                  </p>
                </div>

                {Object.entries(resourcesGrouped).map(([group, resources]) => (
                  <div key={group} className="mb-8">
                    <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
                      {group === '基础对话' && <MessageSquare className="w-5 h-5 mr-2" />}
                      {group === '技能助手' && <Bot className="w-5 h-5 mr-2" />}
                      {group === '知识库' && <BookOpen className="w-5 h-5 mr-2" />}
                      {group}
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {resources.map((resource) => (
                        <ResourceCard
                          key={resource.id}
                          resource={resource}
                          onLaunch={handleLaunch}
                        />
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            }
          />

          <Route
            path="/chat/:sessionId"
            element={
              <div className="flex h-[calc(100vh-8rem)] gap-6">
                <SessionSidebar
                  onSelectSession={(sessionId) => navigate(`/chat/${sessionId}`)}
                  onNewChat={() => navigate('/')}
                />
                <div className="flex-1 bg-white rounded-lg shadow overflow-hidden">
                  <ChatInterface sessionId={searchParams.get('sessionId') || ''} />
                </div>
              </div>
            }
          />

          <Route
            path="/launch/:launchId"
            element={
              <div className="h-[calc(100vh-8rem)] bg-white rounded-lg shadow overflow-hidden">
                <WorkspacePane launchId={searchParams.get('launchId') || ''} />
              </div>
            }
          />
        </Routes>
      </main>
    </div>
  );
}

function AppWithRouter() {
  return (
    <Router>
      <App />
    </Router>
  );
}

export default AppWithRouter;
