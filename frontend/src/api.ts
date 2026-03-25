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
} from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

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
};

// Launch APIs
export const launchApi = {
  getEmbedConfig: (launchId: string) =>
    api.get<EmbedConfig>(`/api/launches/${launchId}/embed-config`),

  listLaunches: (limit = 50) =>
    api.get<{ launches: LaunchRecord[] }>(`/api/launches?limit=${limit}`),
};

// Skill APIs
export const skillApi = {
  listSkills: () =>
    api.get<SkillInfo[]>('/api/skills'),
};

export default api;
