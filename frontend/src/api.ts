/** API client for AI Portal backend */

import axios from 'axios';
import type {
  Resource,
  PortalSession,
  LaunchRecord,
  Message,
  LaunchResponse,
  SkillInfo,
  EmbedConfig,
  IframeConfig,
  StreamChunk,
} from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/';

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Send cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auth APIs
export const authApi = {
  mockLogin: (empNo: string) =>
    api.get(`/api/auth/mock-login?emp_no=${empNo}`),

  getMe: () =>
    api.get<any>('/api/auth/me'),

  logout: () =>
    api.post('/api/auth/logout'),
};

// Resource APIs
export const resourceApi = {
  listResources: () =>
    api.get<Resource[]>('/api/resources'),

  listResourcesGrouped: () =>
    api.get<Record<string, Resource[]>>('/api/resources/grouped'),

  getResource: (id: string) =>
    api.get<Resource>(`/api/resources/${id}`),

  launchResource: (id: string) =>
    api.post<LaunchResponse>(`/api/resources/${id}/launch`),
};

// Session APIs
export const sessionApi = {
  listSessions: (limit = 50) =>
    api.get<{ sessions: PortalSession[] }>(`/api/sessions?limit=${limit}`),

  getMessages: (sessionId: string) =>
    api.get<Message[]>(`/api/sessions/${sessionId}/messages`),

  sendMessage: (sessionId: string, text: string) =>
    api.post<{ response: string }>(`/api/sessions/${sessionId}/messages`, { text }),

  /**
   * Send message with streaming response using SSE
   */
  sendMessageStream: (
    sessionId: string,
    text: string,
    onChunk: (chunk: string, messageId: string) => void,
    onDone: (messageId: string) => void,
    onError: (error: string) => void
  ): AbortController => {
    const controller = new AbortController();
    const { signal } = controller;

    const url = `${API_BASE_URL}api/sessions/${sessionId}/messages/stream`;
    
    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ text }),
      signal,
    })
      .then(async (response) => {
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`HTTP ${response.status}: ${errorText}`);
        }

        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error('Response body is null');
        }

        const decoder = new TextDecoder();
        let buffer = '';
        let currentMessageId = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            const trimmedLine = line.trim();
            if (!trimmedLine) continue;

            if (trimmedLine.startsWith('data: ')) {
              const dataStr = trimmedLine.slice(6);
              
              if (dataStr === '[DONE]') {
                onDone(currentMessageId);
                continue;
              }

              try {
                const data: StreamChunk = JSON.parse(dataStr);
                
                if (data.type === 'start') {
                  currentMessageId = data.message_id || '';
                } else if (data.type === 'chunk' && data.content) {
                  onChunk(data.content, data.message_id || currentMessageId);
                } else if (data.type === 'done') {
                  onDone(data.message_id || currentMessageId);
                } else if (data.type === 'error') {
                  onError(data.content || 'Unknown error');
                }
              } catch (e) {
                // If not valid JSON, treat as plain text chunk
                onChunk(dataStr, currentMessageId);
              }
            }
          }
        }

        // Process remaining buffer
        if (buffer.trim()) {
          const trimmedBuffer = buffer.trim();
          if (trimmedBuffer.startsWith('data: ')) {
            const dataStr = trimmedBuffer.slice(6);
            try {
              const data: StreamChunk = JSON.parse(dataStr);
              if (data.type === 'done') {
                onDone(data.message_id || currentMessageId);
              } else if (data.type === 'error') {
                onError(data.content || 'Unknown error');
              }
            } catch (e) {
              // Ignore parse errors at end
            }
          }
        }

        onDone(currentMessageId);
      })
      .catch((error) => {
        if (error.name === 'AbortError') {
          return;
        }
        onError(error.message || 'Failed to send message');
      });

    return controller;
  },
};

// Launch APIs
export const launchApi = {
  getEmbedConfig: (launchId: string) =>
    api.get<EmbedConfig>(`/api/launches/${launchId}/embed-config`),

  getIframeConfig: (launchId: string) =>
    api.get<IframeConfig>(`/api/launches/${launchId}/iframe-config`),

  listLaunches: (limit = 50) =>
    api.get<{ launches: LaunchRecord[] }>(`/api/launches?limit=${limit}`),
};

// Skill APIs
export const skillApi = {
  listSkills: () =>
    api.get<SkillInfo[]>('/api/skills'),
};

export default api;
