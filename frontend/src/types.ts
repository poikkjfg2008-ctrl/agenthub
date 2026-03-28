/** Type definitions for AI Portal */

export type ResourceType = 'direct_chat' | 'skill_chat' | 'kb_websdk' | 'agent_websdk' | 'iframe';
export type LaunchMode = 'native' | 'websdk' | 'iframe';

export interface UserCtx {
  emp_no: string;
  name: string;
  dept: string;
  roles: string[];
  email?: string;
}

export interface ResourceConfig {
  workspace_id?: string;
  model?: string;
  script_url?: string;
  app_key?: string;
  base_url?: string;
  skill_name?: string;
  starter_prompts?: string[];
  iframe_url?: string;  // Direct iframe URL for iframe mode
  [key: string]: any;  // Allow additional config properties
}

export interface Resource {
  id: string;
  name: string;
  type: ResourceType;
  launch_mode: LaunchMode;
  group: string;
  description: string;
  enabled: boolean;
  tags: string[];
  config: ResourceConfig;
  acl?: any;
}

export interface PortalSession {
  portal_session_id: string;
  engine_session_id: string;
  resource_id: string;
  user_emp_no: string;
  created_at: string;
  updated_at: string;
  metadata: {
    adapter: string;
  };
}

export interface LaunchRecord {
  launch_id: string;
  resource_id: string;
  user_emp_no: string;
  launched_at: string;
  launch_token: string;
  user_context: any;
}

export interface Message {
  role: 'user' | 'assistant' | 'system';
  text: string;
  timestamp?: string;
}

export interface LaunchResponse {
  kind: LaunchMode;
  portal_session_id?: string;
  launch_id?: string;
}

export interface SkillInfo {
  id: string;
  name: string;
  description: string;
  installed: boolean;
  skill_name?: string;
  starter_prompts?: string[];
}

export interface EmbedConfig {
  script_url: string;
  app_key: string;
  base_url: string;
  launch_token: string;
  user_context: any;
}

export interface IframeConfig {
  iframe_url: string;
  user_context: any;
}
