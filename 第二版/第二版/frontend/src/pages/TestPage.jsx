// 完全獨立的測試頁面 - 不依賴任何外部組件
const TestPage = () => {
  return (
    <div style={{ padding: '40px', backgroundColor: '#f0f0f0', minHeight: '100vh' }}>
      <h1 style={{ fontSize: '48px', color: '#333', marginBottom: '20px' }}>
        ✅ 測試頁面成功渲染！
      </h1>
      <p style={{ fontSize: '24px', color: '#666' }}>
        如果你看到這個頁面，表示 Vite 和 React 都正常運作。
      </p>
      <div style={{ marginTop: '40px', padding: '20px', backgroundColor: 'white', borderRadius: '8px' }}>
        <h2 style={{ fontSize: '24px', marginBottom: '10px' }}>系統狀態</h2>
        <ul style={{ fontSize: '18px', lineHeight: '1.8' }}>
          <li>✅ React 正常</li>
          <li>✅ Vite 正常</li>
          <li>✅ 路由正常</li>
          <li>✅ 容器正常</li>
        </ul>
      </div>
    </div>
  );
};

export default TestPage;
