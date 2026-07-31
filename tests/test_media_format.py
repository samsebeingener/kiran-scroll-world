"""Unit tests for media aspect / encode helpers."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import media_format as mf  # noqa: E402
import pytest  # noqa: E402


def test_grid_cols_rows_for_m6() -> None:
    """M=6 is one supported grid (3×2), not a code default."""
    assert mf.grid_cols_rows(6) == (3, 2)


def test_grid_cols_rows_for_m3_and_m9() -> None:
    assert mf.grid_cols_rows(3) == (3, 1)
    assert mf.grid_cols_rows(9) == (3, 3)


def test_encode_dimensions_480p_16_9() -> None:
    assert mf.encode_dimensions("480p", "16:9") == (854, 480)


def test_encode_dimensions_480p_9_16() -> None:
    w, h = mf.encode_dimensions("480p", "9:16")
    assert w == 480
    assert h == 854


def test_resolve_cell_aspect_from_meta() -> None:
    assert mf.resolve_cell_aspect(None, {"media_aspect_ratio": "3:4"}) == "3:4"


def test_resolve_cell_aspect_legacy_alias() -> None:
    assert mf.resolve_cell_aspect(None, {"video_aspect_ratio": "9:16"}) == "9:16"


def test_resolve_cell_aspect_required_raises() -> None:
    with pytest.raises(SystemExit):
        mf.resolve_cell_aspect(None, {}, required=True)


def test_aspect_close_accepts_matching_ratio() -> None:
    assert mf.aspect_close(854, 480, "16:9")


def test_aspect_close_rejects_square_for_16_9() -> None:
    assert not mf.aspect_close(480, 480, "16:9")


def test_board_aspect_ratio_m6_cell_16_9() -> None:
    """8:3 = 3×2 grid of 16:9 cells — math for request-aspect choice / slice check."""
    assert mf.board_aspect_ratio(6, "16:9") == "8:3"


def test_board_aspect_ratio_m3_cell_16_9() -> None:
    assert mf.board_aspect_ratio(3, "16:9") == "16:3"


def test_choose_request_aspect_exact_match() -> None:
    supported = {"16:9", "3:1", "1:1"}
    assert mf.choose_request_aspect(3, 3, "16:9", supported) == "16:9"


def test_choose_request_aspect_picks_nearest_wider() -> None:
    supported = {"16:9", "3:1", "1:1"}
    # M=6 grid 3×2 of 16:9 → board 8:3 ≈ 2.667 → nearest >= is 3:1
    assert mf.choose_request_aspect(3, 2, "16:9", supported) == "3:1"


def test_choose_request_aspect_raises_when_nothing_covers() -> None:
    supported = {"16:9", "1:1"}
    with pytest.raises(ValueError):
        # board 16:3 ≈ 5.33 — nothing wide enough
        mf.choose_request_aspect(3, 1, "16:9", supported)


def test_resolve_encode_dimensions_default_480p() -> None:
    w, h = mf.resolve_encode_dimensions(None, {"media_aspect_ratio": "16:9"})
    assert (w, h) == (854, 480)
