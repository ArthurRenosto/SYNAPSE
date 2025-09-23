import { useState, useEffect } from 'react';
import { apiClient } from './apiClient';
import './ImportedLogs.css';
import Sidebar from './components/Sidebar';

export default function ImportedLogs({ onNavigate }) {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadLogs();
  }, []);

  const loadLogs = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getAvailableFiles();
      setLogs(data.available_files || []);
    } catch (err) {
      setError('Erro ao carregar logs');
      console.error('Error loading logs:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (fileId) => {
    if (!confirm('Tem certeza que deseja excluir este arquivo?')) return;
    
    try {
      await apiClient.deleteFile(fileId);
      setLogs(logs.filter(log => log.id !== fileId));
    } catch (err) {
      setError('Erro ao excluir arquivo');
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('pt-BR');
  };

  if (loading) {
    return (
      <div className="imported-logs">
        <div className="loading">⏳ Carregando logs...</div>
      </div>
    );
  }

  return (
    <div className="imported-logs-page">

      {/* Left Sidebar */}
            <Sidebar 
             currentPage="imported-logs"
             onNavigate={onNavigate}
             loading={loading}
           />

      {/* Main Content */}
      <div className="imported-logs">
        {/* Header Card */}
        <div className="header-card">
          <div className="logs-header">
            <h1>📁 Imported Logs</h1>
            <p>Visualize e gerencie todos os arquivos de log importados</p>
            <div className="logs-stats">
              <span className="stat">Total: {logs.length} arquivos</span>
              <span className="stat">
                Tamanho: {formatFileSize(logs.reduce((sum, log) => sum + log.size, 0))}
              </span>
            </div>
          </div>
        </div>

        {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}

      {logs.length === 0 ? (
        <div className="no-logs">
          <div className="no-logs-icon">📂</div>
          <h3>Nenhum log importado</h3>
          <p>Importe arquivos de log para começar a análise</p>
        </div>
      ) : (
        <div className="logs-grid">
          {logs.map((log) => (
            <div key={log.id} className="log-card">
              <div className="log-card-header">
                <div className="log-title">
                  <div className="log-icon">📄</div>
                  <h3 className="log-filename">{log.filename}</h3>
                </div>
                <div className="log-actions">
                  <button 
                    className="delete-btn"
                    onClick={() => handleDelete(log.id)}
                    title="Excluir arquivo"
                  >
                    🗑️
                  </button>
                </div>
              </div>
              
              <div className="log-card-content">
                
                <div className="log-details">
                  <div className="detail-item">
                    <span className="detail-label">Tamanho:</span>
                    <span className="detail-value">{formatFileSize(log.size)}</span>
                  </div>
                  
                  <div className="detail-item">
                    <span className="detail-label">Linhas:</span>
                    <span className="detail-value">{log.total_lines?.toLocaleString() || 'N/A'}</span>
                  </div>
                  
                  <div className="detail-item">
                    <span className="detail-label">Importado:</span>
                    <span className="detail-value">{formatDate(log.uploaded_at)}</span>
                  </div>
                </div>
              </div>
              
              <div className="log-card-footer">
                <div className="log-status">
                  <span className="status-indicator active"></span>
                  <span>Disponível</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      </div>
    </div>
  );
}
