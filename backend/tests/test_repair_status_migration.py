from pathlib import Path
import importlib.util


def load_migration_module():
    path = Path(__file__).resolve().parents[1] / "alembic" / "versions" / "0012_simplify_repair_status_flow.py"
    spec = importlib.util.spec_from_file_location("migration_0012_simplify_repair_status_flow", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_0012_status_upgrade_map_matches_simplified_flow():
    migration = load_migration_module()

    assert migration.UPGRADE_STATUS_MAP == {
        "received": "pending",
        "diagnosis": "pending",
        "in_repair": "in_process",
        "waiting_parts": "in_process",
        "ready": "ready",
        "delivered": "delivered",
        "cancelled": "cancelled",
    }
