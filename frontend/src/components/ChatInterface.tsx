/** Chat interface component for native/skill conversations with Markdown support */

import { useState, useEffect, useRef, useCallback } from 'react';
import { Send, Loader2, RefreshCw, Copy, Check } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeHighlight from 'rehype-highlight';
import { sessionApi } from '../api';
import type { Message, Resource } from '../types';

// Import KaTeX styles for math rendering
import 'katex/dist/katex.min.css';
import 'highlight.js/styles/github.css';

interface ChatInterfaceProps {
  sessionId: string;
  resource?: Resource;
  onRestart?: () => void;
}

// Strip empty lines from text
const stripText = (text: string): string => {
  return text
    .split('\n')
    .map((line) => line.trimEnd())
    .join('\n')
    .trim();
};

// Copy button component for code blocks
function CopyButton({ code }: { code: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <button
      onClick={handleCopy}
      className="absolute top-2 right-2 p-1.5 rounded bg-gray-700 hover:bg-gray-600 text-gray-300 transition-colors"
      title={copied ? '已复制' : '复制代码'}
    >
      {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
    </button>
  );
}

export function ChatInterface({ sessionId, resource, onRestart }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Load message history
  useEffect(() => {
    loadMessages();
  }, [sessionId]);

  // Auto-scroll to bottom
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [inputText]);

  const loadMessages = async () => {
    try {
      setIsLoadingHistory(true);
      const response = await sessionApi.getMessages(sessionId);
      // Strip all messages
      const strippedMessages = response.data.map((msg: Message) => ({
        ...msg,
        text: stripText(msg.text),
      }));
      setMessages(strippedMessages);
    } catch (error) {
      console.error('Failed to load messages:', error);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async () => {
    const trimmedInput = inputText.trim();
    if (!trimmedInput || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      text: trimmedInput,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }

    try {
      const response = await sessionApi.sendMessage(sessionId, trimmedInput);
      const strippedResponse = stripText(response.data.response);

      const assistantMessage: Message = {
        role: 'assistant',
        text: strippedResponse,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);

      const errorMessage: Message = {
        role: 'system',
        text: '消息发送失败，请重试',
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const renderMarkdown = useCallback((content: string) => {
    return (
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex, rehypeHighlight]}
        components={{
          // Code block with copy button
          code({ className, children, ...props }: any) {
            const match = /language-(\w+)/.exec(className || '');
            const isInline = !className;
            const code = String(children).replace(/\n$/, '');

            if (!isInline) {
              return (
                <div className="relative my-3">
                  <div className="flex items-center justify-between px-4 py-2 bg-gray-800 text-gray-300 text-xs rounded-t-lg">
                    <span>{match ? match[1] : 'code'}</span>
                    <CopyButton code={code} />
                  </div>
                  <pre className="bg-gray-900 text-gray-100 p-4 rounded-b-lg overflow-x-auto text-sm">
                    <code className={className} {...props}>
                      {children}
                    </code>
                  </pre>
                </div>
              );
            }

            return (
              <code
                className="bg-gray-100 text-gray-800 px-1.5 py-0.5 rounded text-sm font-mono"
                {...props}
              >
                {children}
              </code>
            );
          },
          // Table styling
          table({ children }) {
            return (
              <div className="overflow-x-auto my-4">
                <table className="min-w-full border-collapse border border-gray-300">
                  {children}
                </table>
              </div>
            );
          },
          thead({ children }) {
            return <thead className="bg-gray-100">{children}</thead>;
          },
          th({ children }) {
            return (
              <th className="border border-gray-300 px-4 py-2 text-left font-semibold text-gray-700">
                {children}
              </th>
            );
          },
          td({ children }) {
            return (
              <td className="border border-gray-300 px-4 py-2 text-gray-600">
                {children}
              </td>
            );
          },
          // List styling
          ul({ children }) {
            return <ul className="list-disc pl-6 my-2 space-y-1">{children}</ul>;
          },
          ol({ children }) {
            return <ol className="list-decimal pl-6 my-2 space-y-1">{children}</ol>;
          },
          li({ children }) {
            return <li className="text-gray-700">{children}</li>;
          },
          // Heading styling
          h1({ children }) {
            return <h1 className="text-2xl font-bold text-gray-900 my-4">{children}</h1>;
          },
          h2({ children }) {
            return <h2 className="text-xl font-bold text-gray-800 my-3">{children}</h2>;
          },
          h3({ children }) {
            return <h3 className="text-lg font-bold text-gray-800 my-2">{children}</h3>;
          },
          // Paragraph styling
          p({ children }) {
            return <p className="my-2 text-gray-700 leading-relaxed">{children}</p>;
          },
          // Blockquote styling
          blockquote({ children }) {
            return (
              <blockquote className="border-l-4 border-primary-300 pl-4 my-3 text-gray-600 italic bg-gray-50 py-2 pr-4 rounded-r">
                {children}
              </blockquote>
            );
          },
          // Link styling
          a({ href, children }) {
            return (
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary-600 hover:text-primary-700 underline"
              >
                {children}
              </a>
            );
          },
          // Horizontal rule
          hr() {
            return <hr className="my-4 border-gray-200" />;
          },
        }}
      >
        {content}
      </ReactMarkdown>
    );
  }, []);

  return (
    <div className="flex flex-col h-full bg-gradient-to-b from-gray-50 to-white">
      {/* Header with resource info */}
      {resource && (
        <div className="px-6 py-4 border-b bg-white flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-gray-900">{resource.name}</h2>
            <p className="text-sm text-gray-500">{resource.description}</p>
          </div>
          {onRestart && (
            <button
              onClick={onRestart}
              className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              新对话
            </button>
          )}
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-6 space-y-6">
        {isLoadingHistory ? (
          <div className="flex justify-center items-center h-full">
            <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
          </div>
        ) : messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mb-4">
              <Send className="w-8 h-8 text-primary-500" />
            </div>
            <p className="text-lg font-medium mb-2">开始新的对话</p>
            <p className="text-sm text-gray-400">在下方输入框中输入您的问题</p>
            {resource?.config?.starter_prompts && (
              <div className="mt-6 flex flex-wrap gap-2 justify-center max-w-md">
                {resource.config.starter_prompts.map((prompt, idx) => (
                  <button
                    key={idx}
                    onClick={() => setInputText(prompt)}
                    className="px-4 py-2 bg-white border border-gray-200 rounded-full text-sm text-gray-600 hover:border-primary-300 hover:text-primary-600 transition-colors"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            )}
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${
                message.role === 'user'
                  ? 'justify-end'
                  : message.role === 'system'
                  ? 'justify-center'
                  : 'justify-start'
              }`}
            >
              <div
                className={`max-w-[85%] sm:max-w-[75%] ${
                  message.role === 'user'
                    ? 'message-user'
                    : message.role === 'assistant'
                    ? 'message-assistant'
                    : 'message-system'
                }`}
              >
                {message.role === 'user' && (
                  <span className="text-xs opacity-70 mb-1 block font-medium">您</span>
                )}
                {message.role === 'assistant' && (
                  <span className="text-xs text-gray-500 mb-1 block font-medium">AI 助手</span>
                )}
                
                {/* Render markdown for assistant messages, plain text for user */}
                {message.role === 'assistant' ? (
                  <div className="markdown-content">{renderMarkdown(message.text)}</div>
                ) : (
                  <p className="whitespace-pre-wrap break-words">{message.text}</p>
                )}
                
                {message.timestamp && (
                  <span className="text-xs opacity-50 mt-2 block">
                    {new Date(message.timestamp).toLocaleTimeString('zh-CN', {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </span>
                )}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area - Larger and more prominent */}
      <div className="border-t bg-white px-4 sm:px-6 py-4">
        <div className="max-w-4xl mx-auto">
          <div className="relative flex items-end gap-3 bg-gray-50 border border-gray-200 rounded-2xl p-3 focus-within:border-primary-400 focus-within:ring-2 focus-within:ring-primary-100 transition-all">
            <textarea
              ref={textareaRef}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="输入消息... (Enter 发送，Shift+Enter 换行)"
              className="flex-1 bg-transparent border-0 resize-none focus:outline-none text-gray-800 placeholder-gray-400 min-h-[56px] max-h-[200px] py-2 px-1"
              rows={2}
              disabled={isLoading}
            />
            <button
              onClick={handleSendMessage}
              disabled={isLoading || !inputText.trim()}
              className="mb-1 px-5 py-2.5 bg-primary-500 text-white rounded-xl hover:bg-primary-600 transition-all disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2 font-medium shadow-sm hover:shadow"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <span>发送</span>
                  <Send className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
          <p className="text-xs text-gray-400 mt-2 text-center">
            AI 生成的内容仅供参考，请核实重要信息
          </p>
        </div>
      </div>
    </div>
  );
}
