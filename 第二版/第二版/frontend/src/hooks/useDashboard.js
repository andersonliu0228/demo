import { useState, useEffect, useCallback } from 'react';
import { dashboardApi } from '../lib/api';

export function useDashboard(refreshInterval = 5000) {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboard = useCallback(async () => {
    try {
      setLoading(true);
      const response = await dashboardApi.getSummary();
      setDashboard(response.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || '獲取儀表板數據失敗');
      console.error('Dashboard fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // 初始載入
  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  // 定期刷新
  useEffect(() => {
    if (refreshInterval > 0) {
      const interval = setInterval(fetchDashboard, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [refreshInterval, fetchDashboard]);

  return {
    dashboard,
    loading,
    error,
    refresh: fetchDashboard,
  };
}
