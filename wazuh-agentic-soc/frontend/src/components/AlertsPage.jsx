import { useState, useEffect } from 'react';
import { ArrowLeft, AlertTriangle, Clock, Shield, Filter, Search } from 'lucide-react';

function AlertsPage({ onBack }) {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/wazuh/alerts?limit=100');
      const data = await response.json();
      
      if (data.data && data.data.affected_items) {
        setAlerts(data.data.affected_items);
      }
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (level) => {
    if (level >= 10) return 'bg-red-600 text-white border-red-500';
    if (level >= 7) return 'bg-orange-600 text-white border-orange-500';
    if (level >= 5) return 'bg-yellow-600 text-black border-yellow-500';
    return 'bg-green-600 text-black border-green-500';
  };

  const getSeverityLabel = (level) => {
    if (level >= 10) return 'Critical';
    if (level >= 7) return 'High';
    if (level >= 5) return 'Medium';
    return 'Low';
  };

  const filteredAlerts = alerts.filter(alert => {
    const rule = alert.rule || {};
    const matchesFilter = filter === 'all' || 
      (filter === 'critical' && rule.level >= 10) ||
      (filter === 'high' && rule.level >= 7 && rule.level < 10) ||
      (filter === 'medium' && rule.level >= 5 && rule.level < 7);
    
    const matchesSearch = !searchTerm || 
      rule.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      alert.agent?.name?.toLowerCase().includes(searchTerm.toLowerCase());
    
    return matchesFilter && matchesSearch;
  });

  return (
    <div className="min-h-screen bg-black text-green-400 terminal-text">
      {/* Header */}
      <div className="bg-black/90 backdrop-blur-sm border-b border-green-500/30 sticky top-0 z-40 hacker-border">
        <div className="px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={onBack}
              className="p-2 hover:bg-green-500/10 rounded transition hacker-border"
            >
              <ArrowLeft className="w-5 h-5 text-green-400" />
            </button>
            <div className="flex items-center gap-3">
              <AlertTriangle className="w-8 h-8 text-red-400 text-glow pulse-glow" />
              <div>
                <h1 className="text-2xl font-bold text-green-400 text-glow terminal-text">
                  &gt; SECURITY_ALERTS
                </h1>
                <p className="text-xs text-green-500/60 terminal-text">
                  Real-time threat detection and monitoring
                </p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1 bg-black border border-green-500/30 rounded">
              <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
              <span className="text-xs text-green-400 terminal-text">LIVE</span>
            </div>
            <button
              onClick={fetchAlerts}
              className="px-4 py-2 bg-green-500/10 border border-green-500/50 rounded hover:bg-green-500/20 transition hacker-border terminal-text text-sm"
            >
              REFRESH
            </button>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="p-6 border-b border-green-500/30">
        <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
          <div className="flex items-center gap-4">
            <Filter className="w-5 h-5 text-green-400" />
            <div className="flex gap-2">
              {['all', 'critical', 'high', 'medium'].map(f => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`px-3 py-1 rounded text-xs terminal-text transition ${
                    filter === f 
                      ? 'bg-green-500/20 border border-green-500/50 text-green-300' 
                      : 'bg-black/30 border border-green-500/20 text-green-500/60 hover:text-green-400'
                  }`}
                >
                  {f.toUpperCase()}
                </button>
              ))}
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Search className="w-4 h-4 text-green-500/60" />
            <input
              type="text"
              placeholder="Search alerts..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-black border border-green-500/30 text-green-400 rounded px-3 py-1 text-sm terminal-text focus:outline-none focus:border-green-500 hacker-border"
            />
          </div>
        </div>
      </div>

      {/* Alerts List */}
      <div className="p-6">
        {loading ? (
          <div className="text-center py-16">
            <div className="w-12 h-12 border-2 border-green-500/30 border-t-green-400 rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-green-500/60 terminal-text">Loading alerts...</p>
          </div>
        ) : filteredAlerts.length === 0 ? (
          <div className="text-center py-16 text-green-500/60 terminal-text">
            <Shield className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p className="text-lg">No alerts found</p>
            <p className="text-sm">System is secure or no alerts match your filters</p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-green-400 terminal-text">
                Found {filteredAlerts.length} alerts
              </h2>
            </div>
            
            {filteredAlerts.map((alert, index) => {
              const rule = alert.rule || {};
              const agent = alert.agent || {};
              const severity = getSeverityLabel(rule.level);
              
              return (
                <div 
                  key={index}
                  className="bg-black/50 border border-green-500/30 rounded-lg p-6 hover:bg-black/70 hover:border-green-500/50 transition-all duration-300 hacker-border group"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 space-y-3">
                      <div className="flex items-center gap-3 flex-wrap">
                        <span className={`text-xs px-3 py-1 rounded border terminal-text font-semibold ${getSeverityColor(rule.level)}`}>
                          [{severity}]
                        </span>
                        <span className="text-xs text-green-500/60 terminal-text">
                          RULE_ID: {rule.id || 'N/A'}
                        </span>
                        <span className="text-xs text-green-500/60 terminal-text">
                          LEVEL: {rule.level || 'N/A'}
                        </span>
                        {rule.mitre && (
                          <span className="text-xs text-blue-400 terminal-text">
                            MITRE: {rule.mitre.technique || rule.mitre.tactic}
                          </span>
                        )}
                      </div>
                      
                      <h3 className="text-green-300 font-semibold terminal-text leading-relaxed">
                        {rule.description || 'Unknown Alert'}
                      </h3>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-green-500/60 terminal-text">
                        <div className="flex items-center gap-2">
                          <Shield className="w-3 h-3" />
                          <span>AGENT: {agent.name || 'N/A'}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Clock className="w-3 h-3" />
                          <span>{alert.timestamp || 'N/A'}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <AlertTriangle className="w-3 h-3" />
                          <span>IP: {agent.ip || 'N/A'}</span>
                        </div>
                      </div>
                      
                      {alert.full_log && (
                        <details className="mt-3">
                          <summary className="text-xs text-green-500/60 cursor-pointer hover:text-green-400 terminal-text">
                            Show full log
                          </summary>
                          <pre className="mt-2 text-xs bg-black/30 border border-green-500/20 rounded p-3 text-green-400 terminal-text overflow-x-auto">
                            {alert.full_log}
                          </pre>
                        </details>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

export default AlertsPage;