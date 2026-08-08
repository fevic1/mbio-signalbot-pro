from pathlib import Path


def test_main_registers_adaptive_dca_supervisor():
    text = Path("main.py").read_text(encoding="utf-8")
    assert "from monitoring.adaptive_dca_supervisor import adaptive_dca_supervisor_loop" in text
    assert '("adaptive_dca", adaptive_dca_supervisor_loop())' in text
    assert '("trailing_dca", update_trailing_dca())' not in text
