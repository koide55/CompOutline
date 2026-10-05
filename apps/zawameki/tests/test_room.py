import pytest

from zawameki.room import LOST_TTL, Rejected, Room, weather


def make():
    r = Room(1, "1234", "key", "test", opened_at=1000.0)
    for i in range(20):
        r.connect(f"S{i:05d}")
    return r


def test_weather_thresholds():
    assert weather(100, 0) == "sunny"
    assert weather(100, 4) == "sunny"
    assert weather(100, 7) == "fair"
    assert weather(100, 15) == "cloudy"
    assert weather(100, 30) == "rain"
    assert weather(100, 40) == "storm"


def test_small_class_is_not_stormy():
    # 5人中2人が迷子でも、3人未満なら「晴れ」より悪くしない
    assert weather(5, 2) == "fair"
    assert weather(5, 3) == "storm"


def test_lost_decays():
    r = make()
    r.press_lost("S00000", 1000)
    assert r.counts(1000 + LOST_TTL - 1)["lost"] == 1
    assert r.counts(1000 + LOST_TTL + 1)["lost"] == 0


def test_lost_of_disconnected_student_is_not_counted():
    r = make()
    r.press_lost("S00000", 1000)
    r.disconnect("S00000")
    assert r.counts(1001)["lost"] == 0


def test_got_clears_lost_and_counts_aha():
    r = make()
    r.press_lost("S00001", 1000)
    r.press_got("S00001", 1010)
    c = r.counts(1011)
    assert c["lost"] == 0 and c["aha"] == 1
    r.press_got("S00002", 1012)   # 迷子でなかった人の「わかった！」は数えない
    assert r.counts(1013)["aha"] == 1


def test_pace_toggle():
    r = make()
    r.press_pace("S00000", "slow", 1000)
    assert r.counts(1001)["slow"] == 1
    r.press_pace("S00000", "slow", 1002)   # もう一度で取り消し
    assert r.counts(1003)["slow"] == 0
    with pytest.raises(Rejected):
        r.press_pace("S00000", "sideways", 1004)


def test_fireworks_when_confusion_resolves():
    r = make()
    t = 1000.0
    for i in range(8):
        r.press_lost(f"S{i:05d}", t)
    for k in range(5):
        assert r.record(t + k)["fireworks"] == 0
    for i in range(6):
        r.press_got(f"S{i:05d}", t + 10)
    c = r.record(t + 11)
    assert c["fireworks"] == 6
    assert r.record(t + 12)["fireworks"] == 0   # 続けては上げない


def test_post_kinds_and_limits():
    r = make()
    p = r.post("S00000", "naive", "  素朴な疑問  ", False, 1000)
    assert p.kind == "naive" and p.text == "素朴な疑問" and p.named is None
    with pytest.raises(Rejected):
        r.post("S00000", "question", "続けて", False, 1005)      # 重い投稿は30秒に1件
    r.post("S00000", "comment", "コメントは別枠", False, 1005)
    with pytest.raises(Rejected):
        r.post("S00001", "comment", "x" * 81, False, 1005)
    with pytest.raises(Rejected):
        r.post("S00001", "spam", "x", False, 1005)
    with pytest.raises(Rejected):
        r.post("S00001", "opinion", "   ", False, 1005)
    named = r.post("S00002", "opinion", "記名します", True, 1005)
    assert named.named == "S00002"
    assert "named" not in named.public()


def test_comments_can_be_paused_but_questions_cannot():
    r = make()
    r.update_settings({"comments_open": False})
    with pytest.raises(Rejected):
        r.post("S00000", "comment", "止まっている", False, 1000)
    r.post("S00000", "question", "質問は送れる", False, 1000)


def test_metoo_toggle_and_not_on_comments():
    r = make()
    q = r.post("S00000", "question", "Q", False, 1000)
    c = r.post("S00001", "comment", "C", False, 1000)
    r.metoo("v1", q.id)
    r.metoo("v2", q.id)
    assert len(q.voters) == 2
    r.metoo("v1", q.id)
    assert len(q.voters) == 1
    with pytest.raises(Rejected):
        r.metoo("v1", c.id)


def test_hidden_posts_are_not_visible():
    r = make()
    q = r.post("S00000", "question", "Q", False, 1000)
    r.mark(q.id, "hidden")
    assert r.visible_posts() == []
    with pytest.raises(Rejected):
        r.metoo("v1", q.id)


def test_ng_words_are_masked():
    r = Room(1, "1234", "k", "t", 0, ng_words=("ばか",))
    r.connect("S00000")
    assert r.post("S00000", "comment", "ばかな", False, 1).text == "＊＊な"


def test_control_characters_are_removed():
    r = make()
    assert r.post("S00000", "comment", "a\x00b\nc", False, 1000).text == "ab c"
