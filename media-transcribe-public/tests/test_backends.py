import argparse
from pathlib import Path

from media_transcribe_public import cli


def test_publish_local_uses_cache_when_no_output_dir(tmp_path: Path) -> None:
    note_path = tmp_path / "note.md"
    note_path.write_text("# Test\n", encoding="utf-8")

    result = cli.publish_local("Test", "# Test\n", None, note_path)

    assert result == {"backend": "local", "ok": True, "path": str(note_path)}


def test_publish_local_writes_unique_markdown(tmp_path: Path) -> None:
    existing = tmp_path / "Episode.md"
    existing.write_text("old", encoding="utf-8")

    result = cli.publish_local("Episode", "# Episode\n", str(tmp_path), tmp_path / "cache.md")

    assert result["backend"] == "local"
    assert result["ok"] is True
    assert Path(result["path"]).name == "Episode-2.md"
    assert Path(result["path"]).read_text(encoding="utf-8") == "# Episode\n"


def test_publish_obsidian_stays_inside_vault(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()

    result = cli.publish_obsidian(
        "Interview",
        "# Interview\n",
        vault_path=str(vault),
        vault_folder="Transcripts",
        meta={"duration": "1分钟", "source": "input.mp3"},
    )

    output = Path(result["path"])
    assert output.parent == vault / "Transcripts"
    text = output.read_text(encoding="utf-8")
    assert text.startswith("---\ntags:\n  - media-transcribe\n")
    assert "# Interview" in text


def test_legacy_skip_youdao_maps_to_none() -> None:
    args = argparse.Namespace(skip_youdao=True, note_backend="local", folder_id=None, destination=None)

    normalized = cli.normalize_legacy_args(args)

    assert normalized.note_backend == "none"


def test_legacy_folder_id_maps_to_youdao_destination() -> None:
    args = argparse.Namespace(
        skip_youdao=False,
        note_backend="youdao",
        folder_id="folder-123",
        destination=None,
    )

    normalized = cli.normalize_legacy_args(args)

    assert normalized.destination == "folder-123"


def test_default_cache_dir_respects_environment(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MEDIA_TRANSCRIBE_CACHE_DIR", str(tmp_path / "cache"))

    assert cli.default_cache_dir() == tmp_path / "cache"
