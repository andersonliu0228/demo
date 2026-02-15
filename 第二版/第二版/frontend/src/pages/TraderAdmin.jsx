import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function TraderAdmin() {
  const [clients, setClients] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [emergencyStop, setEmergencyStop] = useState(false);

  // Fetch clients from API
  useEffect(() => {
    fetchClients();
    fetchEmergencyStopStatus();
  }, []);

  const fetchClients = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('請先登入');
        setLoading(false);
        return;
      }

      const response = await axios.get(`${API_BASE_URL}/api/v1/trader/clients`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      // Transform API data to match component structure
      const transformedClients = response.data.map(client => ({
        id: client.id,
        relationId: client.relation_id,
        name: client.username,
        email: client.email,
        copyRatio: client.copy_ratio,
        status: client.status,
        totalValue: client.net_value,
        positions: 0, // TODO: Get from API
        lastUpdate: new Date(client.created_at).toLocaleString('zh-TW'),
        lastSeen: client.last_seen ? new Date(client.last_seen) : null
      }));

      setClients(transformedClients);
      setLastUpdate(new Date());
    } catch (err) {
      console.error('獲取客戶列表失敗:', err);
      setError(err.response?.data?.detail || '獲取客戶列表失敗');
    } finally {
      setLoading(false);
    }
  };

  // Filter clients based on search and status
  const filteredClients = clients.filter(client => {
    const matchesSearch = client.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         client.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || client.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  // Status badge with real-time color logic
  const getStatusBadge = (status) => {
    const statusConfig = {
      active: {
        bg: 'bg-green-100',
        text: 'text-green-800',
        label: '啟用中',
        dot: 'bg-green-500'
      },
      pending: {
        bg: 'bg-yellow-100',
        text: 'text-yellow-800',
        label: '待審核',
        dot: 'bg-yellow-500'
      },
      blocked: {
        bg: 'bg-red-100',
        text: 'text-red-800',
        label: '已封鎖',
        dot: 'bg-red-500'
      }
    };

    const config = statusConfig[status] || statusConfig.pending;

    return (
      <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium ${config.bg} ${config.text}`}>
        <span className={`w-2 h-2 rounded-full ${config.dot} animate-pulse`}></span>
        {config.label}
      </span>
    );
  };

  // Handle status change
  const handleStatusChange = async (relationId, newStatus) => {
    setLoading(true);
    
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        alert('請先登入');
        return;
      }

      await axios.patch(
        `${API_BASE_URL}/api/v1/trader/update-client`,
        {
          relation_id: relationId,
          status: newStatus
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      // Update local state
      setClients(prevClients =>
        prevClients.map(client =>
          client.relationId === relationId ? { ...client, status: newStatus } : client
        )
      );

      alert(`客戶狀態已更新為: ${newStatus}`);
    } catch (err) {
      console.error('更新狀態失敗:', err);
      alert(err.response?.data?.detail || '更新狀態失敗');
    } finally {
      setLoading(false);
    }
  };

  // Handle copy ratio change
  const handleCopyRatioChange = async (relationId, newRatio) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        alert('請先登入');
        return;
      }

      await axios.patch(
        `${API_BASE_URL}/api/v1/trader/update-client`,
        {
          relation_id: relationId,
          copy_ratio: parseFloat(newRatio)
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      // Update local state
      setClients(prevClients =>
        prevClients.map(client =>
          client.relationId === relationId ? { ...client, copyRatio: parseFloat(newRatio) } : client
        )
      );

      alert('跟單比例已更新');
    } catch (err) {
      console.error('更新跟單比例失敗:', err);
      alert(err.response?.data?.detail || '更新跟單比例失敗');
    }
  };

  // Fetch emergency stop status
  const fetchEmergencyStopStatus = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const response = await axios.get(`${API_BASE_URL}/api/v1/trader/emergency-stop-status`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      setEmergencyStop(response.data.emergency_stop);
    } catch (err) {
      console.error('獲取緊急全停狀態失敗:', err);
    }
  };

  // Handle emergency stop toggle
  const handleEmergencyStop = async () => {
    const newState = !emergencyStop;
    const confirmMsg = newState 
      ? '確定要啟動緊急全停嗎？這將停止所有客戶的跟單！' 
      : '確定要解除緊急全停嗎？';
    
    if (!window.confirm(confirmMsg)) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        alert('請先登入');
        return;
      }

      const response = await axios.post(
        `${API_BASE_URL}/api/v1/trader/emergency-stop`,
        {
          stop_all: newState
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      setEmergencyStop(newState);
      alert(response.data.message);
    } catch (err) {
      console.error('緊急全停操作失敗:', err);
      alert(err.response?.data?.detail || '緊急全停操作失敗');
    }
  };

  // Get online status indicator
  const getOnlineStatus = (lastSeen) => {
    if (!lastSeen) {
      return {
        color: 'bg-gray-400',
        label: '未連線',
        isOnline: false
      };
    }

    const now = new Date();
    const lastSeenDate = new Date(lastSeen);
    const diffMinutes = (now - lastSeenDate) / 1000 / 60;

    if (diffMinutes < 5) {
      return {
        color: 'bg-green-500',
        label: '在線',
        isOnline: true
      };
    } else if (diffMinutes < 30) {
      return {
        color: 'bg-yellow-500',
        label: '離線',
        isOnline: false
      };
    } else {
      return {
        color: 'bg-red-500',
        label: '離線',
        isOnline: false
      };
    }
  };

  // Statistics
  const stats = {
    total: clients.length,
    active: clients.filter(c => c.status === 'active').length,
    pending: clients.filter(c => c.status === 'pending').length,
    blocked: clients.filter(c => c.status === 'blocked').length,
    totalValue: clients.reduce((sum, c) => sum + c.totalValue, 0)
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">交易員管理面板</h1>
              <p className="mt-1 text-sm text-gray-500">
                管理您的跟單客戶
                {lastUpdate && (
                  <span className="ml-2 text-gray-400">
                    • 最後更新: {lastUpdate.toLocaleTimeString('zh-TW')}
                  </span>
                )}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={fetchClients}
                disabled={loading}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? '載入中...' : '重新整理'}
              </button>
              <button
                onClick={handleEmergencyStop}
                className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                  emergencyStop 
                    ? 'bg-red-600 text-white hover:bg-red-700' 
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {emergencyStop ? '🚨 緊急全停中' : '緊急全停'}
              </button>
              <span className="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-lg">
                <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></span>
                系統運行中
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-red-800 font-medium">{error}</span>
            </div>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && clients.length === 0 ? (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="flex flex-col items-center justify-center gap-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="text-gray-600 font-medium">載入客戶資料中...</p>
          </div>
        </div>
      ) : (
        <>

      {/* Statistics Cards */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500">總客戶數</div>
            <div className="mt-2 text-3xl font-bold text-gray-900">{stats.total}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500">啟用中</div>
            <div className="mt-2 text-3xl font-bold text-green-600">{stats.active}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500">待審核</div>
            <div className="mt-2 text-3xl font-bold text-yellow-600">{stats.pending}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500">已封鎖</div>
            <div className="mt-2 text-3xl font-bold text-red-600">{stats.blocked}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500">總資產 (USDT)</div>
            <div className="mt-2 text-2xl font-bold text-blue-600">
              ${stats.totalValue.toLocaleString()}
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                搜尋客戶
              </label>
              <input
                type="text"
                placeholder="輸入客戶名稱或郵箱..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Status Filter */}
            <div className="w-full md:w-48">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                狀態篩選
              </label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">全部狀態</option>
                <option value="active">啟用中</option>
                <option value="pending">待審核</option>
                <option value="blocked">已封鎖</option>
              </select>
            </div>
          </div>

          {/* Results count */}
          <div className="mt-4 text-sm text-gray-600">
            顯示 {filteredClients.length} / {clients.length} 位客戶
          </div>
        </div>
      </div>

      {/* Client Table */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 pb-8">
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    在線狀態
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    客戶資訊
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    跟單比例
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    總資產 (USDT)
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    持倉數
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    狀態
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    最後更新
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    操作
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredClients.length === 0 ? (
                  <tr>
                    <td colSpan="8" className="px-6 py-12 text-center text-gray-500">
                      <div className="flex flex-col items-center gap-2">
                        <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                        </svg>
                        <p className="text-lg font-medium">沒有找到符合條件的客戶</p>
                        <p className="text-sm">請嘗試調整搜尋條件或篩選器</p>
                      </div>
                    </td>
                  </tr>
                ) : (
                  filteredClients.map((client) => {
                    const onlineStatus = getOnlineStatus(client.lastSeen);
                    return (
                    <tr key={client.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex flex-col items-center gap-1">
                          <div className={`w-3 h-3 rounded-full ${onlineStatus.color} ${onlineStatus.isOnline ? 'animate-pulse' : ''}`}></div>
                          <span className="text-xs text-gray-600">{onlineStatus.label}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                              <span className="text-blue-600 font-semibold text-sm">
                                {client.name.charAt(client.name.length - 1)}
                              </span>
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">{client.name}</div>
                            <div className="text-sm text-gray-500">{client.email}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <input
                          type="number"
                          step="0.1"
                          min="0"
                          value={client.copyRatio}
                          onChange={(e) => {
                            const newValue = e.target.value;
                            // Update local state immediately for responsiveness
                            setClients(prevClients =>
                              prevClients.map(c =>
                                c.relationId === client.relationId ? { ...c, copyRatio: parseFloat(newValue) || 0 } : c
                              )
                            );
                          }}
                          onBlur={(e) => handleCopyRatioChange(client.relationId, e.target.value)}
                          className="w-20 px-2 py-1 text-sm font-semibold text-gray-900 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                        <span className="ml-1 text-sm text-gray-600">x</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-semibold text-gray-900">
                          ${client.totalValue.toLocaleString()}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{client.positions}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getStatusBadge(client.status)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {client.lastUpdate}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex gap-2">
                          {client.status !== 'active' && (
                            <button
                              onClick={() => handleStatusChange(client.relationId, 'active')}
                              disabled={loading}
                              className="text-green-600 hover:text-green-900 disabled:opacity-50"
                            >
                              啟用
                            </button>
                          )}
                          {client.status !== 'blocked' && (
                            <button
                              onClick={() => handleStatusChange(client.relationId, 'blocked')}
                              disabled={loading}
                              className="text-red-600 hover:text-red-900 disabled:opacity-50"
                            >
                              封鎖
                            </button>
                          )}
                          {client.status === 'blocked' && (
                            <button
                              onClick={() => handleStatusChange(client.relationId, 'pending')}
                              disabled={loading}
                              className="text-yellow-600 hover:text-yellow-900 disabled:opacity-50"
                            >
                              解除封鎖
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      </>
      )}
    </div>
  );
}

export default TraderAdmin;
