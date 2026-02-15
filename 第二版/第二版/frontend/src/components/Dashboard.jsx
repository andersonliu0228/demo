import { useState, useEffect } from 'react';
import { useDashboard } from '../hooks/useDashboard';
import { Activity, TrendingUp, Settings, AlertCircle, Loader2, Power, PowerOff } from 'lucide-react';
import StatusBar from './StatusBar';
import FollowSettings from './FollowSettings';
import TradeHistory from './TradeHistory';
import TestConsole from './TestConsole';
import { followConfigApi } from '../lib/api';

export default function Dashboard() {
  const { dashboard, loading, error, refresh } = useDashboard(3000); // 3秒輪詢
  const [toast, setToast] = useState(null);
  const [toggleLoading, setToggleLoading] = useState(false);

  // 顯示 Toast 通知
  const showToast = (message, type = 'info') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 5000);
  };

  // 檢測錯誤並顯示通知
  useEffect(() => {
    if (dashboard?.has_unresolved_errors && dashboard?.unresolved_error_count > 0) {
      showToast(
        `⚠️ 檢測到 ${dashboard.unresolved_error_count} 個未解決的交易錯誤！`,
        'error'
      );
    }
  }, [dashboard?.unresolved_error_count]);

  // 切換跟單開關
  const handleToggleActive = async () => {
    if (!dashboard) return;
    
    setToggleLoading(true);
    try {
      const newActiveState = !dashboard.is_active;
      
      await followConfigApi.updateSettings({
        is_active: newActiveState,
        follow_ratio: dashboard.follow_ratio,
        master_user_id: dashboard.master_user_id || 1,
        master_credential_id: 1 // 使用預設憑證
      });
      
      showToast(
        newActiveState ? '✅ 跟單已啟用，Worker 將在下一個循環同步倉位' : '⚠️ 跟單已停用',
        newActiveState ? 'success' : 'warning'
      );
      
      // 立即刷新數據
      setTimeout(refresh, 500);
    } catch (err) {
      showToast(`❌ 切換失敗: ${err.response?.data?.detail || err.message}`, 'error');
    } finally {
      setToggleLoading(false);
    }
  };

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
    <div className="min-h-screen bg-gray-50">
      
      {/* Toast 通知 */}
      {toast && (
        <div className="fixed top-4 right-4 z-50 animate-slide-in">
          <div className={`px-6 py-4 rounded-lg shadow-2xl border-2 max-w-md ${
            toast.type === 'error' ? 'bg-red-50 border-red-500 text-red-800' :
            toast.type === 'success' ? 'bg-green-50 border-green-500 text-green-800' :
            toast.type === 'warning' ? 'bg-yellow-50 border-yellow-500 text-yellow-800' :
            'bg-blue-50 border-blue-500 text-blue-800'
          }`}>
            <div className="flex items-start gap-3">
              <AlertCircle className="w-6 h-6 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="font-semibold text-sm">{toast.message}</p>
              </div>
              <button
                onClick={() => setToast(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 頂部狀態欄 */}
      <StatusBar dashboard={dashboard} />

      {/* 主要內容區 */}
      <div className="container mx-auto px-4 py-6 space-y-6">
        {/* 一鍵開關 + 統計卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
          {/* 一鍵開關卡片 */}
          <div className="bg-white rounded-lg shadow p-6 md:col-span-1">
            <h3 className="text-sm font-medium text-gray-600 mb-3">跟單狀態</h3>
            <button
              onClick={handleToggleActive}
              disabled={toggleLoading}
              className={`w-full py-3 px-4 rounded-lg font-semibold transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 ${
                dashboard.is_active
                  ? 'bg-green-500 hover:bg-green-600 text-white shadow-lg shadow-green-200'
                  : 'bg-gray-300 hover:bg-gray-400 text-gray-700'
              }`}
            >
              {toggleLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : dashboard.is_active ? (
                <>
                  <Power className="w-5 h-5" />
                  <span>已啟用</span>
                </>
              ) : (
                <>
                  <PowerOff className="w-5 h-5" />
                  <span>已停用</span>
                </>
              )}
            </button>
            <p className="text-xs text-gray-500 mt-2 text-center">
              {dashboard.is_active ? '點擊停用跟單' : '點擊啟用跟單'}
            </p>
          </div>

          {/* 統計卡片 */}
          <StatCard
            title="總持倉價值"
            value={`${dashboard.total_position_value.toLocaleString()}`}
            subtitle="USDT"
            icon={<TrendingUp className="w-6 h-6" />}
            color="blue"
          />
          
          {/* 未實現盈虧卡片 */}
          <StatCard
            title="未實現盈虧"
            value={`${dashboard.unrealized_pnl >= 0 ? '+' : ''}${Math.abs(dashboard.unrealized_pnl).toLocaleString()}`}
            subtitle={`${dashboard.unrealized_pnl_percent >= 0 ? '+' : ''}${dashboard.unrealized_pnl_percent.toFixed(2)}%`}
            icon={<TrendingUp className="w-6 h-6" />}
            color={dashboard.unrealized_pnl >= 0 ? 'green' : 'red'}
          />
          
          <StatCard
            title="跟單比例"
            value={`${(dashboard.follow_ratio * 100).toFixed(1)}%`}
            subtitle="Master 倉位的比例"
            icon={<Settings className="w-6 h-6" />}
            color="purple"
          />
          <StatCard
            title="我的倉位"
            value={dashboard.my_positions.length}
            subtitle="個交易對"
            icon={<Activity className="w-6 h-6" />}
            color="orange"
          />
          <StatCard
            title="成功交易"
            value={dashboard.recent_successful_trades.length}
            subtitle="最近記錄"
            icon={<TrendingUp className="w-6 h-6" />}
            color="blue"
          />
        </div>

        {/* 跟單設定 */}
        <FollowSettings dashboard={dashboard} onUpdate={refresh} />

        {/* 倉位對比 - Master 和 Follower 並排顯示 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Master 倉位 */}
          <PositionCard
            title="Master 倉位"
            positions={dashboard.master_positions}
            color="green"
            showExpected={true}
            followRatio={dashboard.follow_ratio}
          />

          {/* 我的倉位 */}
          <PositionCard
            title="我的倉位"
            positions={dashboard.my_positions}
            color="blue"
          />
        </div>

        {/* Master 最新動作 */}
        {dashboard.master_latest_activity && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Master 最新動作</h3>
            <div className="flex items-center justify-between bg-blue-50 p-4 rounded-lg">
              <div>
                <div className="font-medium text-lg">{dashboard.master_latest_activity.symbol}</div>
                <div className="text-sm text-gray-600">{dashboard.master_latest_activity.action}</div>
              </div>
              <div className="text-right">
                <div className="font-bold text-xl">{dashboard.master_latest_activity.position_size}</div>
                <div className="text-xs text-gray-500">
                  {new Date(dashboard.master_latest_activity.timestamp).toLocaleString('zh-TW')}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 交易歷史 */}
        <TradeHistory trades={dashboard.recent_successful_trades} />

        {/* 錯誤提示 */}
        {dashboard.has_unresolved_errors && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center">
              <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
              <div>
                <h4 className="font-semibold text-red-800">有未解決的錯誤</h4>
                <p className="text-sm text-red-600">
                  您有 {dashboard.unresolved_error_count} 個未解決的交易錯誤，請前往錯誤管理頁面處理。
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 測試控制台 */}
      <TestConsole onTrigger={refresh} />
    </div>
  );
}

// 統計卡片組件
function StatCard({ title, value, subtitle, icon, color }) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600',
    orange: 'bg-orange-50 text-orange-600',
    red: 'bg-red-50 text-red-600',
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium text-gray-600">{title}</h3>
        <div className={`p-2 rounded-lg ${colorClasses[color]}`}>
          {icon}
        </div>
      </div>
      <div className="text-2xl font-bold text-gray-900">{value}</div>
      <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
    </div>
  );
}

