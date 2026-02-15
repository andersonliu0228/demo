import { Settings, Eye, EyeOff } from 'lucide-react';
import { useState } from 'react';

export default function FollowSettings({ dashboard, onUpdate }) {
  const [showApiKey, setShowApiKey] = useState(false);

  // 模擬 API Key 遮罩
  const maskApiKey = (key) => {
    if (!key) return 'N/A';
    if (showApiKey) return key;
    return key.substring(0, 8) + '****' + key.substring(key.length - 4);
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold flex items-center">
          <Settings className="w-5 h-5 mr-2" />
          我的跟隨設定
        </h3>
        <div className={`px-3 py-1 rounded-full text-sm font-medium ${
          dashboard.is_active 
            ? 'bg-green-100 text-green-800' 
            : 'bg-gray-100 text-gray-800'
        }`}>
          {dashboard.is_active ? '啟用中' : '已停用'}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* 跟單比例 */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600 mb-1">跟單比例</div>
          <div className="text-2xl font-bold text-gray-900">
            {(dashboard.follow_ratio * 100).toFixed(1)}%
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Master 倉位的 {(dashboard.follow_ratio * 100).toFixed(1)}%
          </div>
        </div>

        {/* Master 用戶 */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600 mb-1">跟隨 Master</div>
          <div className="text-2xl font-bold text-gray-900">
            #{dashboard.master_user_id || 'N/A'}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Master 用戶 ID
          </div>
        </div>

        {/* API Key（遮罩） */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600 mb-1 flex items-center justify-between">
            <span>API Key</span>
            <button
              onClick={() => setShowApiKey(!showApiKey)}
              className="text-gray-400 hover:text-gray-600"
            >
              {showApiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
          <div className="text-sm font-mono text-gray-900 break-all">
            {maskApiKey('mock_api_key_1234567890abcdef')}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            跟隨者憑證
          </div>
        </div>
      </div>

      {/* 設定說明 */}
      <div className="mt-4 p-3 bg-blue-50 rounded-lg">
        <p className="text-sm text-blue-800">
          💡 <strong>提示：</strong>
          當 Master 的倉位變動時，系統會在 3 秒內自動執行對帳，
          根據您設定的跟單比例調整您的倉位。
        </p>
      </div>
    </div>
  );
}
