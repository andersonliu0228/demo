import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import ProtectedRoute from './components/ProtectedRoute';
import Navbar from './components/Navbar';
import TraderAdmin from './pages/TraderAdmin';

function AppContent() {
  const location = useLocation();
  const [user, setUser] = useState(null);
  
  // 檢查是否為認證頁面
  const isAuthPage = location.pathname === '/login' || location.pathname === '/register';
  
  // 監聽 localStorage 變化和路由變化，更新用戶狀態
  useEffect(() => {
    const loadUser = () => {
      try {
        const token = localStorage.getItem('token');
        const userStr = localStorage.getItem('user');
        
        if (token && userStr) {
          const userData = JSON.parse(userStr);
          setUser(userData);
          console.log('✅ 用戶已登入:', userData.username);
        } else {
          setUser(null);
          console.log('ℹ️ 用戶未登入');
        }
      } catch (error) {
        console.error('❌ 解析用戶資訊失敗:', error);
        setUser(null);
      }
    };
    
    loadUser();
    
    // 監聽 storage 事件（跨標籤頁同步）
    window.addEventListener('storage', loadUser);
    
    return () => {
      window.removeEventListener('storage', loadUser);
    };
  }, [location.pathname]);

  return (
    <div className="min-h-screen bg-gray-100">
      {/* 只在已登入且非認證頁面時顯示 Navbar */}
      {!isAuthPage && user && (
        <Navbar username={user.username || 'User'} />
      )}
      
      {/* 路由 */}
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/login" element={<Login />} />
        <Route path="/admin" element={<TraderAdmin />} />
        <Route path="/register" element={<Register />} />
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } 
        />
      </Routes>
    </div>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
