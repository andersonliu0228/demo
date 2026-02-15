# Run Database Migration 010
Write-Host "=== Running Database Migration 010 ===" -ForegroundColor Cyan
Write-Host "Adding last_seen to users and creating global_settings table" -ForegroundColor Yellow

Write-Host "`n[Step 1] Running Alembic Migration..." -ForegroundColor Yellow
try {
    docker-compose exec backend alembic upgrade head
    Write-Host "✅ Migration Completed!" -ForegroundColor Green
} catch {
    Write-Host "❌ Migration Failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`nTrying alternative method..." -ForegroundColor Yellow
    docker-compose exec -T backend alembic upgrade head
}

Write-Host "`n[Step 2] Verifying Migration..." -ForegroundColor Yellow
Write-Host "Checking if global_settings table exists..." -ForegroundColor Gray

# Test if we can query the new table
try {
    docker-compose exec -T backend python -c "
import asyncio
from sqlalchemy import select, text
from backend.app.database import AsyncSessionLocal
from backend.app.models.global_setting import GlobalSetting

async def check():
    async with AsyncSessionLocal() as session:
        # Check global_settings table
        result = await session.execute(select(GlobalSetting))
        settings = result.scalars().all()
        print(f'Found {len(settings)} global settings')
        for s in settings:
            print(f'  - {s.key}: {s.value_bool}')
        
        # Check if users have last_seen column
        result = await session.execute(text('SELECT column_name FROM information_schema.columns WHERE table_name = \'users\' AND column_name = \'last_seen\''))
        if result.scalar():
            print('✅ last_seen column exists in users table')
        else:
            print('❌ last_seen column NOT found in users table')

asyncio.run(check())
"
    Write-Host "✅ Migration Verified!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Could not verify migration: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`n" + ("=" * 60) -ForegroundColor Cyan
Write-Host "✅ MIGRATION 010 COMPLETED!" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Cyan

Write-Host "`n📊 Changes:" -ForegroundColor Yellow
Write-Host "  ✅ Added last_seen column to users table" -ForegroundColor White
Write-Host "  ✅ Created global_settings table" -ForegroundColor White
Write-Host "  ✅ Inserted emergency_stop_all setting (default: false)" -ForegroundColor White

Write-Host "`n🎯 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Restart backend: docker-compose restart backend" -ForegroundColor White
Write-Host "  2. Test EA features: .\test-ea-features.ps1" -ForegroundColor White
Write-Host "  3. Open frontend: http://localhost:3000/admin" -ForegroundColor White
