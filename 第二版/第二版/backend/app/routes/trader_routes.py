"""
Trader Routes
交易員管理 API 路由 - 客戶管理
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from backend.app.database import get_db
from backend.app.config import settings
from backend.app.services.auth_service import get_current_active_user
from backend.app.models.user import User
from backend.app.models.follower_relation import FollowerRelation, RelationStatus
from backend.app.models.global_setting import GlobalSetting

logger = logging.getLogger(__name__)

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/trader", tags=["trader"])


# Pydantic 模型
class ClientInfo(BaseModel):
    """客戶資訊"""
    id: int
    relation_id: int
    username: str
    email: str
    copy_ratio: float
    status: str
    created_at: str
    last_seen: str | None = None
    # Mock 數據欄位
    net_value: float = 10000.0
    pnl: float = 0.0
    pnl_percentage: float = 0.0


class ManageClientRequest(BaseModel):
    """管理客戶請求"""
    relation_id: int
    action: str  # 'approve', 'block', 'delete'


class UpdateClientRequest(BaseModel):
    """更新客戶設定請求"""
    relation_id: int
    copy_ratio: float | None = None
    status: str | None = None


class EmergencyStopRequest(BaseModel):
    """緊急全停請求"""
    stop_all: bool


@router.get("/clients", response_model=List[ClientInfo])
async def get_clients(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    獲取交易員名下的所有客戶
    
    返回該交易員的所有跟隨者及其跟單數據
    """
    try:
        logger.info(f"📊 獲取客戶列表: trader={current_user.username}")
        
        # 查詢所有跟隨該交易員的關係
        stmt = select(FollowerRelation).where(
            FollowerRelation.master_id == current_user.id
        )
        result = await db.execute(stmt)
        relations = result.scalars().all()
        
        # 構建客戶資訊列表
        clients = []
        for relation in relations:
            # 獲取跟隨者資訊
            follower = relation.follower
            
            # 構建客戶資訊（包含 Mock 數據）
            client_info = ClientInfo(
                id=follower.id,
                relation_id=relation.id,
                username=follower.username,
                email=follower.email,
                copy_ratio=relation.copy_ratio,
                status=relation.status,
                created_at=relation.created_at.isoformat(),
                last_seen=follower.last_seen.isoformat() if follower.last_seen else None,
                # Mock 數據
                net_value=10000.0 + (relation.id * 1000),
                pnl=200.0 * relation.id,
                pnl_percentage=2.0 * relation.id
            )
            clients.append(client_info)
        
        logger.info(f"✅ 成功獲取 {len(clients)} 個客戶")
        return clients
        
    except Exception as e:
        logger.error(f"❌ 獲取客戶列表失敗: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取客戶列表失敗: {str(e)}"
        )


