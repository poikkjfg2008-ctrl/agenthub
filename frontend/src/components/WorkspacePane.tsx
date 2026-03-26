/** Workspace pane component for WebSDK iframe embed */

import { useEffect, useState, useRef } from 'react';
import { Loader2, AlertCircle } from 'lucide-react';
import { launchApi } from '../api';
import type { EmbedConfig } from '../types';

interface WorkspacePaneProps {
  launchId: string;
}

export function WorkspacePane({ launchId }: WorkspacePaneProps) {
  const [config, setConfig] = useState<EmbedConfig | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    loadConfig();
  }, [launchId]);

  const loadConfig = async () => {
    try {
      setIsLoading(true);
      const response = await launchApi.getEmbedConfig(launchId);
      setConfig(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || '加载配置失败');
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessageToIframe = () => {
    if (!config || !iframeRef.current) return;

    const message = {
      type: 'init',
      config: {
        appKey: config.app_key,
        launchToken: config.launch_token,
        userContext: config.user_context,
        baseUrl: config.base_url,
        scriptUrl: config.script_url,
      },
    };

    const sdkHostOrigin = new URL('/sdk-host.html', window.location.origin).origin;
    iframeRef.current.contentWindow?.postMessage(message, sdkHostOrigin);
  };

  useEffect(() => {
    if (config && iframeRef.current) {
      // Wait for iframe to load, then send message
      const iframe = iframeRef.current;
      iframe.addEventListener('load', sendMessageToIframe);

      return () => {
        iframe.removeEventListener('load', sendMessageToIframe);
      };
    }
  }, [config]);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-full bg-gray-50">
        <Loader2 className="w-12 h-12 animate-spin text-primary-500 mb-4" />
        <p className="text-gray-600">加载中...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full bg-gray-50">
        <AlertCircle className="w-12 h-12 text-red-500 mb-4" />
        <p className="text-red-600 font-medium mb-2">加载失败</p>
        <p className="text-gray-600 text-sm">{error}</p>
      </div>
    );
  }

  if (!config) {
    return null;
  }

  return (
    <div className="h-full w-full">
      <iframe
        ref={iframeRef}
        src="/sdk-host.html"
        className="w-full h-full border-0"
        title="WebSDK Workspace"
        sandbox="allow-same-origin allow-scripts allow-forms allow-popups"
      />
    </div>
  );
}
