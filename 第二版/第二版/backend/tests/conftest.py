"""
Pytest 配置和共用 fixtures
"""
import pytest
import pytest_asyncio
from hypothesis import settings, Verbosity, HealthCheck

# 配置 Hypothesis
settings.register_profile(
    "default",
    max_examples=100,
    verbosity=Verbosity.normal,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None  # 禁用測試超時，因為異步測試可能較慢
)
settings.register_profile(
    "ci",
    max_examples=200,
    verbosity=Verbosity.verbose,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None
)
settings.load_profile("default")


# 配置 pytest-asyncio
def pytest_configure(config):
    """配置 pytest"""
    config.addinivalue_line(
        "markers", "asyncio: mark test as an asyncio test"
    )
