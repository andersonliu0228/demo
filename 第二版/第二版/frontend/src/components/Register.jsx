import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authApi } from '../lib/api';
import { Lock, User, Mail, Loader2, CheckCircle } from 'lucide-react';

export default function Register() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const validateForm = () => {
    if (formData.password !== formData.confirmPassword) {
      setError('密碼和確認密碼不一致');
      return false;
    }
    if (formData.password.length < 6) {
      setError('密碼長度至少需要 6 個字元');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError('');

    try {
      await authApi.register(
        formData.username,
        formData.email,
        formData.password
      );
      
      setSuccess(true);
      
      // 3 秒後導向登入頁
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } catch (err) {
      console.error('註冊錯誤:', err);
      
      // 處理不同的錯誤情況
      if (err.response?.status === 400) {
        // 用戶名或郵箱已存在
        const detail = err.response?.data?.detail || '';
        if (detail.includes('用戶名')) {
          setError('此用戶名已被使用，請選擇其他用戶名');
        } else if (detail.includes('郵件') || detail.includes('電子郵件')) {
          setError('此 Email 已被註冊');
        } else {
          setError(detail || '註冊失敗，請檢查輸入資料');
        }
      } else if (err.response?.status === 500) {
        setError('伺服器錯誤，請稍後再試');
      } else {
        setError(err.response?.data?.detail || '註冊失敗，請稍後再試');
      }
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md text-center">
          <div className="bg-green-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-12 h-12 text-green-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">註冊成功！</h2>
          <p className="text-gray-600 mb-4">
            您的帳號已成功創建，即將跳轉至登入頁面...
          </p>
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
        {/* Logo 和標題 */}
        <div className="text-center mb-8">
          <div className="bg-purple-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <User className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">創建帳號</h1>
          <p className="text-gray-600">加入 EA Trading 自動跟單系統</p>
        </div>

        {/* 註冊表單 */}
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
                name="username"
                value={formData.username}
                onChange={handleChange}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="請輸入用戶名"
                required
              />
            </div>
          </div>

          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="請輸入 Email"
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
                name="password"
                value={formData.password}
                onChange={handleChange}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="請輸入密碼（至少 6 個字元）"
                required
              />
            </div>
          </div>

          {/* 確認密碼 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              確認密碼
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="請再次輸入密碼"
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

          {/* 註冊按鈕 */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>註冊中...</span>
              </>
            ) : (
              <>
                <User className="w-5 h-5" />
                <span>註冊</span>
              </>
            )}
          </button>
        </form>

        {/* 登入連結 */}
        <div className="mt-6 text-center">
          <p className="text-gray-600">
            已有帳號？
            <Link 
              to="/login" 
              className="text-purple-600 hover:text-purple-700 font-semibold ml-1"
            >
              點此登入
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
