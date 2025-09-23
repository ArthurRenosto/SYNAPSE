import './Sidebar.css';

export default function Sidebar({ 
  currentPage, 
  onNavigate, 
  fileInputRef, 
  onFileUpload, 
  loading,
  onAnalyze,
  onAIAnalysis,
  aiLoading,
  selectedFiles = []
}) {
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
      </div>
    </div>
  );
}

            
// <button 
//   onClick={handleAnalyze} 
//   disabled={loading}
//   className="sidebar-btn analyze"
// >
//   {loading ? '⏳ Analyzing...' : '🔍 Run Log Analysis'}
// </button>

// <button 
//   onClick={handleAIAnalysis} 
//   disabled={aiLoading || selectedFiles.length === 0}
//   className="sidebar-btn ai-analyze"
// >
//   {aiLoading ? '⏳ AI Analyzing...' : '🤖 AI Analysis'}
// </button>
