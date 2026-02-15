import { Activity, Power, User } from 'lucide-react';

export default function StatusBar({ dashboard }) {
  return (
    <div className="bg-white border-b border-gray-200 shadow-sm">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* 左側：標題和用戶 */}
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-gray-900">EA Trading</h1>
            <div className="flex items-center text-sm text-gray-600">
              <User className="w-4 h-4 mr-1" />
              <span>{dashboard.username}</span>
            </div>
          </div>

          {/* 右側：狀態指示器 */}
          <div className="flex items-center space-x-6">
            {/* 跟單狀態 */}
            <div className="flex items-center">
              <div className={`w-2 h-2 rounded-full mr-2 ${dashboard.is_active ? 'bg-green-500' : 'bg-gray-400'}`} />
              <span className="text-sm font-medium">
                跟單: {dashboard.is_active ? '啟用' : '停用'}
              </span>
            </div>

            {/* 引擎狀態 */}
            <div className="flex items-center">
              <Power className={`w-4 h-4 mr-2 ${dashboard.engine_status.is_running ? 'text-green-500' : 'text-gray-400'}`} />
              <span className="text-sm font-medium">
                引擎: {dashboard.engine_status.status}
              </span>
            </div>

            {/* Master 用戶 */}
            {dashboard.master_user_id && (
              <div className="flex items-center">
                <Activity className="w-4 h-4 mr-2 text-blue-500" />
                <span className="text-sm font-medium">
                  Master: #{dashboard.master_user_id}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
