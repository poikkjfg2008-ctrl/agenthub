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
  const configRef = useRef<EmbedConfig | null>(null); // Store config in ref for message handler

  // Update ref when config changes
  useEffect(() => {
    configRef.current = config;
  }, [config]);

  useEffect(() => {
    loadConfig();

    // Listen for ready message from iframe
    const handleReadyMessage = (event: MessageEvent) => {
      if (event.data && event.data.type === 'ready' && configRef.current) {
        sendMessageToIframe();
      }
    };

    window.addEventListener('message', handleReadyMessage);
    return () => {
      window.removeEventListener('message', handleReadyMessage);
    };
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
    const currentConfig = configRef.current;
    if (!currentConfig || !iframeRef.current) return;

    const message = {
      type: 'init',
      config: {
        appKey: currentConfig.app_key,
        launchToken: currentConfig.launch_token,
        userContext: currentConfig.user_context,
        baseUrl: currentConfig.base_url,
        scriptUrl: currentConfig.script_url,
      },
    };

    try {
      iframeRef.current.contentWindow?.postMessage(message, '*');
      console.log('Sent init message to iframe');
    } catch (error) {
      console.error('Failed to send message to iframe:', error);
    }
  };

  useEffect(() => {
    if (config && iframeRef.current) {
      // Wait for iframe to load, then send message
      const iframe = iframeRef.current;
      const handleLoad = () => {
        console.log('Iframe loaded, sending init message');
        // Small delay to ensure iframe is ready
        setTimeout(sendMessageToIframe, 100);
      };
      iframe.addEventListener('load', handleLoad);

      return () => {
        iframe.removeEventListener('load', handleLoad);
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