@router.post("/manage-client")
async def manage_client(
    request: ManageClientRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    管理客戶狀態
    
    允許交易員核准、暫停或刪除客戶
    """
    try:
        logger.info(f"🔧 管理客戶: trader={current_user.username}, relation_id={request.relation_id}, action={request.action}")
        
        # 查詢關係
        stmt = select(FollowerRelation).where(
            FollowerRelation.id == request.relation_id,
            FollowerRelation.master_id == current_user.id
        )
        result = await db.execute(stmt)
        relation = result.scalar_one_or_none()
        
        if not relation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="找不到該客戶關係"
            )
        
        # 執行動作
        if request.action == "approve":
            relation.status = RelationStatus.ACTIVE.value
            await db.commit()
            logger.info(f"✅ 已核准客戶: relation_id={request.relation_id}")
            return {"message": "客戶已核准", "status": relation.status}
            
        elif request.action == "block":
            relation.status = RelationStatus.BLOCKED.value
            await db.commit()
            logger.info(f"⛔ 已封鎖客戶: relation_id={request.relation_id}")
            return {"message": "客戶已封鎖", "status": relation.status}
            
        elif request.action == "delete":
            await db.delete(relation)
            await db.commit()
            logger.info(f"🗑️ 已刪除客戶: relation_id={request.relation_id}")
            return {"message": "客戶已刪除"}
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"無效的動作: {request.action}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 管理客戶失敗: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"管理客戶失敗: {str(e)}"
        )


@router.patch("/update-client")
async def update_client(
    request: UpdateClientRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新客戶設定
    
    允許交易員更新客戶的跟單比例和狀態
    """
    try:
        logger.info(f"🔧 更新客戶設定: trader={current_user.username}, relation_id={request.relation_id}")
        
        # 查詢關係
        stmt = select(FollowerRelation).where(
            FollowerRelation.id == request.relation_id,
            FollowerRelation.master_id == current_user.id
        )
        result = await db.execute(stmt)
        relation = result.scalar_one_or_none()
        
        if not relation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="找不到該客戶關係"
            )
        
        # 更新跟單比例
        if request.copy_ratio is not None:
            if request.copy_ratio < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="跟單比例不能為負數"
                )
            relation.copy_ratio = request.copy_ratio
            logger.info(f"✅ 更新跟單比例: relation_id={request.relation_id}, ratio={request.copy_ratio}")
        
        # 更新狀態
        if request.status is not None:
            valid_statuses = [s.value for s in RelationStatus]
            if request.status not in valid_statuses:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"無效的狀態: {request.status}"
                )
            relation.status = request.status
            logger.info(f"✅ 更新狀態: relation_id={request.relation_id}, status={request.status}")
        
        await db.commit()
        await db.refresh(relation)
        
        return {
            "message": "客戶設定已更新",
            "relation_id": relation.id,
            "copy_ratio": relation.copy_ratio,
            "status": relation.status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 更新客戶設定失敗: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新客戶設定失敗: {str(e)}"
        )


@router.post("/emergency-stop")
async def emergency_stop(
    request: EmergencyStopRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    緊急全停開關
    
    允許交易員一鍵停止所有跟單
    
    Args:
        request: 包含 stop_all 布林值
        
    Returns:
        更新結果
    """
    try:
        logger.info(f"🚨 緊急全停請求: trader={current_user.username}, stop_all={request.stop_all}")
        
        # 查詢或創建全局設定
        stmt = select(GlobalSetting).where(
            GlobalSetting.key == "emergency_stop_all"
        )
        result = await db.execute(stmt)
        setting = result.scalar_one_or_none()
        
        if not setting:
            # 如果不存在，創建新設定
            setting = GlobalSetting(
                key="emergency_stop_all",
                value_bool=request.stop_all,
                description="緊急全停開關 - 停止所有跟單"
            )
            db.add(setting)
            logger.info(f"📝 創建緊急全停設定: stop_all={request.stop_all}")
        else:
            # 更新現有設定
            setting.value_bool = request.stop_all
            logger.info(f"🔄 更新緊急全停設定: stop_all={request.stop_all}")
        
        await db.commit()
        await db.refresh(setting)
        
        status_text = "已啟動" if request.stop_all else "已解除"
        logger.info(f"✅ 緊急全停 {status_text}")
        
        return {
            "message": f"緊急全停 {status_text}",
            "emergency_stop": setting.value_bool,
            "updated_at": setting.updated_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 緊急全停操作失敗: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"緊急全停操作失敗: {str(e)}"
        )


@router.get("/emergency-stop-status")
async def get_emergency_stop_status(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    獲取緊急全停狀態
    
    Returns:
        當前緊急全停狀態
    """
    try:
        stmt = select(GlobalSetting).where(
            GlobalSetting.key == "emergency_stop_all"
        )
        result = await db.execute(stmt)
        setting = result.scalar_one_or_none()
        
        if not setting:
            return {
                "emergency_stop": False,
                "message": "緊急全停未啟動"
            }
        
        return {
            "emergency_stop": setting.value_bool or False,
            "message": "緊急全停已啟動" if setting.value_bool else "緊急全停未啟動",
            "updated_at": setting.updated_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 獲取緊急全停狀態失敗: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取緊急全停狀態失敗: {str(e)}"
        )
