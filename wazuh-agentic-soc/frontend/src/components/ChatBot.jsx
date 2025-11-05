import { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Terminal, X, MessageSquare } from 'lucide-react';

function ChatBot({ isOpen, onToggle }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [ws, setWs] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (!isOpen) return;

    // Connect WebSocket
    const socket = new WebSocket('ws://localhost:8000/ws/chat');
    
    socket.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
    };
    
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages(prev => [...prev, {
        type: 'bot',
        content: data.content
      }]);
      setIsLoading(false);
    };
    
    socket.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };
    
    setWs(socket);
    
    return () => {
      socket.close();
    };
  }, [isOpen]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = () => {
    if (!input.trim() || !ws || !isConnected || isLoading) return;
    
    const userMessage = input.trim();
    
    // Add user message
    setMessages(prev => [...prev, {
      type: 'user',
      content: userMessage
    }]);
    
    setIsLoading(true);
    
    // Send to backend
    ws.send(JSON.stringify({ query: userMessage }));
    setInput('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed right-0 top-0 h-screen w-96 bg-black/95 backdrop-blur-sm shadow-2xl flex flex-col border-l border-green-500/30 z-50 hacker-border">
      {/* Header */}
      <div className="bg-black border-b border-green-500/30 p-4 flex items-center justify-between hacker-border">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-green-500/10 border border-green-500/30 rounded">
            <Bot className="w-5 h-5 text-green-400" />
          </div>
          <div>
            <h2 className="text-green-400 font-bold text-lg terminal-text text-glow">
              &gt; AI_ASSISTANT
            </h2>
            <p className="text-xs text-green-500/60 terminal-text">
              SOC Orchestrator v2.0
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`}></div>
          <span className="text-xs text-green-500/60 terminal-text">
            {isConnected ? 'CONNECTED' : 'DISCONNECTED'}
          </span>
          <button 
            onClick={onToggle}
            className="p-1 hover:bg-green-500/10 rounded transition"
          >
            <X className="w-4 h-4 text-green-500/60 hover:text-green-400" />
          </button>
        </div>
      </div>
      
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-black/50">
        {messages.length === 0 && (
          <div className="text-center py-8 text-green-500/60 terminal-text">
            <Terminal className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p className="text-sm mb-2">Agentic SOC Assistant Ready</p>
            <p className="text-xs">Ask me about alerts, rules, agents, or threats...</p>
          </div>
        )}
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`flex gap-3 max-w-[85%] ${msg.type === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`w-8 h-8 rounded border flex items-center justify-center flex-shrink-0 ${
                msg.type === 'user' 
                  ? 'bg-green-500/20 border-green-500/50' 
                  : 'bg-black border-green-500/30'
              }`}>
                {msg.type === 'user' ? 
                  <User className="w-4 h-4 text-green-400" /> : 
                  <Bot className="w-4 h-4 text-green-400" />
                }
              </div>
              <div className={`rounded-lg p-4 border terminal-text ${
                msg.type === 'user' 
                  ? 'bg-green-500/10 border-green-500/30 text-green-300' 
                  : 'bg-black/50 border-green-500/20 text-green-400'
              }`}>
                <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.content}</p>
              </div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input */}
      <div className="p-4 border-t border-green-500/30 bg-black/50">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="> Type your query..."
            className="flex-1 bg-black border border-green-500/30 text-green-400 rounded-lg px-4 py-3 focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500 resize-none terminal-text text-sm hacker-border"
            rows="3"
            disabled={!isConnected}
          />
          <button
            onClick={sendMessage}
            disabled={!isConnected || !input.trim()}
            className="bg-green-500/10 border border-green-500/50 text-green-400 rounded-lg px-4 py-3 hover:bg-green-500/20 hover:border-green-500 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed hacker-border flex items-center justify-center"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        {!isConnected && (
          <p className="text-red-400 text-xs mt-2 terminal-text text-center">
            [ERROR] Disconnected from server
          </p>
        )}
        <div className="mt-2 text-xs text-green-500/40 terminal-text text-center">
          Press ENTER to send • SHIFT+ENTER for new line
        </div>
      </div>
    </div>
  );
}

export default ChatBot;
