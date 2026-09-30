"""The printed comparator of every bar matches its registered direction (HD-PRINT-BARS).

Before the fix the report printed the operator dict as a literal and the
summary printed "<= 2.0" for the strict "> 2.0" residual bar.
"""

from harness import run_test as RT

ROWS = [("resid_ic_tstat_nw", 2.29, 2.0, "gt", "PASS"),
        ("paired_delta_ls_tstat", -1.01, -2.0, "ge", "PASS"),
        ("some_ceiling", 0.5, 1.0, "le", "PASS"),
        ("some_strict_ceiling", 0.5, 1.0, "lt", "PASS")]


def test_bar_ops_cover_every_direction():
    assert RT.BAR_OPS == {"ge": ">=", "gt": ">", "le": "<=", "lt": "<"}


def test_report_prints_the_registered_comparator(capsys):
    RT._print_bars(ROWS, "Stage 2 bars")
    out = capsys.readouterr().out
    assert "{" not in out and "[cd]" not in out
    lines = [ln for ln in out.splitlines() if ln.strip().startswith(tuple(r[0] for r in ROWS))]
    assert len(lines) == 4
    for ln, (_, _, _, d, _) in zip(lines, ROWS):
        assert f"  {RT.BAR_OPS[d]:<2} " in ln


def test_summary_prints_the_registered_comparator(tmp_path):
    header = {"title": "RUN 999 TEST", "harness_sha": "h", "config_sha": "c", "composite_sha": "p",
              "data_sha": "d", "eval_start": "1999-01-01", "eval_end": "2022-12-31",
              "include_holdout": False, "composite": "v0"}
    rec = RT._summary_record("X", "2", {}, None, ROWS, "PASS")
    path = tmp_path / "s.md"
    RT.write_summary(path, header, [rec])
    text = path.read_text()
    assert "| resid_ic_tstat_nw | " in text and "| > 2.0 | PASS |" in text
    assert "| >= -2.0 | PASS |" in text
    assert "| <= 1.0 | PASS |" in text and "| < 1.0 | PASS |" in text
    assert "<= 2.0" not in text
