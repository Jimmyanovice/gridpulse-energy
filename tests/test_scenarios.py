import pandas as pd

from src.scenarios import simulate_storage_dispatch


def test_storage_state_stays_within_capacity():
    frame = pd.DataFrame(
        {
            "timestamp": pd.date_range("2020-01-01", periods=8, freq="h", tz="UTC"),
            "net_load_mw": [20, 20, 100, 100, 100, 20, 20, 20],
            "predicted_net_load_mw": [20, 20, 100, 100, 100, 20, 20, 20],
        }
    )
    result, metrics = simulate_storage_dispatch(
        frame,
        peak_threshold_mw=80,
        capacity_mwh=100,
        max_power_mw=50,
        charge_power_mw=20,
        efficiency=0.9,
    )
    assert result["storage_soc_mwh"].between(0, 100).all()
    assert metrics["min_soc_mwh"] >= 0
    assert metrics["max_soc_mwh"] <= 100


def test_reserve_is_held_until_an_emergency_forecast():
    frame = pd.DataFrame(
        {
            "timestamp": pd.date_range("2020-01-01", periods=2, freq="h", tz="UTC"),
            "net_load_mw": [100, 130],
            "predicted_net_load_mw": [100, 130],
        }
    )
    result, _ = simulate_storage_dispatch(
        frame,
        peak_threshold_mw=80,
        emergency_threshold_mw=120,
        capacity_mwh=200,
        max_power_mw=50,
        charge_power_mw=0,
        efficiency=1.0,
        reserve_fraction=0.30,
    )
    assert result.loc[0, "storage_dispatch_mw"] == 20
    assert result.loc[1, "storage_dispatch_mw"] == 50
