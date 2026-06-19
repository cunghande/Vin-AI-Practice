from __future__ import annotations

from pathlib import Path

from agent_advanced import AdvancedAgent
from agent_baseline import BaselineAgent
from config import LabConfig
from memory_store import UserProfileStore
from model_provider import ProviderConfig


def make_config(tmp_path: Path):
    """Build an isolated config for tests."""

    state_dir = tmp_path / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    return LabConfig(
        base_dir=tmp_path,
        data_dir=tmp_path / "data",
        state_dir=state_dir,
        compact_threshold_tokens=120,
        compact_keep_messages=2,
        model=ProviderConfig(provider="openai", model_name="gpt-4.1-mini", temperature=0.0),
        judge_model=ProviderConfig(provider="openai", model_name="gpt-4.1-mini", temperature=0.0),
    )


def test_user_markdown_read_write_edit(tmp_path: Path) -> None:
    """Verify `User.md` can be created, updated, and edited."""

    store = UserProfileStore(tmp_path / "profiles")
    default_text = store.read_text("user-1")
    assert "User Profile" in default_text

    path = store.write_text("user-1", "# User Profile\n- name: An\n- location: Da Nang\n")
    assert path.exists()
    assert "An" in store.read_text("user-1")

    assert store.edit_text("user-1", "Da Nang", "Hanoi")
    updated = store.read_text("user-1")
    assert "Hanoi" in updated


def test_compact_trigger(tmp_path: Path) -> None:
    """Verify long threads trigger compaction."""

    config = make_config(tmp_path)
    agent = AdvancedAgent(config=config, force_offline=True)

    for idx in range(8):
        agent.reply(
            "user-1",
            "thread-1",
            f"Turn {idx}: Mình đang bổ sung rất nhiều ngữ cảnh dài để ép compact hoạt động. "
            f"Mỗi lượt đều thêm một đoạn văn khá dài về memory system, trade-off và profile cập nhật."
        )

    assert agent.compaction_count("thread-1") > 0
    context = agent.compact_memory.context("thread-1")
    assert len(context["messages"]) <= config.compact_keep_messages


def test_cross_session_recall(tmp_path: Path) -> None:
    """Verify advanced remembers across sessions and baseline does not."""

    config = make_config(tmp_path)
    baseline = BaselineAgent(config=config, force_offline=True)
    advanced = AdvancedAgent(config=config, force_offline=True)

    intro = "Mình tên là An, mình ở Đà Nẵng, mình đang làm MLOps engineer và thích trả lời ngắn gọn theo 3 bullet."
    baseline.reply("user-1", "baseline-chat", intro)
    advanced.reply("user-1", "advanced-chat", intro)

    baseline_answer = baseline.reply("user-1", "baseline-recall", "Mình tên gì?")["reply"]
    advanced_answer = advanced.reply("user-1", "advanced-recall", "Mình tên gì?")["reply"]

    assert "An" not in baseline_answer
    assert "An" in advanced_answer
    assert "3 bullet" in advanced.reply("user-1", "advanced-recall-2", "Style mình thích là gì?")["reply"]


def test_compact_reduces_prompt_load_on_long_thread(tmp_path: Path) -> None:
    """Compare prompt load of baseline vs advanced on a long thread."""

    config = make_config(tmp_path)
    baseline = BaselineAgent(config=config, force_offline=True)
    advanced = AdvancedAgent(config=config, force_offline=True)

    long_turns = [
        "Đây là một lượt rất dài để đẩy context lên cao. Mình muốn agent giữ tên, nghề, nơi ở, style và nhiều nhắc lại về trade-off recall/token cost.",
        "Tiếp tục bổ sung ngữ cảnh dài hơn nữa, nhắc lại rằng style ưu tiên là 3 bullet, có ví dụ thực chiến và bám vào trade-off.",
        "Mình đang cố tình lặp nhiều ý để baseline phải mang theo nhiều history hơn và compact memory của advanced phải nén bớt.",
        "Lượt này vẫn tiếp tục nhắc về memory system, User.md, prompt tokens processed và cross-session recall trong benchmark.",
        "Đoạn này còn dài hơn để tạo pressure thật sự lên short-term memory và làm cho summary phải xuất hiện.",
        "Một lượt khác với nội dung dài, đủ để giữ cho prompt load không còn nhỏ nữa trong baseline.",
        "Lại thêm một đoạn dài tương tự, có nhắc đến Đà Nẵng, MLOps engineer và style 3 bullet để persistent memory có dữ liệu.",
        "Lượt cuối cùng vẫn dài, nhằm ép compact để giảm prompt tokens processed.",
    ]

    for idx, turn in enumerate(long_turns):
        baseline.reply("user-1", "baseline-long", f"{idx}. {turn}")
        advanced.reply("user-1", "advanced-long", f"{idx}. {turn}")

    assert advanced.prompt_token_usage("advanced-long") < baseline.prompt_token_usage("baseline-long")
