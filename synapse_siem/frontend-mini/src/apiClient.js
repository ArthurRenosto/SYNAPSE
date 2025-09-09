import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

export const apiClient = {
  // Lista arquivos importados disponíveis para análise
  getAvailableFiles: async () => {
    const response = await api.get('/logs/');
    return response.data;
  },

  // Executa análise nos arquivos selecionados
  runAnalysis: async (fileIds = []) => {
    const response = await api.post('/logs/', { file_ids: fileIds });
    return response.data;
  },

  // Upload de arquivo de log (apenas salva metadados)
  uploadLog: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/logs/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Exclui arquivo importado
  deleteFile: async (fileId) => {
    const response = await api.delete(`/logs/files/${fileId}/`);
    return response.data;
  },

  // Busca histórico de análises
  getHistory: async () => {
    const response = await api.get('/logs/history/');
    return response.data;
  },

  // Exporta resultado em JSON
  exportResults: (data, filename = 'synapse-analysis.json') => {
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  },

  // Exporta resultado em CSV
  exportCSV: (findings, filename = 'synapse-findings.csv') => {
    if (!findings || findings.length === 0) return;
    
    const headers = ['File', 'Line', 'Rule', 'Severity', 'Description'];
    const csvContent = [
      headers.join(','),
      ...findings.map(f => [
        f.file || '',
        f.line_number || '',
        f.rule_name || '',
        f.severity || '',
        `"${(f.description || '').replace(/"/g, '""')}"`,
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
};
