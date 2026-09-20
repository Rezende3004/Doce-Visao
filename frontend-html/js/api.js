const API_URL = '';

async function apiGet(endpoint, params = {}) {
    const qs = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
        if (v !== null && v !== undefined) qs.append(k, v);
    });
    const query = qs.toString();
    const url = query ? `${endpoint}?${query}` : endpoint;
    const response = await fetch(url);
    if (!response.ok) throw new Error(`API error: ${response.status}`);
    return response.json();
}

async function apiPost(endpoint, data) {
    const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error(`API error: ${response.status}`);
    return response.json();
}

async function apiUpload(endpoint, file) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(endpoint, {
        method: 'POST',
        body: formData,
    });
    if (!response.ok) throw new Error(`API error: ${response.status}`);
    return response.json();
}

const API = {
    getSummary: (params) => apiGet('/api/v1/dashboard/summary', params),
    getTimeline: (params) => apiGet('/api/v1/sales/timeline', params),
    getByWeekday: (params) => apiGet('/api/v1/sales/by-weekday', params),
    getByChannel: (params) => apiGet('/api/v1/sales/by-channel', params),
    getRanking: (params) => apiGet('/api/v1/products/ranking', params),
    getCategoryPerformance: (params) => apiGet('/api/v1/products/categories/performance', params),
    getMargin: (params) => apiGet('/api/v1/products/margin', params),
    getWaste: (params) => apiGet('/api/v1/production/waste', params),
    getInsights: (params) => apiGet('/api/v1/insights', params),
    getFilterOptions: () => apiGet('/api/v1/filters/options'),
    getImports: (params) => apiGet('/api/v1/imports', params),
    previewSales: (file) => apiUpload('/api/v1/imports/sales/preview', file),
    confirmSales: (file) => apiUpload('/api/v1/imports/sales/confirm', file),
    previewProduction: (file) => apiUpload('/api/v1/imports/production/preview', file),
    confirmProduction: (file) => apiUpload('/api/v1/imports/production/confirm', file),
    getImportErrors: (batchId) => apiGet(`/api/v1/imports/${batchId}/errors`),
};
