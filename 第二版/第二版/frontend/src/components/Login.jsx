import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authApi } from '../lib/api';
import { Lock, User, Loader2 } from 'lucide-react';

export default function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('testuser');
  const [password, setPassword] = useState('testpass123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // 清除舊的 localStorage 數據
    localStorage.clear();
    console.log('🧹 已清除舊的 localStorage 數據');

    try {
      console.log('🔐 嘗試登入:', { username, api: 'http://localhost:8000/api/v1/auth/login' });
      
      const response = await authApi.login(username, password);
      
      console.log('✅ 登入成功，響應:', response.data);
      
      // 儲存 token 和用戶資訊
      const token = response.data.access_token;
      const userInfo = {
        username: username, // 使用登入時的用戶名
      };
      
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(userInfo));
      
      console.log('💾 已儲存 Token 和用戶資訊');
      console.log('Token:', token.substring(0, 20) + '...');
      console.log('User:', userInfo);
      
      // 導向 Dashboard
      console.log('🚀 跳轉到 Dashboard');
      navigate('/dashboard', { replace: true });
    } catch (err) {
      console.error('❌ 登入失敗:', err);
      console.error('錯誤詳情:', err.response?.data);
      setError(err.response?.data?.detail || '登入失敗，請檢查用戶名和密碼');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
        {/* Logo 和標題 */}
        <div className="text-center mb-8">
          <div className="bg-blue-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <Lock className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">EA Trading</h1>
          <p className="text-gray-600">自動跟單系統</p>
        </div>

        {/* 登入表單 */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* 用戶名 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              用戶名
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="請輸入用戶名"
                required
              />
            </div>
          </div>

          {/* 密碼 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              密碼
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="請輸入密碼"
                required
              />
            </div>
          </div>

          {/* 錯誤訊息 */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          {/* 登入按鈕 */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>登入中...</span>
              </>
            ) : (
              <>
                <Lock className="w-5 h-5" />
                <span>登入</span>
              </>
            )}
          </button>
        </form>

        {/* 註冊連結 */}
        <div className="mt-6 text-center">
          <p className="text-gray-600">
            尚未註冊？
            <Link 
              to="/register" 
              className="text-blue-600 hover:text-blue-700 font-semibold ml-1"
            >
              點此註冊
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
