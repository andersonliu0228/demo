"""
PnL Service
盈虧計算服務 - 計算未實現和已實現盈虧
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from backend.app.models.follower_position import FollowerPosition
from backend.app.models.trade_log import TradeLog
from backend.app.services.exchanges.mock_exchange import MockExchange

logger = logging.getLogger(__name__)


class PnLService:
    """盈虧計算服務"""
    
    def __init__(self, db: AsyncSession):
        """
        初始化 PnL Service
        
        Args:
            db: 資料庫 session
        """
        self.db = db
        logger.info("PnLService 初始化完成")
    
    async def calculate_unrealized_pnl(
        self,
        user_id: int,
        credential_id: int
    ) -> Dict[str, Any]:
        """
        計算未實現盈虧
        
        公式: (當前市價 - 入場均價) × 持倉數量
        
        Args:
            user_id: 用戶 ID
            credential_id: 憑證 ID
            
        Returns:
            {
                "total_unrealized_pnl": 1250.50,
                "total_unrealized_pnl_percent": 12.5,
                "total_position_value": 10000.0,
                "total_cost": 8750.0,
                "positions": [
                    {
                        "symbol": "BTC/USDT",
                        "entry_price": 48000.0,
                        "current_price": 50000.0,
                        "position_size": 0.5,
                        "cost": 24000.0,
                        "current_value": 25000.0,
                        "unrealized_pnl": 1000.0,
                        "unrealized_pnl_percent": 4.17
                    }
                ]
            }
        """
        try:
            # 獲取用戶所有倉位
            result = await self.db.execute(
                select(FollowerPosition).where(
                    and_(
                        FollowerPosition.user_id == user_id,
                        FollowerPosition.credential_id == credential_id
                    )
                )
            )
            positions = result.scalars().all()
            
            if not positions:
                logger.info(f"用戶 {user_id} 沒有倉位")
                return {
                    "total_unrealized_pnl": 0.0,
                    "total_unrealized_pnl_percent": 0.0,
                    "total_position_value": 0.0,
                    "total_cost": 0.0,
                    "positions": []
                }
            
            # 獲取當前市價（從 MockExchange）
            current_prices = await self._fetch_current_prices(positions)
            
            # 計算每個倉位的盈虧
            position_pnls = []
            total_cost = 0.0
            total_value = 0.0
            
            for pos in positions:
                if pos.position_size == 0:
                    continue
                
                entry_price = pos.entry_price or 0.0
                current_price = current_prices.get(pos.symbol, entry_price)
                position_size = abs(pos.position_size)
                
                # 計算成本和當前價值
                cost = entry_price * position_size
                current_value = current_price * position_size
                
                # 計算盈虧
                unrealized_pnl = (current_price - entry_price) * position_size
                unrealized_pnl_percent = (unrealized_pnl / cost * 100) if cost > 0 else 0.0
                
                total_cost += cost
                total_value += current_value
                
                position_pnls.append({
                    "symbol": pos.symbol,
                    "entry_price": entry_price,
                    "current_price": current_price,
                    "position_size": pos.position_size,
                    "cost": cost,
                    "current_value": current_value,
                    "unrealized_pnl": unrealized_pnl,
                    "unrealized_pnl_percent": unrealized_pnl_percent
                })
            
            # 計算總盈虧
            total_unrealized_pnl = total_value - total_cost
            total_unrealized_pnl_percent = (total_unrealized_pnl / total_cost * 100) if total_cost > 0 else 0.0
            
            logger.info(
                f"用戶 {user_id} 未實現盈虧: {total_unrealized_pnl:.2f} USDT "
                f"({total_unrealized_pnl_percent:.2f}%)"
            )
            
            return {
                "total_unrealized_pnl": round(total_unrealized_pnl, 2),
                "total_unrealized_pnl_percent": round(total_unrealized_pnl_percent, 2),
                "total_position_value": round(total_value, 2),
                "total_cost": round(total_cost, 2),
                "positions": position_pnls
            }
            
        except Exception as e:
            logger.error(f"計算未實現盈虧失敗: {str(e)}", exc_info=True)
            raise
    
    async def calculate_realized_pnl(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        計算已實現盈虧（從交易記錄）
        
        Args:
            user_id: 用戶 ID
            start_date: 開始日期（可選）
            end_date: 結束日期（可選）
            
        Returns:
            {
                "total_realized_pnl": 500.25,
                "total_realized_pnl_percent": 5.0,
                "trades_count": 10,
                "winning_trades": 7,
                "losing_trades": 3,
                "win_rate": 70.0
            }
        """
        try:
            # 構建查詢條件
            conditions = [
                TradeLog.follower_user_id == user_id,
                TradeLog.is_success == True
            ]
            
            if start_date:
                conditions.append(TradeLog.timestamp >= datetime.combine(start_date, datetime.min.time()))
            if end_date:
                conditions.append(TradeLog.timestamp <= datetime.combine(end_date, datetime.max.time()))
            
            # 獲取成功的交易記錄
            result = await self.db.execute(
                select(TradeLog).where(and_(*conditions))
            )
            trades = result.scalars().all()
            
            if not trades:
                logger.info(f"用戶 {user_id} 沒有交易記錄")
                return {
                    "total_realized_pnl": 0.0,
                    "total_realized_pnl_percent": 0.0,
                    "trades_count": 0,
                    "winning_trades": 0,
                    "losing_trades": 0,
                    "win_rate": 0.0
                }
            
            # 簡化版：假設每筆交易的盈虧為 0（實際需要記錄開倉和平倉價格）
            # 這裡只統計交易次數
            trades_count = len(trades)
            
            # TODO: 實作真實的已實現盈虧計算
            # 需要 position_history 表記錄開倉和平倉資訊
            
            logger.info(f"用戶 {user_id} 交易次數: {trades_count}")
            
            return {
                "total_realized_pnl": 0.0,
                "total_realized_pnl_percent": 0.0,
                "trades_count": trades_count,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0
            }
            
        except Exception as e:
            logger.error(f"計算已實現盈虧失敗: {str(e)}", exc_info=True)
            raise
    
    async def get_pnl_summary(
        self,
        user_id: int,
        credential_id: int
    ) -> Dict[str, Any]:
        """
        獲取 PnL 摘要（未實現 + 已實現）
        
        Args:
            user_id: 用戶 ID
            credential_id: 憑證 ID
            
        Returns:
            {
                "unrealized_pnl": 1250.50,
                "unrealized_pnl_percent": 12.5,
                "realized_pnl": 500.25,
                "realized_pnl_percent": 5.0,
                "total_pnl": 1750.75,
                "total_pnl_percent": 17.5,
                "total_position_value": 10000.0,
                "trades_count": 10
            }
        """
        try:
            # 計算未實現盈虧
            unrealized = await self.calculate_unrealized_pnl(user_id, credential_id)
            
            # 計算已實現盈虧
            realized = await self.calculate_realized_pnl(user_id)
            
            # 匯總
            total_pnl = unrealized["total_unrealized_pnl"] + realized["total_realized_pnl"]
            total_cost = unrealized["total_cost"]
            total_pnl_percent = (total_pnl / total_cost * 100) if total_cost > 0 else 0.0
            
            return {
                "unrealized_pnl": unrealized["total_unrealized_pnl"],
                "unrealized_pnl_percent": unrealized["total_unrealized_pnl_percent"],
                "realized_pnl": realized["total_realized_pnl"],
                "realized_pnl_percent": realized["total_realized_pnl_percent"],
                "total_pnl": round(total_pnl, 2),
                "total_pnl_percent": round(total_pnl_percent, 2),
                "total_position_value": unrealized["total_position_value"],
                "trades_count": realized["trades_count"]
            }
            
        except Exception as e:
            logger.error(f"獲取 PnL 摘要失敗: {str(e)}", exc_info=True)
            raise
    
    async def _fetch_current_prices(
        self,
        positions: List[FollowerPosition]
    ) -> Dict[str, float]:
        """
        獲取當前市價（從 MockExchange）
        
        Args:
            positions: 倉位列表
            
        Returns:
            交易對價格字典 {"BTC/USDT": 50000.0, ...}
        """
        try:
            # 創建 MockExchange 實例（不需要真實憑證）
            exchange = MockExchange(
                api_key="mock_key",
                api_secret="mock_secret"
            )
            
            # 模擬市價（實際應該從交易所獲取）
            # 這裡使用簡化邏輯：當前價格 = 入場價格 * 1.05（模擬 5% 漲幅）
            current_prices = {}
            for pos in positions:
                if pos.entry_price:
                    # 模擬價格波動：±5%
                    current_prices[pos.symbol] = pos.entry_price * 1.05
                else:
                    current_prices[pos.symbol] = 0.0
            
            logger.debug(f"獲取當前市價: {current_prices}")
            return current_prices
            
        except Exception as e:
            logger.error(f"獲取當前市價失敗: {str(e)}")
            # 返回空字典，使用入場價格作為當前價格
            return {}


# 全域實例
_pnl_service_instance: Optional[PnLService] = None


def get_pnl_service(db: AsyncSession) -> PnLService:
    """
    獲取 PnLService 實例
    
    Args:
        db: 資料庫 session
        
    Returns:
        PnLService 實例
    """
    return PnLService(db)
