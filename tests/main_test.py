from __future__ import annotations

from pathlib import Path
import pytest

# Adjust if your package exports are different
from pytex_lib import wtl, write_to_latex


def _write(tex_path: Path, text: str) -> None:
    tex_path.write_text(text, encoding="utf-8")


def _read(tex_path: Path) -> str:
    return tex_path.read_text(encoding="utf-8")


# -----------------------------------------------------------------------------
# wtl tests
# -----------------------------------------------------------------------------

def test_wtl_inserts_line_after_keyword(tmp_path: Path) -> None:
    tex = tmp_path / "test.tex"
    _write(
        tex,
        "\\begin{document}\n"
        "Hello\n"
        "% keyword in latex doc\n"
        "OLD\n"
        "\\end{document}\n",
    )

    wtl("NEW", keyword="% keyword in latex doc", file_path=tex)

    out = _read(tex)
    assert "% keyword in latex doc\nNEW\n\\end{document}\n" in out
    assert "OLD\n" not in out  # old line below keyword overwritten


def test_wtl_overwrites_only_one_line_below_keyword(tmp_path: Path) -> None:
    tex = tmp_path / "test.tex"
    _write(
        tex,
        "% keyword in latex doc\n"
        "LINE1_TO_OVERWRITE\n"
        "LINE2_SHOULD_REMAIN\n",
    )

    wtl("REPLACED", keyword="% keyword in latex doc", file_path=tex)

    out = _read(tex).splitlines()
    assert out[0] == "% keyword in latex doc"
    assert out[1] == "REPLACED"
    assert out[2] == "LINE2_SHOULD_REMAIN"


def test_wtl_inserts_even_if_keyword_is_last_line(tmp_path: Path) -> None:
    tex = tmp_path / "test.tex"
    _write(tex, "A\n% keyword in latex doc\n")

    wtl("X", keyword="% keyword in latex doc", file_path=tex)

    out = _read(tex)
    assert out.endswith("% keyword in latex doc\nX\n")


def test_wtl_raises_if_keyword_not_found(tmp_path: Path) -> None:
    tex = tmp_path / "test.tex"
    _write(tex, "A\nB\nC\n")

    with pytest.raises(ValueError, match="Keyword"):
        wtl("X", keyword="% keyword in latex doc", file_path=tex)


def test_wtl_strips_extra_newlines_from_x(tmp_path: Path) -> None:
    tex = tmp_path / "test.tex"
    _write(tex, "% keyword in latex doc\nOLD\n")

    wtl("X\n\n", keyword="% keyword in latex doc", file_path=tex)

    out = _read(tex)
    # Should be exactly one line written after keyword
    assert out == "% keyword in latex doc\nX\n"


def test_wtl_only_first_keyword_occurrence_is_used(tmp_path: Path) -> None:
    tex = tmp_path / "test.tex"
    _write(
        tex,
        "% keyword in latex doc\n"
        "OLD1\n"
        "middle\n"
        "% keyword in latex doc\n"
        "OLD2\n",
    )

    wtl("NEW", keyword="% keyword in latex doc", file_path=tex)

    out = _read(tex).splitlines()
    # First occurrence overwritten
    assert out[0] == "% keyword in latex doc"
    assert out[1] == "NEW"
    # Second occurrence should still have OLD2 unchanged (since we only do first)
    assert out[-2] == "% keyword in latex doc"
    assert out[-1] == "OLD2"


# -----------------------------------------------------------------------------
# decorator tests
# -----------------------------------------------------------------------------

def test_write_to_latex_decorator_writes_and_returns(tmp_path: Path) -> None:
    tex = tmp_path / "test.tex"
    _write(tex, "% keyword in latex doc\nOLD\n")

    @write_to_latex
    def compute_square(x: int) -> str:
        return f"{x*x}"

    ret = compute_square(4, file_path=tex, keyword="% keyword in latex doc")

    assert ret == "16"
    out = _read(tex).splitlines()
    assert out[0] == "% keyword in latex doc"
    assert out[1] == "16"


def test_write_to_latex_requires_file_path_and_keyword(tmp_path: Path) -> None:
    @write_to_latex
    def f() -> str:
        return "X"

    with pytest.raises(TypeError, match="file_path"):
        f(keyword="K")  # missing file_path

    with pytest.raises(TypeError, match="keyword"):
        f(file_path=tmp_path / "test.tex")  # missing keyword


def test_write_to_latex_raises_if_return_not_str(tmp_path: Path) -> None:
    tex = tmp_path / "test.tex"
    _write(tex, "% keyword in latex doc\nOLD\n")

    @write_to_latex
    def f() -> int:
        return 123  # type: ignore[return-value]

    with pytest.raises(TypeError, match="must return a str"):
        f(file_path=tex, keyword="% keyword in latex doc")


def test_write_to_latex_passes_through_function_args(tmp_path: Path) -> None:
    tex = tmp_path / "test.tex"
    _write(tex, "% keyword in latex doc\nOLD\n")

    @write_to_latex
    def greet(name: str, punctuation: str = "!") -> str:
        return f"Hi {name}{punctuation}"

    greet("Gavin", punctuation=".", file_path=tex, keyword="% keyword in latex doc")

    out = _read(tex)
    assert "Hi Gavin." in out


def test_write_to_latex_propagates_wtl_keyword_missing(tmp_path: Path) -> None:
    tex = tmp_path / "test.tex"
    _write(tex, "no keyword here\n")

    @write_to_latex
    def f() -> str:
        return "X"

    with pytest.raises(ValueError, match="Keyword"):
        f(file_path=tex, keyword="% keyword in latex doc")
