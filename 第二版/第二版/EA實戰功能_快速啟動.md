# EA 實戰功能 - 快速啟動指南

## 🚀 快速開始

### 1. 確保系統運行
```powershell
# 啟動所有服務
docker-compose up -d

# 或使用腳本
.\docker-start.ps1
```

### 2. 資料庫已遷移
如果是首次使用，需要運行遷移：
```powershell
.\run-migration-010.ps1
```

### 3. 測試功能
```powershell
.\test-ea-features.ps1
```

## 📱 前端使用

### 訪問管理面板
```
URL: http://localhost:3000/admin
帳號: testuser
密碼: testpass123
```

### 功能說明

#### 1. 在線狀態燈號
表格第一欄顯示客戶的在線狀態：
- 🟢 **綠燈 + "在線"**: EA 正常運行（5分鐘內有心跳）
- 🟡 **黃燈 + "離線"**: EA 可能離線（5-30分鐘）
- 🔴 **紅燈 + "離線"**: EA 已離線（超過30分鐘）
- ⚪ **灰燈 + "未連線"**: EA 從未連接

#### 2. 緊急全停按鈕
位置：右上角，重新整理按鈕旁邊

**使用方法**:
1. 點擊「緊急全停」按鈕
2. 確認對話框選擇「確定」
3. 按鈕變為紅色「🚨 緊急全停中」
4. 所有 EA 將在下次調用 API 時停止跟單

**解除方法**:
1. 再次點擊「🚨 緊急全停中」按鈕
2. 確認對話框選擇「確定」
3. 按鈕恢復為灰色「緊急全停」
4. 所有 EA 恢復正常跟單

## 🤖 EA 集成

### API 端點
```
GET http://your-server:8000/api/v1/ea/config?user_id={USER_ID}
```

### 調用頻率
建議每 **1-5 分鐘** 調用一次

### 返回數據
```json
{
  "user_id": 2,
  "username": "follower1",
  "is_active": true,
  "copy_ratio": 2.5,
  "emergency_stop": false,
  "last_seen": "2026-02-04T10:30:00",
  "message": "配置獲取成功"
}
```

### EA 偽代碼示例

#### MQL4/MQL5
```mql4
// 全局變量
int g_user_id = 2;  // 從配置讀取
string g_api_url = "http://your-server:8000/api/v1/ea/config";
bool g_is_active = false;
double g_copy_ratio = 1.0;
bool g_emergency_stop = false;

// 定時器（每2分鐘調用一次）
void OnTimer()
{
    // 調用 API 獲取配置
    string url = g_api_url + "?user_id=" + IntegerToString(g_user_id);
    string response = HttpGet(url);
    
    // 解析 JSON
    JSONValue json;
    json.Deserialize(response);
    
    g_is_active = json["is_active"].ToBool();
    g_copy_ratio = json["copy_ratio"].ToDouble();
    g_emergency_stop = json["emergency_stop"].ToBool();
    
    Print("配置更新: is_active=", g_is_active, 
          ", copy_ratio=", g_copy_ratio,
          ", emergency_stop=", g_emergency_stop);
}

// 交易邏輯
void OnTick()
{
    // 檢查是否可以跟單
    if (!g_is_active || g_emergency_stop)
    {
        Print("跟單已停用");
        return;
    }
    
    // 執行跟單邏輯
    double master_lot = 0.1;
    double follower_lot = master_lot * g_copy_ratio;
    
    // 開倉...
    OrderSend(..., follower_lot, ...);
}
```

#### Python 示例
```python
import requests
import time

USER_ID = 2
API_URL = "http://your-server:8000/api/v1/ea/config"

def get_config():
    """獲取 EA 配置"""
    try:
        response = requests.get(f"{API_URL}?user_id={USER_ID}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"獲取配置失敗: {e}")
        return None

def main():
    """主循環"""
    while True:
        # 獲取配置
        config = get_config()
        
        if config:
            print(f"配置: is_active={config['is_active']}, "
                  f"copy_ratio={config['copy_ratio']}, "
                  f"emergency_stop={config['emergency_stop']}")
            
            # 檢查是否可以跟單
            if config['is_active'] and not config['emergency_stop']:
                # 執行跟單邏輯
                execute_copy_trade(config['copy_ratio'])
            else:
                print("跟單已停用")
        
        # 等待 2 分鐘
        time.sleep(120)

if __name__ == "__main__":
    main()
```

## 🔍 監控與診斷

### 檢查客戶在線狀態
1. 打開管理面板
2. 查看表格第一欄的燈號
3. 綠燈 = 正常，紅燈 = 需要檢查

### 檢查緊急全停狀態
```powershell
# 使用 API
curl http://localhost:8000/api/v1/trader/emergency-stop-status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 手動更新心跳
```powershell
# 測試 EA 心跳
curl "http://localhost:8000/api/v1/ea/heartbeat?user_id=2"
```

## 📊 常見場景

### 場景 1: EA 離線告警
**症狀**: 前端顯示紅燈

**排查步驟**:
1. 檢查 EA 是否正在運行
2. 檢查網絡連接
3. 檢查 API URL 配置是否正確
4. 查看 EA 日誌

### 場景 2: 緊急停止所有跟單
**操作步驟**:
1. 登入管理面板
2. 點擊「緊急全停」按鈕
3. 確認操作
4. 所有 EA 將在下次調用 API 時停止

### 場景 3: 單個客戶停用
**操作步驟**:
1. 在客戶列表找到目標客戶
2. 點擊「封鎖」按鈕
3. 該客戶的 EA 將在下次調用 API 時停止
4. 其他客戶不受影響

### 場景 4: 調整跟單比例
**操作步驟**:
1. 在客戶列表找到目標客戶
2. 修改「跟單比例」輸入框
3. 點擊輸入框外部（失焦）自動保存
4. EA 下次調用 API 時獲取新比例

## 🛠️ 故障排除

### 問題 1: 前端顯示「未連線」
**原因**: EA 從未調用過 API

**解決**:
1. 確認 EA 已啟動
2. 確認 API URL 配置正確
3. 確認 user_id 配置正確

### 問題 2: 緊急全停無效
**原因**: EA 調用頻率太低

**解決**:
1. 檢查 EA 的調用間隔設置
2. 建議設置為 1-5 分鐘
3. 手動觸發 EA 調用 API

### 問題 3: last_seen 不更新
**原因**: 資料庫遷移未執行

**解決**:
```powershell
.\run-migration-010.ps1
docker-compose restart backend
```

## 📞 技術支援

### 測試腳本
```powershell
# 完整功能測試
.\test-ea-features.ps1

# 持久化測試
.\test-persistence-verification.ps1

# 系統狀態檢查
.\check-system-status.ps1
```

### 日誌查看
```powershell
# 後端日誌
docker-compose logs -f backend

# 前端日誌
docker-compose logs -f frontend
```

### API 文檔
訪問 Swagger 文檔：
```
http://localhost:8000/docs
```

## 🎯 最佳實踐

### EA 端
1. ✅ 設置合理的調用間隔（1-5分鐘）
2. ✅ 實現錯誤重試機制
3. ✅ 記錄所有 API 調用日誌
4. ✅ 在收到 `is_active=false` 時立即停止跟單
5. ✅ 定期檢查 `emergency_stop` 狀態

### 交易員端
1. ✅ 定期檢查客戶在線狀態
2. ✅ 在市場異常時使用緊急全停
3. ✅ 根據客戶需求調整跟單比例
4. ✅ 及時處理離線客戶
5. ✅ 保持與客戶的溝通

---

**版本**: 2.0.0
**更新日期**: 2026-02-04
