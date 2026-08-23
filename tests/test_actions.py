# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# The 6.8 behaviour text parser tests
#
# Copyright (C) 2026 Alexey Fedoseev <aleksey@fedoseev.net>
#
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see https://www.gnu.org/licenses/
#
# -----------------------------------------------------------------------------

from cgmlval.actions import parse


def test_empty_value_is_zero_blocks():
    for text in (None, "", "\n", "  \n  "):
        blocks, errors = parse(text)
        assert blocks == []
        assert errors == []


def test_entry_block_with_body():
    blocks, errors = parse("entry/\nLED.on();")
    assert errors == []
    assert len(blocks) == 1
    assert blocks[0].kind == "entry"
    assert blocks[0].behaviour == ["LED.on();"]


def test_inline_behaviour_after_keyword():
    blocks, _ = parse("exit/ LED.off();")
    assert blocks[0].kind == "exit"
    assert blocks[0].behaviour == ["LED.off();"]


def test_keyword_with_empty_body():
    for text in ("entry/", "exit/", "do/"):
        blocks, errors = parse(text)
        assert errors == []
        assert blocks[0].kind == text[:-1]
        assert blocks[0].behaviour == []


def test_multiple_blocks_order_preserved():
    text = "entry/\na();\n\nTIMER/\nb();\n\nexit/\nc();"
    blocks, errors = parse(text)
    assert errors == []
    assert [b.kind for b in blocks] == ["entry", "event", "exit"]
    assert blocks[1].trigger == "TIMER"
    assert blocks[1].behaviour == ["b();"]


def test_consecutive_blank_lines_make_no_empty_blocks():
    blocks, _ = parse("entry/\n\n\n\nexit/")
    assert [b.kind for b in blocks] == ["entry", "exit"]


def test_trigger_with_guard_and_behaviour():
    blocks, errors = parse("TIMER(100) [cnt > 0]/ blink()")
    assert errors == []
    block = blocks[0]
    assert block.kind == "event"
    assert block.trigger == "TIMER(100)"
    assert block.guard == "cnt > 0"
    assert block.behaviour == ["blink()"]


def test_trigger_with_guard_and_empty_behaviour():
    blocks, errors = parse("EVENT [x = 1]/")
    assert errors == []
    assert blocks[0].trigger == "EVENT"
    assert blocks[0].guard == "x = 1"
    assert blocks[0].behaviour == []


def test_event_parameters():
    for param in ("propagate", "block", "defer"):
        blocks, errors = parse("TIMER %s/ x()" % param)
        assert errors == []
        assert blocks[0].trigger == "TIMER"
        assert blocks[0].param == param


def test_parameter_with_guard():
    blocks, _ = parse("TIMER propagate [cnt > 0]/ x()")
    assert blocks[0].trigger == "TIMER"
    assert blocks[0].param == "propagate"
    assert blocks[0].guard == "cnt > 0"


def test_else_guard():
    blocks, errors = parse("[else]/ fallback()")
    assert errors == []
    assert blocks[0].trigger == ""
    assert blocks[0].guard == "else"
    assert blocks[0].behaviour == ["fallback()"]


def test_escaped_brackets_in_guard():
    blocks, errors = parse("E [Строка.Содержит(\\[Пример\\])]/")
    assert errors == []
    assert blocks[0].guard == "Строка.Содержит([Пример])"


def test_exotic_event_names_preserved():
    for trigger in ("Module.Event", "EVENT(a, b)", "Событие"):
        blocks, errors = parse(trigger + "/")
        assert errors == []
        assert blocks[0].trigger == trigger


def test_slash_inside_arguments_not_a_separator():
    blocks, _ = parse("E(a/b)/ x()")
    assert blocks[0].trigger == "E(a/b)"
    assert blocks[0].behaviour == ["x()"]


def test_multiline_behaviour_preserved():
    text = "TIMER/\nfirst();\n  indented();\nlast();"
    blocks, _ = parse(text)
    assert blocks[0].behaviour == ["first();", "  indented();", "last();"]
    assert blocks[0].verbatim == text


def test_event_without_separator():
    blocks, errors = parse("EV")
    assert errors == []
    assert blocks[0].kind == "event"
    assert blocks[0].trigger == "EV"
    assert blocks[0].guard is None
    assert blocks[0].behaviour == []


def test_event_with_guard_without_separator():
    blocks, errors = parse("EV [x > 1]")
    assert errors == []
    assert blocks[0].trigger == "EV"
    assert blocks[0].guard == "x > 1"
    assert blocks[0].behaviour == []


def test_multiline_header_standard_example():
    text = "Сенсор.ЦельПолучена\n[Счетчик.ТекущееЗначениеСчетчика >= 2]"
    blocks, errors = parse(text)
    assert errors == []
    assert blocks[0].trigger == "Сенсор.ЦельПолучена"
    assert blocks[0].guard == "Счетчик.ТекущееЗначениеСчетчика >= 2"
    assert blocks[0].behaviour == []
    assert blocks[0].verbatim == text


def test_separator_on_second_line():
    blocks, errors = parse("EV\n[g]/ act()\nmore()")
    assert errors == []
    assert blocks[0].trigger == "EV"
    assert blocks[0].guard == "g"
    assert blocks[0].behaviour == ["act()", "more()"]


def test_event_parameter_after_guard():
    blocks, errors = parse("STOP [ready] block/ halt()")
    assert errors == []
    assert (blocks[0].trigger, blocks[0].param, blocks[0].guard) == \
        ("STOP", "block", "ready")


def test_event_parameter_before_guard():
    blocks, errors = parse("START propagate [g]/")
    assert errors == []
    assert (blocks[0].trigger, blocks[0].param, blocks[0].guard) == \
        ("START", "propagate", "g")


def test_empty_event_name_is_an_error():
    blocks, errors = parse("/ x()")
    assert len(errors) == 1
    assert "empty event name" in errors[0][1]


def test_error_line_numbers():
    _, errors = parse("entry/\na()\n\n/ x()")
    assert errors == [(3, "empty event name in the event description")]