// 倉位卡片組件
function PositionCard({ title, positions, color, showExpected, followRatio }) {
  const borderColor = color === 'blue' ? 'border-blue-200' : 'border-green-200';
  const bgColor = color === 'blue' ? 'bg-blue-50' : 'bg-green-50';

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      {positions.length === 0 ? (
        <p className="text-gray-500 text-center py-8">暫無倉位</p>
      ) : (
        <div className="space-y-3">
          {positions.map((pos, index) => {
            // 計算盈虧（簡化版：假設當前價格 = 開倉價格）
            const pnl = 0; // 實際應該從交易所獲取當前價格計算
            const pnlColor = pnl > 0 ? 'text-green-600' : pnl < 0 ? 'text-red-600' : 'text-gray-600';
            
            return (
              <div
                key={index}
                className={`flex items-center justify-between p-3 ${bgColor} rounded-lg border ${borderColor}`}
              >
                <div className="flex-1">
                  <div className="font-medium">{pos.symbol}</div>
                  <div className="text-sm text-gray-600">
                    {pos.position_size} @ ${pos.entry_price?.toLocaleString() || 'N/A'}
                  </div>
                  {showExpected && followRatio && (
                    <div className="text-xs text-gray-500 mt-1">
                      預期跟隨: {(pos.position_size * followRatio).toFixed(4)}
                    </div>
                  )}
                </div>
                <div className="text-right">
                  <div className="font-bold">${pos.current_value.toLocaleString()}</div>
                  <div className={`text-xs font-semibold ${pnlColor}`}>
                    {pnl > 0 ? '+' : ''}{pnl.toFixed(2)} USDT
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
