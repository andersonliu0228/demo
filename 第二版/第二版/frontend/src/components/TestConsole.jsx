import { useState } from 'react';
import { Zap, X, ChevronLeft, ChevronRight, Loader2 } from 'lucide-react';
import { dashboardApi } from '../lib/api';

export default function TestConsole({ onTrigger }) {
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [formData, setFormData] = useState({
    master_user_id: 1,
    master_credential_id: 1,
    symbol: 'BTC/USDT',
    position_size: 1.0,
    entry_price: 50000.0,
  });

  const handleTrigger = async () => {
    try {
      setLoading(true);
      setMessage('');
      
      const response = await dashboardApi.triggerMasterOrder(formData);
      
      setMessage(`✓ 成功！倉位變動: ${response.data.master_info.old_position_size} → ${response.data.master_info.new_position_size}`);
      
      // 立即刷新儀表板
      setTimeout(() => {
        onTrigger();
      }, 100);
      
      // 3 秒後再次刷新（等待跟單完成）
      setTimeout(() => {
        onTrigger();
        setMessage(prev => prev + '\n✓ 跟單已完成，數據已更新');
      }, 3000);
      
    } catch (error) {
      setMessage(`✗ 失敗: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* 開關按鈕 */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 bg-blue-600 text-white p-4 rounded-full shadow-lg hover:bg-blue-700 transition z-50"
          title="開啟測試控制台"
        >
          <Zap className="w-6 h-6" />
        </button>
      )}

      {/* 側邊欄 */}
      <div
        className={`fixed top-0 right-0 h-full w-96 bg-white shadow-2xl transform transition-transform duration-300 z-50 ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        {/* 標題欄 */}
        <div className="bg-blue-600 text-white p-4 flex items-center justify-between">
          <div className="flex items-center">
            <Zap className="w-5 h-5 mr-2" />
            <h3 className="font-semibold">測試控制台</h3>
          </div>
          <button
            onClick={() => setIsOpen(false)}
            className="hover:bg-blue-700 p-1 rounded"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* 內容區 */}
        <div className="p-6 space-y-4 overflow-y-auto h-[calc(100%-64px)]">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
            <p className="text-sm text-yellow-800">
              ⚠️ <strong>測試專用</strong><br />
              此控制台僅用於開發測試，可以模擬 Master 下單觸發跟單。
            </p>
          </div>

          {/* 表單 */}
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Master 用戶 ID
              </label>
              <input
                type="number"
                value={formData.master_user_id}
                onChange={(e) => setFormData({ ...formData, master_user_id: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Master 憑證 ID
              </label>
              <input
                type="number"
                value={formData.master_credential_id}
                onChange={(e) => setFormData({ ...formData, master_credential_id: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                交易對
              </label>
              <select
                value={formData.symbol}
                onChange={(e) => setFormData({ ...formData, symbol: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="BTC/USDT">BTC/USDT</option>
                <option value="ETH/USDT">ETH/USDT</option>
                <option value="BNB/USDT">BNB/USDT</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                倉位大小
              </label>
              <input
                type="number"
                step="0.1"
                value={formData.position_size}
                onChange={(e) => setFormData({ ...formData, position_size: parseFloat(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">
                正數=多倉，負數=空倉，0=平倉
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                開倉價格
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.entry_price}
                onChange={(e) => setFormData({ ...formData, entry_price: parseFloat(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* 觸發按鈕 */}
          <button
            onClick={handleTrigger}
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                處理中...
              </>
            ) : (
              <>
                <Zap className="w-5 h-5 mr-2" />
                模擬 Master 下單
              </>
            )}
          </button>

          {/* 訊息顯示 */}
          {message && (
            <div className={`p-3 rounded-lg text-sm whitespace-pre-line ${
              message.includes('✗') 
                ? 'bg-red-50 text-red-800 border border-red-200' 
                : 'bg-green-50 text-green-800 border border-green-200'
            }`}>
              {message}
            </div>
          )}

          {/* 快速操作 */}
          <div className="border-t pt-4">
            <h4 className="text-sm font-medium text-gray-700 mb-2">快速操作</h4>
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => setFormData({ ...formData, position_size: 1.0 })}
                className="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded text-sm transition"
              >
                開倉 1.0
              </button>
              <button
                onClick={() => setFormData({ ...formData, position_size: 2.0 })}
                className="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded text-sm transition"
              >
                加倉 2.0
              </button>
              <button
                onClick={() => setFormData({ ...formData, position_size: 0.5 })}
                className="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded text-sm transition"
              >
                減倉 0.5
              </button>
              <button
                onClick={() => setFormData({ ...formData, position_size: 0 })}
                className="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded text-sm transition"
              >
                平倉 0
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 遮罩層 */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-30 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  );
}
