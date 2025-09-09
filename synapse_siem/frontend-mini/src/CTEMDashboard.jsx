import { useState, useEffect, useRef } from 'react';
import { apiClient } from './apiClient';
import './CTEMDashboard.css';

export default function CTEMDashboard() {
  const [analysis, setAnalysis] = useState(null);
  const [availableFiles, setAvailableFiles] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [maturityScore, setMaturityScore] = useState(0);
  const fileInputRef = useRef(null);

  useEffect(() => {
    loadAvailableFiles();
    loadHistory();
  }, []);

  const loadAvailableFiles = async () => {
    try {
      const data = await apiClient.getAvailableFiles();
      setAvailableFiles(data.available_files || []);
    } catch (err) {
      console.error('Error loading files:', err);
    }
  };

  const loadHistory = async () => {
    try {
      const historyData = await apiClient.getHistory();
      setHistory(historyData);
    } catch (err) {
      console.error('Error loading history:', err);
    }
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    try {
      console.log('Selected files:', selectedFiles);
      const result = await apiClient.runAnalysis(selectedFiles);
      console.log('Analysis result:', result);
      setAnalysis(result);
      calculateMaturityScore(result);
      
      // Mostra warnings se houver
      if (result.warnings && result.warnings.length > 0) {
        console.warn('Analysis warnings:', result.warnings);
      }
      
      loadHistory(); // Refresh history
    } catch (err) {
      console.error('Analysis error:', err);
      let errorMessage = 'Erro na análise';
      
      if (err.response?.data?.error) {
        errorMessage = err.response.data.error;
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    setError(null);
    try {
      await apiClient.uploadLog(file);
      loadAvailableFiles(); // Refresh file list
      setError(null);
    } catch (err) {
      setError(err.response?.data?.error || 'Erro no upload');
    } finally {
      setLoading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const toggleFileSelection = (fileId) => {
    setSelectedFiles(prev => 
      prev.includes(fileId) 
        ? prev.filter(id => id !== fileId)
        : [...prev, fileId]
    );
  };

  const handleDeleteFile = async (fileId) => {
    if (!confirm('Tem certeza que deseja excluir este arquivo?')) return;
    
    try {
      await apiClient.deleteFile(fileId);
      loadAvailableFiles(); // Refresh file list
      // Remove from selected files if it was selected
      setSelectedFiles(prev => prev.filter(id => id !== fileId));
    } catch (err) {
      setError('Erro ao excluir arquivo');
    }
  };

  const calculateMaturityScore = (analysisData) => {
    if (!analysisData) return;
    
    const totalFindings = analysisData.total_findings || 0;
    const criticalFindings = analysisData.findings?.filter(f => f.severity === 'critical').length || 0;
    const highFindings = analysisData.findings?.filter(f => f.severity === 'high').length || 0;
    
    // Score calculation (0-100)
    let score = 100;
    
    // Penalize based on findings
    score -= criticalFindings * 15; // -15 per critical
    score -= highFindings * 8;     // -8 per high
    score -= (totalFindings - criticalFindings - highFindings) * 2; // -2 per medium/low
    
    setMaturityScore(Math.max(0, Math.min(100, score)));
  };

  const getSecurityStats = () => {
    if (!analysis) return { total: 0, critical: 0, high: 0, medium: 0, low: 0 };
    
    const findings = analysis.findings || [];
    return {
      total: findings.length,
      critical: findings.filter(f => f.severity === 'critical').length,
      high: findings.filter(f => f.severity === 'high').length,
      medium: findings.filter(f => f.severity === 'medium').length,
      low: findings.filter(f => f.severity === 'low').length,
    };
  };

  const getSeverityColor = (severity) => {
    const colors = {
      critical: '#dc2626',
      high: '#ea580c',
      medium: '#d97706',
      low: '#65a30d'
    };
    return colors[severity] || '#6b7280';
  };

  const stats = getSecurityStats();

  return (
    <div className="ctem-dashboard">
      {/* Left Sidebar */}
      <div className="sidebar">
        <div className="sidebar-section">
          <h3>📊 Analysis Actions</h3>
          
          <div className="sidebar-actions">
            <div className="upload-section">
              <input
                ref={fileInputRef}
                type="file"
                accept=".log,.txt,.json"
                onChange={handleFileUpload}
                disabled={loading}
                className="file-input"
                id="file-upload"
              />
              <label htmlFor="file-upload" className={`sidebar-btn upload ${loading ? 'disabled' : ''}`}>
                📁 Import Log File
              </label>
            </div>
            
            <button 
              onClick={handleAnalyze} 
              disabled={loading}
              className="sidebar-btn analyze"
            >
              {loading ? '⏳ Analyzing...' : '🔍 Run Log Analysis'}
            </button>
          </div>
        </div>

        <div className="sidebar-section">
          <h3>🔧 Advanced Features</h3>
          
          <div className="sidebar-actions">
            <button className="sidebar-btn todo" disabled>
              📋 Imported Logs
              <span className="todo-badge">TODO</span>
            </button>
            <button className="sidebar-btn todo" disabled>
              🔍 Regex Analysis
              <span className="todo-badge">TODO</span>
            </button>
            
            <button className="sidebar-btn todo" disabled>
              🤖 AI Analysis
              <span className="todo-badge">TODO</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-dashboard">
        <div className="dashboard-header">
          <div>
            <h1>🔍 SYNAPSE SIEM Dashboard</h1>
            <p>System Information and Event Management para Análise de Logs</p>
          </div>
          <div className="header-stats">
            <div className="stat-item">
              <div className="stat-value">{maturityScore}</div>
              <div className="stat-label">Security Score</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{stats.total}</div>
              <div className="stat-label">Total Findings</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{history.length}</div>
              <div className="stat-label">Analyses</div>
            </div>
          </div>
        </div>

        {error && (
          <div className="error-message">
            ❌ {error}
          </div>
        )}

      {/* KPI Cards */}
      <div className="kpi-grid">
        <div className="kpi-card security-maturity">
          <div className="kpi-header">
            <span className="kpi-icon">🛡️</span>
            <span className="kpi-title">Total Findings</span>
          </div>
          <div className="kpi-content">
            <div className="kpi-value">{stats.total}</div>
            <div className="kpi-trend">
              <span className="trend-icon">📊</span>
              <span>Security findings detected</span>
            </div>
            <div className="kpi-footer">
              <span>Last analysis: {analysis ? 'Recent' : 'None'}</span>
            </div>
          </div>
        </div>

        <div className="kpi-card medium-findings">
          <div className="kpi-header">
            <span className="kpi-icon">🟡</span>
            <span className="kpi-title">Medium Findings</span>
          </div>
          <div className="kpi-content">
            <div className="kpi-value">{stats.medium}</div>
            <div className="kpi-subtitle">Medium severity issues</div>
            <div className="kpi-footer">
              <span>Percentage: {stats.total > 0 ? Math.round((stats.medium / stats.total) * 100) : 0}%</span>
            </div>
          </div>
        </div>

        <div className="kpi-card high-findings">
          <div className="kpi-header">
            <span className="kpi-icon">🟠</span>
            <span className="kpi-title">High Findings</span>
          </div>
          <div className="kpi-content">
            <div className="kpi-value">{stats.high}</div>
            <div className="kpi-subtitle">High priority issues</div>
            <div className="kpi-footer">
              <span>Percentage: {stats.total > 0 ? Math.round((stats.high / stats.total) * 100) : 0}%</span>
            </div>
          </div>
        </div>

        <div className="kpi-card critical-findings">
          <div className="kpi-header">
            <span className="kpi-icon">🔴</span>
            <span className="kpi-title">Critical Findings</span>
          </div>
          <div className="kpi-content">
            <div className="kpi-value">{stats.critical}</div>
            <div className="kpi-subtitle">Require immediate attention</div>
            <div className="kpi-footer">
              <span>Percentage: {stats.total > 0 ? Math.round((stats.critical / stats.total) * 100) : 0}%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        <div className="content-left">
          {/* Imported Files Section */}
          <div className="files-section">
            <h2>📁 Imported Log Files ({availableFiles.length})</h2>
            {availableFiles.length === 0 ? (
              <div className="no-files">
                <p>Nenhum arquivo importado ainda.</p>
                <p>Use o botão "Import Log File" na sidebar para começar.</p>
              </div>
            ) : (
              <div className="files-list">
                {availableFiles.map((file) => (
                  <div 
                    key={file.id} 
                    className={`file-item ${selectedFiles.includes(file.id) ? 'selected' : ''}`}
                    onClick={() => toggleFileSelection(file.id)}
                  >
                    <div className="file-checkbox">
                      <input 
                        type="checkbox" 
                        checked={selectedFiles.includes(file.id)}
                        onChange={() => {}}
                      />
                    </div>
                    <div className="file-info">
                      <div className="file-name">{file.filename}</div>
                      <div className="file-details">
                        {(file.size / 1024).toFixed(1)} KB • {file.total_lines} lines
                      </div>
                    </div>
                    <div className="file-date">
                      {new Date(file.uploaded_at).toLocaleDateString()}
                    </div>
                    <button 
                      className="delete-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteFile(file.id);
                      }}
                      title="Excluir arquivo"
                    >
                      🗑️
                    </button>
                  </div>
                ))}
              </div>
            )}
            
            {availableFiles.length > 0 && (
              <div className="selection-info">
                <span>{selectedFiles.length} de {availableFiles.length} arquivos selecionados</span>
                <button 
                  onClick={() => setSelectedFiles(availableFiles.map(f => f.id))}
                  className="select-all-btn"
                >
                  Selecionar Todos
                </button>
              </div>
            )}
          </div>
          {/* Analysis Control */}
          <div className="analysis-section">
            <h2>📊 Log Analysis</h2>
            <div className="analysis-controls">
              <button 
                onClick={handleAnalyze} 
                disabled={loading}
                className="btn-analyze"
              >
                {loading ? '⏳ Analyzing...' : '🔍 Run Security Analysis'}
              </button>
            </div>
            
            {error && (
              <div className="error-message">
                ❌ {error}
              </div>
            )}
          </div>

          {/* Security Trends */}
          {analysis && (
            <div className="trends-section">
              <h2>🔍 Security Findings Overview</h2>
              <div className="severity-breakdown">
                {Object.entries(analysis.summary?.by_severity || {}).map(([severity, count]) => (
                  <div key={severity} className="severity-item">
                    <div 
                      className="severity-bar"
                      style={{ 
                        backgroundColor: getSeverityColor(severity),
                        width: `${(count / stats.total) * 100}%`
                      }}
                    ></div>
                    <div className="severity-info">
                      <span className="severity-name">{severity}</span>
                      <span className="severity-count">{count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="content-right">
          {/* Recent Findings */}
          {analysis && analysis.findings && (
            <div className="findings-section">
              <h2>🚨 Recent Findings</h2>
              <div className="findings-list">
                {analysis.findings.slice(0, 5).map((finding, index) => (
                  <div key={index} className="finding-item">
                    <div 
                      className="finding-severity"
                      style={{ backgroundColor: getSeverityColor(finding.severity) }}
                    >
                      {finding.severity}
                    </div>
                    <div className="finding-details">
                      <div className="finding-rule">{finding.rule_name}</div>
                      <div className="finding-desc">{finding.description}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Analysis History */}
          <div className="history-section">
            <h2>📈 Analysis History</h2>
            <div className="history-list">
              {history.slice(0, 5).map((item, index) => (
                <div key={index} className="history-item">
                  <div className="history-date">
                    {new Date(item.started_at).toLocaleDateString()}
                  </div>
                  <div className="history-details">
                    <div>Analysis #{item.id}</div>
                    <div className="history-size">{item.total_files} files • {item.total_findings} findings</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

        {/* Executive Actions */}
        <div className="executive-actions">
          <button 
            onClick={() => analysis && apiClient.exportResults(analysis)}
            disabled={!analysis}
            className="action-btn primary"
          >
            📄 Generate Executive Report
          </button>
          <button 
            onClick={() => analysis && apiClient.exportCSV(analysis.findings)}
            disabled={!analysis}
            className="action-btn secondary"
          >
            📊 Export Findings CSV
          </button>
          <button 
            onClick={loadHistory}
            className="action-btn secondary"
          >
            🔄 Refresh History
          </button>
        </div>
      </div>
    </div>
  );
}
