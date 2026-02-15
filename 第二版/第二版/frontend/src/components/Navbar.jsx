import { LogOut, User, Users } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';

export default function Navbar({ username }) {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    // 清除 localStorage 中的 Token
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    
    console.log('✅ 已登出，清除 Token 和用戶資訊');
    
    // 導回登入頁
    navigate('/login', { replace: true });
  };

  // 安全讀取用戶名，使用可選鏈和預設值
  const displayName = username || 'User';

  return (
    <nav className="bg-gradient-to-r from-blue-600 to-blue-700 shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* 左側：標題與導航 */}
          <div className="flex items-center gap-6">
            <h1 className="text-2xl font-bold text-white">
              EA Trading Dashboard
            </h1>
            
            {/* 導航連結 */}
            <div className="flex gap-2">
              <button
                onClick={() => navigate('/dashboard')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  location.pathname === '/dashboard'
                    ? 'bg-blue-500 text-white'
                    : 'text-blue-100 hover:bg-blue-500 hover:text-white'
                }`}
              >
                儀表板
              </button>
              <button
                onClick={() => navigate('/trader-admin')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                  location.pathname === '/trader-admin'
                    ? 'bg-blue-500 text-white'
                    : 'text-blue-100 hover:bg-blue-500 hover:text-white'
                }`}
              >
                <Users className="w-4 h-4" />
                客戶管理
              </button>
            </div>
          </div>

          {/* 右側：用戶資訊與登出 */}
          <div className="flex items-center gap-4">
            {/* 用戶名 */}
            <div className="flex items-center gap-2 bg-blue-500 bg-opacity-50 px-4 py-2 rounded-lg">
              <User className="w-5 h-5 text-white" />
              <span className="text-white font-medium">{displayName}</span>
            </div>

            {/* 登出按鈕 */}
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition-colors font-medium"
              aria-label="登出"
            >
              <LogOut className="w-5 h-5" />
              <span>登出</span>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
