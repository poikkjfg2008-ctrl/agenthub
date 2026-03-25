/** Resource card component */

import { MessageSquare, BookOpen, Bot, Zap } from 'lucide-react';
import type { Resource } from '../types';

interface ResourceCardProps {
  resource: Resource;
  onLaunch: (resource: Resource) => void;
}

export function ResourceCard({ resource, onLaunch }: ResourceCardProps) {
  const getIcon = () => {
    if (resource.type === 'direct_chat' || resource.type === 'skill_chat') {
      return <MessageSquare className="w-6 h-6" />;
    } else if (resource.type === 'kb_websdk') {
      return <BookOpen className="w-6 h-6" />;
    } else if (resource.type === 'agent_websdk') {
      return <Bot className="w-6 h-6" />;
    }
    return <Zap className="w-6 h-6" />;
  };

  const getBadgeColor = () => {
    if (resource.type === 'direct_chat') {
      return 'bg-blue-100 text-blue-800';
    } else if (resource.type === 'skill_chat') {
      return 'bg-purple-100 text-purple-800';
    } else if (resource.type === 'kb_websdk') {
      return 'bg-green-100 text-green-800';
    } else if (resource.type === 'agent_websdk') {
      return 'bg-orange-100 text-orange-800';
    }
    return 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-lg ${getBadgeColor()}`}>
            {getIcon()}
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{resource.name}</h3>
            <span className={`text-xs px-2 py-1 rounded-full ${getBadgeColor()}`}>
              {resource.type}
            </span>
          </div>
        </div>
      </div>

      <p className="text-gray-600 text-sm mb-4 line-clamp-2">
        {resource.description}
      </p>

      <div className="flex items-center justify-between">
        <div className="flex flex-wrap gap-1">
          {resource.tags.slice(0, 3).map((tag) => (
            <span
              key={tag}
              className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded"
            >
              #{tag}
            </span>
          ))}
        </div>

        <button
          onClick={() => onLaunch(resource)}
          className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors font-medium text-sm"
        >
          启动
        </button>
      </div>
    </div>
  );
}
