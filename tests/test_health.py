from paperagent.health import check_system_health

def test_check_system_health():
    health_data = check_system_health()

    assert isinstance(health_data, dict)
    assert "status" in health_data
    assert health_data["status"] in ("healthy", "degraded")

    assert "version" in health_data
    assert health_data["version"] == "0.2.0"

    assert "sandbox_available" in health_data
    assert isinstance(health_data["sandbox_available"], bool)

    assert "python_version" in health_data
    assert "storage_dir_writable" in health_data
    assert "configured_providers" in health_data
