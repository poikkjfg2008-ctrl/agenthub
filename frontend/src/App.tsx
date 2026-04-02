/** Main application component with new layout */

import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useParams } from 'react-router-dom';
import { User, LogOut, PanelRightOpen, PanelRightClose } from 'lucide-react';
import { resourceApi, authApi, sessionApi } from './api';
import type { Resource, UserCtx, LaunchResponse } from './types';
import { ResourceSidebar } from './components/ResourceSidebar';
import { ChatInterface } from './components/ChatInterface';
import { SessionSidebar } from './components/SessionSidebar';
import { WorkspacePane } from './components/WorkspacePane';
import { IframeWorkspace } from './components/IframeWorkspace';

// Default resource ID to load on startup
const DEFAULT_RESOURCE_ID = 'general-chat';

function App() {
  const [user, setUser] = useState<UserCtx | null>(null);
  const [resourcesGrouped, setResourcesGrouped] = useState<Record<string, Resource[]>>({});
  const [currentResource, setCurrentResource] = useState<Resource | null>(null);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [currentLaunchId, setCurrentLaunchId] = useState<string | null>(null);
  const [showWorkspace, setShowWorkspace] = useState(false);
  const [workspaceMode, setWorkspaceMode] = useState<'websdk' | 'iframe' | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isLaunching, setIsLaunching] = useState(false);
  const navigate = useNavigate();

  // Check auth on mount
  useEffect(() => {
    checkAuth();
  }, []);

  // Load resources when authenticated
  useEffect(() => {
    if (user) {
      loadResources();
    }
  }, [user]);

  // Load default resource when resources are loaded
  useEffect(() => {
    if (Object.keys(resourcesGrouped).length > 0 && !currentResource) {
      launchDefaultResource();
    }
  }, [resourcesGrouped]);

  const checkAuth = async () => {
    try {
      const response = await authApi.getMe();
      setUser(response.data);
    } catch (error) {
      console.log('Not authenticated, trying mock login...');
      try {
        await authApi.mockLogin('E10001');
        const response = await authApi.getMe();
        setUser(response.data);
      } catch (loginError) {
        console.error('Mock login failed:', loginError);
      }
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

  const launchDefaultResource = async () => {
    // Find default resource
    const allResources = Object.values(resourcesGrouped).flat();
    const defaultResource = allResources.find((r) => r.id === DEFAULT_RESOURCE_ID) || allResources[0];
    
    if (defaultResource) {
      await handleSelectResource(defaultResource);
    }
  };

  const handleSelectResource = async (resource: Resource) => {
    if (isLaunching) return;
    
    setIsLaunching(true);
    setCurrentResource(resource);

    try {
      const response = await resourceApi.launchResource(resource.id);
      const launchData: LaunchResponse = response.data;

      if (launchData.kind === 'native' && launchData.portal_session_id) {
        setCurrentSessionId(launchData.portal_session_id);
        setCurrentLaunchId(null);
        setShowWorkspace(false);
        setWorkspaceMode(null);
        navigate('/');
      } else if (launchData.kind === 'websdk' && launchData.launch_id) {
        setCurrentSessionId(null);
        setCurrentLaunchId(launchData.launch_id);
        setShowWorkspace(false);
        setWorkspaceMode('websdk');
        navigate('/');
      } else if (launchData.kind === 'iframe' && launchData.launch_id) {
        setCurrentSessionId(null);
        setCurrentLaunchId(launchData.launch_id);
        setShowWorkspace(false);
        setWorkspaceMode('iframe');
        navigate('/');
      }
    } catch (error: any) {
      console.error('Failed to launch resource:', error);
      alert(error.response?.data?.detail || '启动失败');
    } finally {
      setIsLaunching(false);
    }
  };

  const handleSelectSession = async (sessionId: string) => {
    try {
      // Find resource for this session
      const response = await sessionApi.listSessions(50);
      const session = response.data.sessions.find((s) => s.portal_session_id === sessionId);
      
      if (session) {
        const allResources = Object.values(resourcesGrouped).flat();
        const resource = allResources.find((r) => r.id === session.resource_id);
        if (resource) {
          setCurrentResource(resource);
        }
      }
      
      setCurrentSessionId(sessionId);
      setCurrentLaunchId(null);
      setShowWorkspace(false);
      setWorkspaceMode(null);
    } catch (error) {
      console.error('Failed to select session:', error);
    }
  };

  const handleNewChat = async () => {
    if (currentResource) {
      await handleSelectResource(currentResource);
    } else {
      await launchDefaultResource();
    }
  };

  const handleLogout = async () => {
    try {
      await authApi.logout();
      setUser(null);
      setCurrentResource(null);
      setCurrentSessionId(null);
      setCurrentLaunchId(null);
      navigate('/');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const toggleWorkspace = () => {
    setShowWorkspace((prev) => !prev);
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
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <p className="text-gray-600 mb-4">请先登录</p>
          <button
            onClick={checkAuth}
            className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600"
          >
            重新登录
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b sticky top-0 z-50">
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-br from-primary-400 to-primary-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">AI</span>
                </div>
                <span className="font-bold text-xl text-gray-900">AI Portal</span>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {/* Workspace toggle button (only for websdk/iframe modes) */}
              {(workspaceMode === 'websdk' || workspaceMode === 'iframe') && (
                <button
                  onClick={toggleWorkspace}
                  className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  {showWorkspace ? (
                    <>
                      <PanelRightClose className="w-4 h-4" />
                      <span className="hidden sm:inline">隐藏工作区</span>
                    </>
                  ) : (
                    <>
                      <PanelRightOpen className="w-4 h-4" />
                      <span className="hidden sm:inline">显示工作区</span>
                    </>
                  )}
                </button>
              )}

              <div className="flex items-center space-x-2 text-sm text-gray-600 bg-gray-50 px-3 py-1.5 rounded-lg">
                <User className="w-4 h-4" />
                <span className="font-medium">{user.name}</span>
                <span className="text-gray-400">({user.emp_no})</span>
              </div>
              <button
                onClick={handleLogout}
                className="text-gray-400 hover:text-red-600 transition-colors p-2 hover:bg-red-50 rounded-lg"
                title="退出登录"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main content - Three column layout */}
      <main className="flex-1 flex overflow-hidden">
        {/* Left: Resource Sidebar */}
        <ResourceSidebar
          resourcesGrouped={resourcesGrouped}
          currentResourceId={currentResource?.id}
          onSelectResource={handleSelectResource}
        />

        {/* Middle: Chat/Content Area */}
        <div className="flex-1 flex min-w-0">
          <Routes>
            <Route
              path="/"
              element={
                <MainContent
                  currentResource={currentResource}
                  currentSessionId={currentSessionId}
                  currentLaunchId={currentLaunchId}
                  workspaceMode={workspaceMode}
                  showWorkspace={showWorkspace}
                  onSelectSession={handleSelectSession}
                  onNewChat={handleNewChat}
                  isLaunching={isLaunching}
                />
              }
            />
            <Route
              path="/chat/:sessionId"
              element={
                <ChatRoutePage
                  resourcesGrouped={resourcesGrouped}
                  onResourceChange={setCurrentResource}
                />
              }
            />
            <Route
              path="/launch/:launchId"
              element={<LaunchRoutePage />}
            />
            <Route
              path="/iframe/:launchId"
              element={<IframeRoutePage />}
            />
          </Routes>
        </div>
      </main>
    </div>
  );
}

// Main content component
interface MainContentProps {
  currentResource: Resource | null;
  currentSessionId: string | null;
  currentLaunchId: string | null;
  workspaceMode: 'websdk' | 'iframe' | null;
  showWorkspace: boolean;
  onSelectSession: (sessionId: string) => void;
  onNewChat: () => void;
  isLaunching: boolean;
}

function MainContent({
  currentResource,
  currentSessionId,
  currentLaunchId,
  workspaceMode,
  showWorkspace,
  onSelectSession,
  onNewChat,
  isLaunching,
}: MainContentProps) {
  // Handle session selection from sidebar
  const handleSessionSelect = (sessionId: string) => {
    onSelectSession(sessionId);
  };

  // Handle new chat
  const handleNewChat = () => {
    onNewChat();
  };

  if (isLaunching) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
          <p className="text-gray-600">正在启动资源...</p>
        </div>
      </div>
    );
  }

  // No resource selected
  if (!currentResource) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="text-center text-gray-500">
          <p className="text-lg mb-2">请从左侧选择一个资源</p>
          <p className="text-sm">开始与 AI 助手对话</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex w-full h-full">
      {/* Left part: Session Sidebar + Chat Area */}
      <div className="flex flex-1 min-w-0">
        {/* Session Sidebar - only for native chat mode */}
        {currentResource.launch_mode === 'native' && (
          <div className="w-60 border-r bg-white hidden xl:flex flex-col flex-shrink-0">
            <SessionSidebar
              currentSessionId={currentSessionId || undefined}
              onSelectSession={handleSessionSelect}
              onNewChat={handleNewChat}
            />
          </div>
        )}

        {/* Chat/Content Area */}
        <div className="flex-1 min-w-0">
          {currentResource.launch_mode === 'native' && currentSessionId ? (
            <ChatInterface
              sessionId={currentSessionId}
              resource={currentResource}
              onRestart={handleNewChat}
            />
          ) : (workspaceMode === 'websdk' || workspaceMode === 'iframe') && currentLaunchId ? (
            showWorkspace ? (
              <div className="h-full flex items-center justify-center bg-gray-50 text-gray-500">
                <div className="text-center">
                  <p className="text-lg mb-2">工作区已在右侧显示</p>
                  <p className="text-sm">点击右上角按钮可以隐藏工作区</p>
                </div>
              </div>
            ) : (
              workspaceMode === 'websdk' ? (
                <WorkspacePane launchId={currentLaunchId} />
              ) : (
                <IframeWorkspace launchId={currentLaunchId} />
              )
            )
          ) : (
            <div className="h-full flex items-center justify-center bg-gray-50 text-gray-500">
              <div className="text-center">
                <p className="text-lg mb-2">准备就绪</p>
                <p className="text-sm">正在加载资源...</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Right part: Workspace Pane (for websdk/iframe modes) */}
      {showWorkspace && currentLaunchId && (workspaceMode === 'websdk' || workspaceMode === 'iframe') && (
        <div className="w-5/12 min-w-[380px] max-w-[600px] border-l bg-white flex-shrink-0">
          {workspaceMode === 'websdk' ? (
            <WorkspacePane launchId={currentLaunchId} />
          ) : (
            <IframeWorkspace launchId={currentLaunchId} />
          )}
        </div>
      )}
    </div>
  );
}

