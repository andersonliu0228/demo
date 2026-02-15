import { useState } from 'react';

const MOCK_CLIENTS = [
  { id: 1, name: '客戶 A', email: 'clienta@example.com', copyRatio: 1.0, status: 'active', totalValue: 50000, positions: 5 },
  { id: 2, name: '客戶 B', email: 'clientb@example.com', copyRatio: 0.5, status: 'pending', totalValue: 25000, positions: 3 },
  { id: 3, name: '客戶 C', email: 'clientc@example.com', copyRatio: 2.0, status: 'blocked', totalValue: 100000, positions: 8 }
];

function TraderAdmin() {
  const [clients] = useState(MOCK_CLIENTS);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  const filteredClients = clients.filter(client => {
    const matchesSearch = client.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         client.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || client.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status) => {
    if (status === 'active') return 'bg-green-100 text-green-800';
    if (status === 'pending') return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const getStatusLabel = (status) => {
    if (status === 'active') return '啟用中';
    if (status === 'pending') return '待審核';
    return '已封鎖';
  };

  const stats = {
    total: clients.length,
    active: clients.filter(c => c.status === 'active').length,
    pending: clients.filter(c => c.status === 'pending').length,
    blocked: clients.filter(c => c.status === 'blocked').length,
    totalValue: clients.reduce((sum, c) => sum + c.totalValue, 0)
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">交易員管理面板</h1>
        
        <div className="grid grid-cols-5 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-500">總客戶數</div>
            <div className="text-3xl font-bold text-gray-900">{stats.total}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-500">啟用中</div>
            <div className="text-3xl font-bold text-green-600">{stats.active}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-500">待審核</div>
            <div className="text-3xl font-bold text-yellow-600">{stats.pending}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-500">已封鎖</div>
            <div className="text-3xl font-bold text-red-600">{stats.blocked}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-500">總資產</div>
            <div className="text-2xl font-bold text-blue-600">${stats.totalValue.toLocaleString()}</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4 mb-8">
          <div className="flex gap-4">
            <input
              type="text"
              placeholder="搜尋客戶名稱或郵箱..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="flex-1 px-4 py-2 border rounded-lg"
            />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 border rounded-lg"
            >
              <option value="all">全部狀態</option>
              <option value="active">啟用中</option>
              <option value="pending">待審核</option>
              <option value="blocked">已封鎖</option>
            </select>
          </div>
          <div className="mt-4 text-sm text-gray-600">
            顯示 {filteredClients.length} / {clients.length} 位客戶
          </div>
        </div>

        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">客戶資訊</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">跟單比例</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">總資產</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">持倉數</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">狀態</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredClients.map((client) => (
                <tr key={client.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-gray-900">{client.name}</div>
                    <div className="text-sm text-gray-500">{client.email}</div>
                  </td>
                  <td className="px-6 py-4 text-sm font-semibold">{client.copyRatio}x</td>
                  <td className="px-6 py-4 text-sm font-semibold">${client.totalValue.toLocaleString()}</td>
                  <td className="px-6 py-4 text-sm">{client.positions}</td>
                  <td className="px-6 py-4">
                    <span className={"px-3 py-1 rounded-full text-sm font-medium " + getStatusColor(client.status)}>
                      {getStatusLabel(client.status)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default TraderAdmin;
