import { useState } from 'react';
import CTEMDashboard from './CTEMDashboard';
import ImportedLogs from './ImportedLogs';

export default function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');

  const renderPage = () => {
    switch (currentPage) {
      case 'imported-logs':
        return <ImportedLogs onNavigate={setCurrentPage} />;
      case 'dashboard':
      default:
        return <CTEMDashboard onNavigate={setCurrentPage} />;
    }
  };

  return (
    <div className="app">
      {renderPage()}
    </div>
  );
}
