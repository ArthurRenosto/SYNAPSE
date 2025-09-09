import { useState, useRef } from 'react';
import { apiClient } from './apiClient';
import './Dashboard.css';

export default function Dashboard() {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleAnalyzeServer = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiClient.analyzeLogs();
      setAnalysis(result);
    } catch (err) {
      setError(err.response?.data?.error || 'Erro na análise');
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
      const result = await apiClient.uploadLog(file);
      setAnalysis(result);
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

  const handleExportJSON = () => {
    if (analysis) {
      apiClient.exportResults(analysis);
    }
  };

  const handleExportCSV = () => {
    if (analysis?.findings) {
      apiClient.exportCSV(analysis.findings);
    }
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

  return (
    <div className="dashboard">
      <header className="header">
        <h1>🔍 SYNAPSE SIEM</h1>
        <p>Sistema de Análise de Logs e Detecção de Ameaças</p>
      </header>

      <div className="controls">
        <div className="analysis-options">
          <button 
            onClick={handleAnalyzeServer} 
            disabled={loading}
            className="btn-primary"
          >
            {loading ? '⏳ Analisando...' : '🗂️ Analisar Logs do Servidor'}
          </button>
          
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
            <label htmlFor="file-upload" className={`btn-upload ${loading ? 'disabled' : ''}`}>
              📁 Enviar Arquivo de Log
            </label>
          </div>
        </div>

        {analysis && (
          <div className="export-buttons">
            <button onClick={handleExportJSON} className="btn-secondary">
              📄 Exportar JSON
            </button>
            <button onClick={handleExportCSV} className="btn-secondary">
              📊 Exportar CSV
            </button>
          </div>
        )}
      </div>

      {error && (
        <div className="error">
          ❌ {error}
        </div>
      )}

      {analysis && (
        <div className="results">
          <div className="summary">
            <h2>📊 Resumo da Análise</h2>
            {analysis.filename && (
              <div className="file-info">
                <p><strong>Arquivo:</strong> {analysis.filename}</p>
                <p><strong>Tamanho:</strong> {(analysis.size / 1024).toFixed(1)} KB</p>
              </div>
            )}
            <div className="stats">
              <div className="stat">
                <span className="label">Total de Logs:</span>
                <span className="value">{analysis.summary?.total_logs || analysis.total_logs || 1}</span>
              </div>
              <div className="stat">
                <span className="label">Achados:</span>
                <span className="value">{analysis.total_findings || 0}</span>
              </div>
            </div>

            {analysis.summary?.by_severity && (
              <div className="severity-breakdown">
                <h3>Por Severidade:</h3>
                {Object.entries(analysis.summary.by_severity).map(([severity, count]) => (
                  <div key={severity} className="severity-item">
                    <span 
                      className="severity-badge"
                      style={{ backgroundColor: getSeverityColor(severity) }}
                    >
                      {severity}
                    </span>
                    <span>{count}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {analysis.findings && analysis.findings.length > 0 && (
            <div className="findings">
              <h2>🚨 Achados Detalhados</h2>
              <div className="findings-list">
                {analysis.findings.slice(0, 20).map((finding, index) => (
                  <div key={index} className="finding-card">
                    <div className="finding-header">
                      <span 
                        className="severity-badge"
                        style={{ backgroundColor: getSeverityColor(finding.severity) }}
                      >
                        {finding.severity}
                      </span>
                      <span className="rule-name">{finding.rule_name}</span>
                    </div>
                    <div className="finding-details">
                      <p><strong>Arquivo:</strong> {finding.file}</p>
                      <p><strong>Linha:</strong> {finding.line_number}</p>
                      <p><strong>Descrição:</strong> {finding.description}</p>
                      {finding.recommendation && (
                        <p><strong>Recomendação:</strong> {finding.recommendation}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              {analysis.findings.length > 20 && (
                <p className="more-results">
                  ... e mais {analysis.findings.length - 20} achados. Use a exportação para ver todos.
                </p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
