# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# The grammar fragments of §6.8 and §6.9 of the standard are executable
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

from cgmlval import actions, meta
from tests import standard_text


def test_state_block_example():
    body = standard_text.behaviour_text(standard_text.fragment('id="Scan"'))
    blocks, errors = actions.parse(body)
    assert errors == []
    assert [b.kind for b in blocks] == ["entry", "event", "exit"]
    assert blocks[0].behaviour == ["Сенсор.ПоискЦелиПоДистанции(мин)"]
    assert blocks[1].trigger == "Сенсор.ЦельПолучена"
    assert blocks[1].behaviour == ["МодульДвижения.ЗадатьКоординатуВверх(34)"]
    assert blocks[2].behaviour == ["Сенсор.ОстановкаПоиска"]


def test_transition_label_example():
    body = standard_text.behaviour_text(standard_text.fragment('id="edge0"'))
    blocks, errors = actions.parse(body, transition=True)
    assert errors == []
    assert blocks[0].trigger == "Сенсор.ЦельПолучена"
    assert blocks[0].guard == "Счетчик.ТекущееЗначениеСчетчика >= 2"
    assert blocks[0].behaviour == []


def test_escaped_guard_example():
    body = standard_text.behaviour_text(
        standard_text.fragment("TIMER [pressure"))
    blocks, errors = actions.parse(body, transition=True)
    assert errors == []
    assert blocks[0].trigger == "TIMER"
    assert blocks[0].guard == "pressure > 100 &&\ntemperature < 50"
    assert blocks[0].behaviour == ["turn_off();"]


def test_block_separator_illustration():
    body = standard_text.behaviour_text(
        standard_text.fragment("Событие1 [Условие1]"))
    blocks, errors = actions.parse(body)
    assert errors == []
    assert [(b.trigger, b.guard) for b in blocks] == \
        [("Событие1", "Условие1"), ("Событие2", "Условие2")]
    assert blocks[1].behaviour == ["Поведение_2_1", "Поведение_2_2"]


def test_metadata_example():
    body = standard_text.behaviour_text(
        standard_text.fragment('id="coreMeta"'))
    params, errors = meta.parse(body)
    assert errors == []
    assert [p.name for p in params] == [
        "platform", "standardVersion", "geometry", "name", "author",
        "contact", "description", "target"]
    assert params[1].value == "1.0"
    assert params[6].value.count("\n") == 2
    assert params[7].value == "Autoborder"
