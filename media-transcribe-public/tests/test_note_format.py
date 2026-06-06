from media_transcribe_public import cli


def test_fallback_note_has_no_private_method_line() -> None:
    note = cli.fallback_note("Title", "这是测试文本", {"duration": 1})

    assert note.startswith("# Title\n整理时间：")
    assert "整理方式" not in note
    assert "## 清洗后全文" in note


def test_punctuate_zh_text_splits_long_asr_sentences() -> None:
    text = (
        "像我的朋友那样那么激进地去加成今年确实有非常多的朋友赚了非常多的钱"
        "对我来说我肯定加获了一些仓位但确实没有那么激进"
        "等会你说的是你受到了拨克的影响还是你受到这些观点的影响"
    )

    result = cli.punctuate_zh_text(text)
    lines = [line for line in result.splitlines() if line.strip()]

    assert len(lines) >= 2
    assert "，" in result
    assert max(len(line) for line in lines) <= 80
    assert any(line.endswith("？") for line in lines)


def test_speaker_transcript_preserves_segment_boundaries() -> None:
    segments = [
        {"start": 0, "end": 1, "speaker": "A", "text": "我觉得当你越强烈的表达有观点的时候"},
        {"start": 1, "end": 2, "speaker": "A", "text": "你会被你说出的话限制"},
        {"start": 2, "end": 3, "speaker": "A", "text": "而如果这句话是公开表达的"},
        {"start": 3, "end": 4, "speaker": "A", "text": "那肯定会有更多的限制"},
    ]

    result = cli.speaker_transcript_from_segments(segments, "")
    lines = [line for line in result.splitlines() if line.strip()]

    assert lines[0].startswith("**A**：")
    assert len(lines) >= 2
    assert "，" in result
    assert "限制而如果" not in result


def test_existing_punctuation_long_sentence_is_split_again() -> None:
    text = "这个话说出去产生影响力让你受到影响还是说你观点本身让你产生的影响。"

    result = cli.punctuate_zh_text(text)
    lines = [line for line in result.splitlines() if line.strip()]

    assert len(lines) == 1
    assert "，" in result
    assert result.endswith("？")