// Route page components
function ChatRoutePage({
  resourcesGrouped,
  onResourceChange,
}: {
  resourcesGrouped: Record<string, Resource[]>;
  onResourceChange: (resource: Resource) => void;
}) {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [resource, setResource] = useState<Resource | null>(null);

  // Fetch session details and set correct resource
  useEffect(() => {
    if (sessionId) {
      loadSessionResource();
    }
  }, [sessionId, resourcesGrouped]);

  const loadSessionResource = async () => {
    if (!sessionId) return;
    
    try {
      // Get session details from API to find the resource_id
      const response = await sessionApi.getSession(sessionId);
      const session = response.data;
      
      // Find the resource for this session
      const allResources = Object.values(resourcesGrouped).flat();
      const sessionResource = allResources.find((r) => r.id === session.resource_id);
      
      if (sessionResource) {
        setResource(sessionResource);
        onResourceChange(sessionResource);
      } else {
        // Fallback to default if resource not found
        const defaultRes = allResources.find((r) => r.id === DEFAULT_RESOURCE_ID) || allResources[0];
        if (defaultRes) {
          setResource(defaultRes);
          onResourceChange(defaultRes);
        }
      }
    } catch (error) {
      console.error('Failed to load session resource:', error);
      // Fallback to default resource on error
      const allResources = Object.values(resourcesGrouped).flat();
      if (allResources.length > 0) {
        const defaultRes = allResources.find((r) => r.id === DEFAULT_RESOURCE_ID) || allResources[0];
        setResource(defaultRes);
        onResourceChange(defaultRes);
      }
    }
  };

  const handleSelectSession = (selectedSessionId: string) => {
    // Navigate to the selected session
    navigate(`/chat/${selectedSessionId}`);
  };

  const handleNewChat = () => {
    // Navigate to home to start a new chat with current resource
    if (resource) {
      navigate('/');
    }
  };

  if (!sessionId) return null;

  return (
    <div className="flex h-full w-full">
      <div className="w-64 border-r bg-white hidden lg:flex flex-col">
        <SessionSidebar
          currentSessionId={sessionId}
          onSelectSession={handleSelectSession}
          onNewChat={handleNewChat}
        />
      </div>
      <div className="flex-1">
        <ChatInterface sessionId={sessionId} resource={resource || undefined} />
      </div>
    </div>
  );
}

function LaunchRoutePage() {
  const { launchId } = useParams();
  if (!launchId) return null;
  return (
    <div className="w-full h-full">
      <WorkspacePane launchId={launchId} />
    </div>
  );
}

function IframeRoutePage() {
  const { launchId } = useParams();
  if (!launchId) return null;
  return (
    <div className="w-full h-full">
      <IframeWorkspace launchId={launchId} />
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
