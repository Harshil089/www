import { useState, useEffect } from 'react';
import ChatBot from './ChatBot';
import AlertsPage from './AlertsPage';
import { 
  Menu, Bell, Shield, Activity, Users, AlertTriangle, 
  Terminal, Zap, Lock, Eye, TrendingUp, Server,
  ChevronRight, ExternalLink, BarChart3, Settings, MessageSquare
} from 'lucide-react';

function Dashboard() {
  const [chatOpen, setChatOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [stats, setStats] = useState({
    criticalAlerts: 0,
    activeAgents: 0,
    totalRules: 0,
    incidents: 0,
    connectionStatus: 'connecting'
  });
  const [alerts, setAlerts] = useState([]);
  const [currentTime, setCurrentTime] = useState(new Date());

  // Handle UI actions
  const handleAction = async (actionId) => {
    try {
      const response = await fetch('http://localhost:8000/api/dashboard/agent', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({event: 'click', target_id: actionId, params: {}})
      });
      const plan = await response.json();
      
      console.log('Action plan:', plan);
      
      // Handle navigation
      if (plan.navigate) {
        console.log('Navigate to:', plan.navigate);
        if (plan.navigate === '/alerts') {
          setCurrentPage('alerts');
        }
      }
      
      // Execute HTTP calls
      for (const call of plan.http || []) {
        console.log('Executing API call:', call);
        try {
          const queryString = new URLSearchParams(call.query || {}).toString();
          const url = `http://localhost:8000/api/wazuh${call.url}${queryString ? '?' + queryString : ''}`;
          const res = await fetch(url);
          const data = await res.json();
          console.log(`Data for ${call.id}:`, data);
          
          // Store data for rendering
          window.__wazuhStore = window.__wazuhStore || {};
          window.__wazuhStore[call.id] = data;
        } catch (error) {
          console.error(`Failed to fetch ${call.id}:`, error);
        }
      }
      
      // Show toasts
      if (plan.toasts && plan.toasts.length > 0) {
        plan.toasts.forEach(toast => console.log('Toast:', toast));
      }
      
    } catch (error) {
      console.error('Action failed:', error);
    }
  };

  // Update time every second
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Fetch real stats from backend
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/stats');
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        const data = await response.json();
        setStats({
          criticalAlerts: data.critical_alerts || 0,
          activeAgents: data.active_agents || 0,
          totalRules: data.total_rules || 0,
          incidents: data.critical_alerts > 5 ? Math.floor(data.critical_alerts / 4) : 0,
          connectionStatus: data.connection_status || 'connected'
        });
        setAlerts(data.recent_alerts || []);
      } catch (error) {
        console.error('Backend connection failed:', error);
        setStats({
          criticalAlerts: 0,
          activeAgents: 0,
          totalRules: 0,
          incidents: 0,
          connectionStatus: 'backend_offline'
        });
        setAlerts([]);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 10000);
    return () => clearInterval(interval);
  }, []);

  const getSeverityColor = (severity) => {
    switch (severity.toLowerCase()) {
      case 'critical': return 'bg-red-600 text-white border-red-500';
      case 'high': return 'bg-orange-600 text-white border-orange-500';
      case 'medium': return 'bg-yellow-600 text-black border-yellow-500';
      case 'low': return 'bg-green-600 text-black border-green-500';
      default: return 'bg-gray-600 text-white border-gray-500';
    }
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', { 
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  return (
    <div className="min-h-screen bg-black text-green-400 terminal-text scan-line">
      {/* Top Navigation Bar */}
      <nav className="bg-black/90 backdrop-blur-sm border-b border-green-500/30 sticky top-0 z-40 hacker-border">
        <div className="px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3">
              <Terminal className="w-8 h-8 text-green-400 text-glow pulse-glow" />
              <div>
                <h1 className="text-2xl font-bold text-green-400 text-glow terminal-text">
                  &gt; WAZUH_SOC_SYSTEM
                </h1>
                <p className="text-xs text-green-500/60 terminal-text">
                  Agentic Security Operations Center
                </p>
              </div>
            </div>
            <div className="hidden md:flex items-center gap-6 ml-8">
              <div className="flex items-center gap-2 px-3 py-1 bg-black border border-green-500/30 rounded">
                <div className={`w-2 h-2 rounded-full ${stats.connectionStatus === 'connected' ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`}></div>
                <span className="text-xs text-green-400 terminal-text">
                  {stats.connectionStatus === 'connected' ? 'ONLINE' : 'OFFLINE'}
                </span>
              </div>
              <div className="text-xs text-green-500/70 terminal-text">
                {formatTime(currentTime)}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setChatOpen(!chatOpen)}
              className={`px-4 py-2 border rounded text-sm terminal-text font-semibold transition-all duration-300 hacker-border flex items-center gap-2 ${
                chatOpen 
                  ? 'bg-green-500/20 border-green-500 text-green-300' 
                  : 'bg-green-500/10 border-green-500/50 text-green-400 hover:bg-green-500/20 hover:border-green-500'
              }`}
            >
              <MessageSquare className="w-4 h-4" />
              {chatOpen ? 'HIDE' : 'SHOW'} AI
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      {currentPage === 'dashboard' && (
      <div className={`transition-all duration-300 ${chatOpen ? 'mr-96' : 'mr-0'}`}>
        <div className="p-8 space-y-8">
          {/* Header Section */}
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-3xl font-bold text-green-400 text-glow terminal-text mb-2">
                &gt; SYSTEM_STATUS
              </h2>
              <p className="text-green-500/60 terminal-text">
                Real-time security monitoring and threat detection
              </p>
            </div>
            <div className="flex gap-3">
              <button className="px-4 py-2 bg-black border border-green-500/30 rounded hover:bg-green-500/10 transition hacker-border terminal-text text-sm">
                <Settings className="w-4 h-4 inline mr-2" />
                CONFIG
              </button>
              <button className="px-4 py-2 bg-black border border-green-500/30 rounded hover:bg-green-500/10 transition hacker-border terminal-text text-sm">
                <BarChart3 className="w-4 h-4 inline mr-2" />
                REPORTS
              </button>
            </div>
          </div>

          {/* Stats Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Critical Alerts Card */}
            <div className="bg-black/50 border border-green-500/30 rounded-lg p-6 hacker-border hover:border-green-500/60 transition-all duration-300 group">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-red-500/10 border border-red-500/30 rounded">
                    <AlertTriangle className="w-6 h-6 text-red-400" />
                  </div>
                  <div>
                    <p className="text-xs text-green-500/60 terminal-text uppercase tracking-wider">CRITICAL ALERTS</p>
                    <p className="text-4xl font-bold text-red-400 text-glow mt-1 terminal-text">
                      {stats.criticalAlerts}
                    </p>
                  </div>
                </div>
                <ChevronRight className="w-5 h-5 text-green-500/30 group-hover:text-green-400 transition" />
              </div>
              <div className="h-1 bg-black rounded-full overflow-hidden">
                <div 
                  className="h-full bg-red-500 transition-all duration-500"
                  style={{ width: `${Math.min(stats.criticalAlerts * 10, 100)}%` }}
                ></div>
              </div>
            </div>

            {/* Active Agents Card */}
            <div className="bg-black/50 border border-green-500/30 rounded-lg p-6 hacker-border hover:border-green-500/60 transition-all duration-300 group">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-green-500/10 border border-green-500/30 rounded">
                    <Server className="w-6 h-6 text-green-400" />
                  </div>
                  <div>
                    <p className="text-xs text-green-500/60 terminal-text uppercase tracking-wider">ACTIVE AGENTS</p>
                    <p className="text-4xl font-bold text-green-400 text-glow mt-1 terminal-text">
                      {stats.activeAgents}
                    </p>
                  </div>
                </div>
                <ChevronRight className="w-5 h-5 text-green-500/30 group-hover:text-green-400 transition" />
              </div>
              <div className="flex items-center gap-2 mt-2">
                <div className={`w-2 h-2 rounded-full ${stats.connectionStatus === 'connected' ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`}></div>
                <span className="text-xs text-green-500/60 terminal-text">
                  {stats.connectionStatus === 'connected' ? 'ALL SYSTEMS OPERATIONAL' : 'CONNECTION ISSUES'}
                </span>
              </div>
            </div>

            {/* Total Rules Card */}
            <div className="bg-black/50 border border-green-500/30 rounded-lg p-6 hacker-border hover:border-green-500/60 transition-all duration-300 group">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-blue-500/10 border border-blue-500/30 rounded">
                    <Lock className="w-6 h-6 text-blue-400" />
                  </div>
                  <div>
                    <p className="text-xs text-green-500/60 terminal-text uppercase tracking-wider">TOTAL RULES</p>
                    <p className="text-4xl font-bold text-blue-400 text-glow mt-1 terminal-text">
                      {stats.totalRules}
                    </p>
                  </div>
                </div>
                <ChevronRight className="w-5 h-5 text-green-500/30 group-hover:text-green-400 transition" />
              </div>
              <p className="text-xs text-green-500/60 terminal-text mt-2">
                Detection rules active
              </p>
            </div>

            {/* Open Incidents Card */}
            <div className="bg-black/50 border border-green-500/30 rounded-lg p-6 hacker-border hover:border-green-500/60 transition-all duration-300 group">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-orange-500/10 border border-orange-500/30 rounded">
                    <Zap className="w-6 h-6 text-orange-400" />
                  </div>
                  <div>
                    <p className="text-xs text-green-500/60 terminal-text uppercase tracking-wider">OPEN INCIDENTS</p>
                    <p className="text-4xl font-bold text-orange-400 text-glow mt-1 terminal-text">
                      {stats.incidents}
                    </p>
                  </div>
                </div>
                <ChevronRight className="w-5 h-5 text-green-500/30 group-hover:text-green-400 transition" />
              </div>
              <div className="h-1 bg-black rounded-full overflow-hidden">
                <div 
                  className="h-full bg-orange-500 transition-all duration-500"
                  style={{ width: `${Math.min(stats.incidents * 20, 100)}%` }}
                ></div>
              </div>
            </div>
          </div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Recent Alerts - Large Column */}
            <div className="lg:col-span-2 bg-black/50 border border-green-500/30 rounded-lg hacker-border">
              <div className="p-6 border-b border-green-500/30">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Eye className="w-5 h-5 text-green-400" />
                    <h2 className="text-xl font-bold text-green-400 text-glow terminal-text">
                      &gt; RECENT_ALERTS
                    </h2>
                  </div>
                  <button className="px-4 py-1 bg-black border border-green-500/30 rounded hover:bg-green-500/10 transition hacker-border terminal-text text-sm text-green-400">
                    VIEW_ALL
                  </button>
                </div>
              </div>
              
              <div className="p-6 space-y-4 max-h-[600px] overflow-y-auto">
                {alerts.length > 0 ? alerts.map((alert, index) => {
                  const rule = alert.rule || {};
                  const agent = alert.agent || {};
                  const severity = rule.level >= 10 ? 'Critical' : rule.level >= 7 ? 'High' : rule.level >= 5 ? 'Medium' : 'Low';
                  
                  return (
                    <div 
                      key={index} 
                      className="bg-black/30 border border-green-500/20 rounded-lg p-5 hover:bg-black/50 hover:border-green-500/40 transition-all duration-300 hacker-border group cursor-pointer"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 space-y-3">
                          <div className="flex items-center gap-3 flex-wrap">
                            <span className={`text-xs px-3 py-1 rounded border terminal-text font-semibold ${getSeverityColor(severity)}`}>
                              [{severity}]
                            </span>
                            <span className="text-xs text-green-500/60 terminal-text">
                              RULE_ID: {rule.id || 'N/A'}
                            </span>
                            <span className="text-xs text-green-500/60 terminal-text">
                              LEVEL: {rule.level || 'N/A'}
                            </span>
                          </div>
                          
                          <h3 className="text-green-300 font-semibold terminal-text leading-relaxed">
                            {rule.description || 'Unknown Alert'}
                          </h3>
                          
                          <div className="flex items-center gap-4 text-xs text-green-500/60 terminal-text">
                            <div className="flex items-center gap-2">
                              <Server className="w-3 h-3" />
                              <span>AGENT: {agent.name || 'N/A'}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <Activity className="w-3 h-3" />
                              <span>{alert.timestamp || 'N/A'}</span>
                            </div>
                          </div>
                        </div>
                        
                        <button className="px-4 py-2 bg-green-500/10 border border-green-500/30 rounded hover:bg-green-500/20 hover:border-green-500 transition hacker-border terminal-text text-sm text-green-400 flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          INVESTIGATE
                          <ExternalLink className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  );
                }) : (
                  <div className="text-center py-16 text-green-500/60 terminal-text">
                    <div className="space-y-2">
                      {stats.connectionStatus === 'connected' ? (
                        <>
                          <Terminal className="w-12 h-12 mx-auto mb-4 opacity-50" />
                          <p className="text-lg">No alerts detected</p>
                          <p className="text-sm">System is secure and operational</p>
                        </>
                      ) : stats.connectionStatus === 'backend_offline' ? (
                        <>
                          <AlertTriangle className="w-12 h-12 mx-auto mb-4 text-red-400" />
                          <p className="text-lg text-red-400">Backend server offline</p>
                          <p className="text-sm">Start backend with: python main.py</p>
                        </>
                      ) : stats.connectionStatus === 'disconnected' ? (
                        <>
                          <AlertTriangle className="w-12 h-12 mx-auto mb-4 text-red-400" />
                          <p className="text-lg text-red-400">Wazuh connection failed</p>
                          <p className="text-sm">Check credentials in .env</p>
                        </>
                      ) : (
                        <>
                          <Activity className="w-12 h-12 mx-auto mb-4 animate-pulse" />
                          <p className="text-lg">Connecting to Wazuh...</p>
                          <p className="text-sm">Establishing secure connection</p>
                        </>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Sidebar - Quick Actions & System Health */}
            <div className="space-y-6">
              {/* Quick Actions */}
              <div className="bg-black/50 border border-green-500/30 rounded-lg hacker-border">
                <div className="p-6 border-b border-green-500/30">
                  <div className="flex items-center gap-3">
                    <Zap className="w-5 h-5 text-green-400" />
                    <h3 className="text-lg font-bold text-green-400 text-glow terminal-text">
                      &gt; QUICK_ACTIONS
                    </h3>
                  </div>
                </div>
                <div className="p-6 space-y-3">
                  <button 
                    data-action="view_all_alerts"
                    onClick={() => handleAction('view_all_alerts')}
                    className="w-full text-left p-4 bg-black/30 border border-green-500/20 rounded hover:bg-black/50 hover:border-green-500/40 transition hacker-border terminal-text group"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-green-400 group-hover:text-green-300">VIEW_ALL_ALERTS</span>
                      <ChevronRight className="w-4 h-4 text-green-500/30 group-hover:text-green-400 transition" />
                    </div>
                  </button>
                  <button 
                    data-action="agent_status"
                    onClick={() => handleAction('agent_status')}
                    className="w-full text-left p-4 bg-black/30 border border-green-500/20 rounded hover:bg-black/50 hover:border-green-500/40 transition hacker-border terminal-text group"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-green-400 group-hover:text-green-300">AGENT_STATUS</span>
                      <ChevronRight className="w-4 h-4 text-green-500/30 group-hover:text-green-400 transition" />
                    </div>
                  </button>
                  <button 
                    data-action="rule_management"
                    onClick={() => handleAction('rule_management')}
                    className="w-full text-left p-4 bg-black/30 border border-green-500/20 rounded hover:bg-black/50 hover:border-green-500/40 transition hacker-border terminal-text group"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-green-400 group-hover:text-green-300">RULE_MANAGEMENT</span>
                      <ChevronRight className="w-4 h-4 text-green-500/30 group-hover:text-green-400 transition" />
                    </div>
                  </button>
                  <button 
                    data-action="threat_intelligence"
                    onClick={() => handleAction('threat_intelligence')}
                    className="w-full text-left p-4 bg-black/30 border border-green-500/20 rounded hover:bg-black/50 hover:border-green-500/40 transition hacker-border terminal-text group"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-green-400 group-hover:text-green-300">THREAT_INTELLIGENCE</span>
                      <ChevronRight className="w-4 h-4 text-green-500/30 group-hover:text-green-400 transition" />
                    </div>
                  </button>
                </div>
              </div>

              {/* System Health */}
              <div className="bg-black/50 border border-green-500/30 rounded-lg hacker-border">
                <div className="p-6 border-b border-green-500/30">
                  <div className="flex items-center gap-3">
                    <Activity className="w-5 h-5 text-green-400" />
                    <h3 className="text-lg font-bold text-green-400 text-glow terminal-text">
                      &gt; SYSTEM_HEALTH
                    </h3>
                  </div>
                </div>
                <div className="p-6 space-y-4">
                  <div className="flex justify-between items-center py-2 border-b border-green-500/10">
                    <span className="text-green-500/60 terminal-text text-sm">WAZUH_MANAGER</span>
                    <span className={`terminal-text text-sm font-semibold ${stats.connectionStatus === 'connected' ? 'text-green-400' : 'text-red-400'}`}>
                      {stats.connectionStatus === 'connected' ? '[ONLINE]' : 
                       stats.connectionStatus === 'backend_offline' ? '[OFFLINE]' :
                       stats.connectionStatus === 'disconnected' ? '[AUTH_FAIL]' : '[CONNECTING]'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-green-500/10">
                    <span className="text-green-500/60 terminal-text text-sm">ACTIVE_AGENTS</span>
                    <span className="text-green-400 terminal-text text-sm font-semibold">
                      {stats.activeAgents}/{stats.activeAgents}
                    </span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-green-500/10">
                    <span className="text-green-500/60 terminal-text text-sm">API_STATUS</span>
                    <span className={`terminal-text text-sm font-semibold ${stats.connectionStatus === 'connected' ? 'text-green-400' : 'text-red-400'}`}>
                      {stats.connectionStatus === 'connected' ? '[HEALTHY]' : '[ERROR]'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center py-2">
                    <span className="text-green-500/60 terminal-text text-sm">UPTIME</span>
                    <span className="text-green-400 terminal-text text-sm font-semibold">
                      {formatTime(currentTime)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Example Queries */}
              <div className="bg-black/50 border border-green-500/30 rounded-lg hacker-border">
                <div className="p-6 border-b border-green-500/30">
                  <div className="flex items-center gap-3">
                    <Terminal className="w-5 h-5 text-green-400" />
                    <h3 className="text-lg font-bold text-green-400 text-glow terminal-text">
                      &gt; TRY_QUERIES
                    </h3>
                  </div>
                </div>
                <div className="p-6 space-y-3">
                  <div className="text-xs text-green-500/60 terminal-text font-mono p-3 bg-black/30 border border-green-500/10 rounded">
                    &gt; "Show critical alerts"
                  </div>
                  <div className="text-xs text-green-500/60 terminal-text font-mono p-3 bg-black/30 border border-green-500/10 rounded">
                    &gt; "Triage alerts MITRE ATT&CK"
                  </div>
                  <div className="text-xs text-green-500/60 terminal-text font-mono p-3 bg-black/30 border border-green-500/10 rounded">
                    &gt; "Generate compliance report"
                  </div>
                  <div className="text-xs text-green-500/60 terminal-text font-mono p-3 bg-black/30 border border-green-500/10 rounded">
                    &gt; "Show FIM events"
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      )}

      {/* Conditional Page Rendering */}
      {currentPage === 'alerts' && (
        <AlertsPage onBack={() => setCurrentPage('dashboard')} />
      )}
      
      {/* Chatbot Sidebar */}
      <ChatBot isOpen={chatOpen} onToggle={() => setChatOpen(!chatOpen)} />
    </div>
  );
}

export default Dashboard;
