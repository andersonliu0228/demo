import { Clock, TrendingUp, TrendingDown, CheckCircle } from 'lucide-react';

export default function TradeHistory({ trades }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4 flex items-center">
        <Clock className="w-5 h-5 mr-2" />
        最近交易記錄
      </h3>

      {trades.length === 0 ? (
        <p className="text-gray-500 text-center py-8">暫無交易記錄</p>
      ) : (
        <div className="space-y-2">
          {trades.map((trade) => (
            <div
              key={trade.id}
              className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition"
            >
              {/* 左側：交易資訊 */}
              <div className="flex items-center space-x-4">
                {/* 圖標 */}
                <div className={`p-2 rounded-lg ${
                  trade.side === 'buy' 
                    ? 'bg-green-100 text-green-600' 
                    : 'bg-red-100 text-red-600'
                }`}>
                  {trade.side === 'buy' ? (
                    <TrendingUp className="w-5 h-5" />
                  ) : (
                    <TrendingDown className="w-5 h-5" />
                  )}
                </div>

                {/* 詳情 */}
                <div>
                  <div className="font-medium text-gray-900">{trade.symbol}</div>
                  <div className="text-sm text-gray-600">{trade.action}</div>
                </div>
              </div>

              {/* 中間：數量和方向 */}
              <div className="text-center">
                <div className="font-medium text-gray-900">
                  {trade.side === 'buy' ? '買入' : '賣出'} {trade.amount}
                </div>
                <div className="text-xs text-gray-500">
                  {trade.execution_time_ms ? `${trade.execution_time_ms}ms` : 'N/A'}
                </div>
              </div>

              {/* 右側：狀態和時間 */}
              <div className="text-right">
                <div className="flex items-center justify-end mb-1">
                  <CheckCircle className="w-4 h-4 text-green-500 mr-1" />
                  <span className="text-sm font-medium text-green-600">成功</span>
                </div>
                <div className="text-xs text-gray-500">
                  {new Date(trade.timestamp).toLocaleString('zh-TW', {
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 查看更多 */}
      {trades.length > 0 && (
        <div className="mt-4 text-center">
          <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
            查看完整交易歷史 →
          </button>
        </div>
      )}
    </div>
  );
}
