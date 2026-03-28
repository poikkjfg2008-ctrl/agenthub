/** Iframe workspace component for direct iframe embedding */

import { useEffect, useState } from 'react';
import { Loader2, AlertCircle } from 'lucide-react';
import { launchApi } from '../api';
import type { IframeConfig } from '../types';

interface IframeWorkspaceProps {
  launchId: string;
}

export function IframeWorkspace({ launchId }: IframeWorkspaceProps) {
  const [config, setConfig] = useState<IframeConfig | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadConfig();
  }, [launchId]);

  const loadConfig = async () => {
    try {
      setIsLoading(true);
      const response = await launchApi.getIframeConfig(launchId);
      setConfig(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || '加载配置失败');
    } finally {
      setIsLoading(false);
    }
  };

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

  if (!config || !config.iframe_url) {
    return (
      <div className="flex flex-col items-center justify-center h-full bg-gray-50">
        <AlertCircle className="w-12 h-12 text-yellow-500 mb-4" />
        <p className="text-yellow-600 font-medium mb-2">配置错误</p>
        <p className="text-gray-600 text-sm">未找到有效的 iframe URL</p>
      </div>
    );
  }

  return (
    <div className="h-full w-full">
      <iframe
        src={config.iframe_url}
        className="w-full h-full border-0"
        title="Iframe Workspace"
        sandbox="allow-same-origin allow-scripts allow-forms allow-popups"
        allow="fullscreen"
      />
    </div>
  );
}
