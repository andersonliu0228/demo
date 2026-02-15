import { useState, useEffect } from 'react';
import { useDashboard } from '../hooks/useDashboard';
import { Loader2, AlertCircle } from 'lucide-react';

export default function Dashboard() {
  const { dashboard, loading, error, refresh } = useDashboard(3000);

  if (loading && !dashboard) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-gray-600">載入中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="bg-white p-8 rounded-lg shadow-lg max-w-md">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-center mb-2">載入失敗</h2>
          <p className="text-gray-600 text-center mb-4">{error}</p>
          <button
            onClick={refresh}
            className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 transition"
          >
            重試
          </button>
        </div>
      </div>
    );
  }

  if (!dashboard) return null;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Dashboard 測試（含數據）</h1>
        
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">基本資訊</h2>
          <div className="space-y-2">
            <p><strong>跟單狀態：</strong>{dashboard.is_active ? '✅ 已啟用' : '❌ 已停用'}</p>
            <p><strong>跟單比例：</strong>{(dashboard.follow_ratio * 100).toFixed(1)}%</p>
            <p><strong>總持倉價值：</strong>${dashboard.total_position_value.toLocaleString()}</p>
            <p><strong>未實現盈虧：</strong>${dashboard.unrealized_pnl.toFixed(2)} ({dashboard.unrealized_pnl_percent.toFixed(2)}%)</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">倉位資訊</h2>
          <div className="space-y-2">
            <p><strong>Master 倉位數：</strong>{dashboard.master_positions.length}</p>
            <p><strong>我的倉位數：</strong>{dashboard.my_positions.length}</p>
            <p><strong>成功交易數：</strong>{dashboard.recent_successful_trades.length}</p>
          </div>
        </div>

        <div className="bg-green-100 border border-green-400 rounded-lg p-4">
          <p className="text-green-800 font-semibold">✅ 如果你看到這個頁面，說明：</p>
          <ul className="list-disc list-inside text-green-700 mt-2 space-y-1">
            <li>useDashboard hook 正常工作</li>
            <li>API 請求成功</li>
            <li>數據載入正常</li>
            <li>問題可能在於某個子組件（StatusBar, FollowSettings, 等）</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
