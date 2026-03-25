/** Session sidebar component */

import { useEffect, useState } from 'react';
import { MessageSquare, Clock, Trash2 } from 'lucide-react';
import { sessionApi } from '../api';
import type { PortalSession } from '../types';
import { resourceApi } from './api';

interface SessionSidebarProps {
  currentSessionId?: string;
  onSelectSession: (sessionId: string) => void;
  onNewChat: () => void;
}

export function SessionSidebar({
  currentSessionId,
  onSelectSession,
  onNewChat,
}: SessionSidebarProps) {
  const [sessions, setSessions] = useState<PortalSession[]>([]);
  const [resourceNames, setResourceNames] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadSessions();
    loadResources();
  }, []);

  const loadSessions = async () => {
    try {
      const response = await sessionApi.listSessions(50);
      setSessions(response.data.sessions);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadResources = async () => {
    try {
      const response = await resourceApi.listResources();
      const names: Record<string, string> = {};
      response.data.forEach((resource) => {
        names[resource.id] = resource.name;
      });
      setResourceNames(names);
    } catch (error) {
      console.error('Failed to load resources:', error);
    }
  };

  return (
    <div className="w-64 bg-white border-r flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">会话历史</h2>
        <button
          onClick={onNewChat}
          className="w-full px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors font-medium text-sm"
        >
          新建对话
        </button>
      </div>

      {/* Sessions */}
      <div className="flex-1 overflow-y-auto p-4">
        {isLoading ? (
          <div className="text-center text-gray-500 text-sm">加载中...</div>
        ) : sessions.length === 0 ? (
          <div className="text-center text-gray-500 text-sm">
            暂无会话历史
          </div>
        ) : (
          <div className="space-y-2">
            {sessions.map((session) => (
              <div
                key={session.portal_session_id}
                onClick={() => onSelectSession(session.portal_session_id)}
                className={`p-3 rounded-lg cursor-pointer transition-colors ${
                  currentSessionId === session.portal_session_id
                    ? 'bg-primary-50 border border-primary-200'
                    : 'hover:bg-gray-50 border border-transparent'
                }`}
              >
                <div className="flex items-start space-x-2">
                  <MessageSquare className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {resourceNames[session.resource_id] || '未知资源'}
                    </p>
                    <div className="flex items-center mt-1 text-xs text-gray-500">
                      <Clock className="w-3 h-3 mr-1" />
                      {new Date(session.updated_at).toLocaleString('zh-CN', {
                        month: '2-digit',
                        day: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
