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

export interface ResourceSyncMeta {
  origin: string;
  origin_key: string;
  workspace_id?: string;
  version?: string;
  sync_status?: string;
  last_seen_at?: string;
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
  sync_meta?: ResourceSyncMeta;
}

export interface PortalSession {
  portal_session_id: string;
  resource_id: string;
  resource_type: string;
  resource_name?: string;
  user_emp_no: string;
  title?: string;
  status?: string;
  resource_snapshot?: Record<string, any>;
  created_at: string;
  updated_at: string;
  last_message_at?: string;
  last_message_preview?: string;
  parent_session_id?: string;
  metadata: {
    adapter: string;
  };
}

export interface SessionBinding {
  binding_id: string;
  portal_session_id: string;
  engine_type: string;
  adapter: string;
  engine_session_id?: string;
  external_session_ref?: string;
  workspace_id?: string;
  skill_name?: string;
  binding_status: string;
  created_at: string;
  updated_at: string;
}

export interface PortalMessage {
  message_id: string;
  portal_session_id: string;
  role: 'user' | 'assistant' | 'system';
  text: string;
  engine_message_id?: string;
  trace_id?: string;
  created_at: string;
  metadata?: Record<string, any>;
}

export interface ContextScope {
  context_id: string;
  scope_type: string;
  scope_key: string;
  payload: Record<string, any>;
  summary?: string;
  updated_at: string;
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

export interface StreamChunk {
  type: 'start' | 'chunk' | 'done' | 'error';
  content?: string;
  message_id?: string;
}

export interface PendingFile {
  file: File;
  id: string;
  previewUrl?: string;
  status: 'pending' | 'uploading' | 'uploaded' | 'error';
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
