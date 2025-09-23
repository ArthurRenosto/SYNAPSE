import './Sidebar.css';

export default function Sidebar({ currentPage, onNavigate, fileInputRef, onFileUpload, loading }) {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>🔍 SYNAPSE</h2>
      </div>

      <div className="sidebar-nav">
        <button 
          className={`nav-btn ${currentPage === 'dashboard' ? 'active' : ''}`}
          onClick={() => onNavigate('dashboard')}
        >
          <span className="nav-icon">🏠</span>
          Dashboard
        </button>
        
        <button 
          className={`nav-btn ${currentPage === 'imported-logs' ? 'active' : ''}`}
          onClick={() => onNavigate('imported-logs')}
        >
          <span className="nav-icon">📋</span>
          Imported Logs
        </button>

        {currentPage === 'dashboard' && (
          <button 
            className={`nav-btn ${currentPage === 'ai-analysis' ? 'active' : ''}`}
            onClick={() => onNavigate('ai-analysis')}
          >
            <span className="nav-icon">🤖</span>
            AI Analysis
          </button>
        )}
      </div>
    </div>
  );
}
