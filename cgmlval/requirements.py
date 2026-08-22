# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# The requirement table transcribed from the testing specification
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

from collections import namedtuple

MUST = "MUST"
SHOULD = "SHOULD"
MAY = "MAY"

CORE = "CORE"
EXT_COMPLETENESS = "EXT-COMPLETENESS"
EXT_DISPLAY = "EXT-DISPLAY"
EXT_PLATFORM = "EXT-PLATFORM"

# Scope classes: which part of the suite can check the requirement.
# validator   - checkable on a document (the catalog's L1-L4 rows)
# integration - implementation behaviour (the catalog's INT rows only)
# write-only  - [W]-sense only, checkable on produced documents alone
VALIDATOR = "validator"
INTEGRATION = "integration"
WRITE_ONLY = "write-only"

Req = namedtuple("Req", "level senses profile scope")

REQUIREMENTS = {
    # 5.1 Document
    "CGML-5.1-1": Req(MUST, "RWX", CORE, VALIDATOR),
    "CGML-5.1-2": Req(MUST, "RW", CORE, VALIDATOR),
    "CGML-5.1-3": Req(MAY, "R", CORE, VALIDATOR),
    # 5.2 Special characters
    "CGML-5.2-1": Req(MUST, "RW", CORE, VALIDATOR),
    # 5.3 XML text comments
    "CGML-5.3-1": Req(MUST, "R", CORE, VALIDATOR),
    # 5.4 Format version
    "CGML-5.4-1": Req(MUST, "RWX", CORE, VALIDATOR),
    "CGML-5.4-2": Req(MUST, "RWX", CORE, VALIDATOR),
    # 5.5 Data keys
    "CGML-5.5-1": Req(MUST, "RW", CORE, VALIDATOR),
    "CGML-5.5-2": Req(SHOULD, "RW", CORE, VALIDATOR),
    "CGML-5.5-3": Req(MUST, "RWX", CORE, VALIDATOR),
    "CGML-5.5-4": Req(MUST, "RWX", CORE, VALIDATOR),
    # 5.6 Graph
    "CGML-5.6-1": Req(MUST, "RWX", CORE, VALIDATOR),
    "CGML-5.6-2": Req(MUST, "RW", CORE, VALIDATOR),
    "CGML-5.6-3": Req(MUST, "RW", CORE, VALIDATOR),
    # 5.7 Node
    "CGML-5.7-1": Req(MUST, "RWX", CORE, VALIDATOR),
    "CGML-5.7-2": Req(MAY, "R", CORE, VALIDATOR),
    # 5.8 Edge
    "CGML-5.8-1": Req(MUST, "RWX", CORE, VALIDATOR),
    "CGML-5.8-2": Req(MAY, "W", CORE, VALIDATOR),
    "CGML-5.8-3": Req(MUST, "RW", CORE, VALIDATOR),
    # 5.9 Identifiers
    "CGML-5.9-1": Req(MUST, "RWX", CORE, VALIDATOR),
    "CGML-5.9-2": Req(MUST, "RWX", CORE, VALIDATOR),
    "CGML-5.9-3": Req(MUST, "RWX", CORE, VALIDATOR),
    "CGML-5.9-4": Req(MUST, "RWX", CORE, VALIDATOR),
    # 6.1 State machine
    "CGML-6.1-1": Req(MUST, "RWX", CORE, VALIDATOR),
    "CGML-6.1-2": Req(MUST, "RWX", CORE, VALIDATOR),
    "CGML-6.1-3": Req(MAY, "RW", CORE, INTEGRATION),
    "CGML-6.1-4": Req(MUST, "RWX", CORE, VALIDATOR),
    "CGML-6.1-5": Req(MAY, "RW", CORE, INTEGRATION),
    # 6.2 Simple state
    "CGML-6.2-1": Req(MUST, "R", CORE, INTEGRATION),
    "CGML-6.2-2": Req(MAY, "RWX", CORE, INTEGRATION),
    "CGML-6.2-3": Req(MUST, "RWX", CORE, VALIDATOR),
    "CGML-6.2-4": Req(MAY, "RW", CORE, INTEGRATION),
    "CGML-6.2-5": Req(MAY, "RW", CORE, INTEGRATION),
    # 6.3 Transition
    "CGML-6.3-1": Req(MAY, "RW", CORE, INTEGRATION),
    "CGML-6.3-2": Req(MUST, "RWX", CORE, VALIDATOR),
    "CGML-6.3-3": Req(MAY, "R", CORE, INTEGRATION),
    "CGML-6.3-4": Req(MUST, "RWX", CORE, VALIDATOR),
    "CGML-6.3-5": Req(MUST, "RW", CORE, VALIDATOR),
    # 6.4 Pseudostates and final state
    "CGML-6.4-1": Req(MUST, "RWX", CORE, VALIDATOR),
    "CGML-6.4-2": Req(MUST, "RWX", CORE, VALIDATOR),
    "CGML-6.4-3": Req(MAY, "RW", CORE, INTEGRATION),
    "CGML-6.4-4-1": Req(MUST, "RW", CORE, VALIDATOR),
    "CGML-6.4-4-2": Req(MUST, "RWX", CORE, VALIDATOR),
    # 6.5 Composite state and region
    "CGML-6.5-1": Req(MUST, "RW", CORE, VALIDATOR),
    "CGML-6.5-2": Req(MUST, "RW", CORE, VALIDATOR),
    "CGML-6.5-3": Req(MAY, "W", CORE, WRITE_ONLY),
    "CGML-6.5-4": Req(MUST, "RWX", CORE, VALIDATOR),
    # 6.6 Comment
    "CGML-6.6-1": Req(MUST, "RWX", CORE, VALIDATOR),
    "CGML-6.6-2": Req(MAY, "RW", CORE, INTEGRATION),
    "CGML-6.6-3": Req(SHOULD, "R", CORE, INTEGRATION),
    # 6.7 Comment-subject links
    "CGML-6.7-1": Req(MUST, "RWX", CORE, VALIDATOR),
    "CGML-6.7-2": Req(MUST, "RWX", CORE, VALIDATOR),
    "CGML-6.7-3": Req(MAY, "RW", CORE, INTEGRATION),
    # 6.8 Events, guards, behaviour
    "CGML-6.8-1": Req(MUST, "RW", CORE, VALIDATOR),
    "CGML-6.8-2": Req(MUST, "RW", CORE, VALIDATOR),
    "CGML-6.8-3": Req(MUST, "RW", CORE, VALIDATOR),
    "CGML-6.8-4": Req(MUST, "RW", CORE, VALIDATOR),
    "CGML-6.8-5": Req(MAY, "RW", CORE, VALIDATOR),
    "CGML-6.8-6": Req(MAY, "RW", CORE, VALIDATOR),
    "CGML-6.8-7": Req(MUST, "RWX", CORE, VALIDATOR),
    "CGML-6.8-8": Req(MUST, "RW", CORE, VALIDATOR),
    # 6.9 Document metadata
    "CGML-6.9-1": Req(MUST, "RWX", CORE, VALIDATOR),
    "CGML-6.9-2": Req(MUST, "RWX", CORE, VALIDATOR),
    "CGML-6.9-3": Req(MUST, "RWX", CORE, VALIDATOR),
    "CGML-6.9-4-1": Req(MAY, "R", CORE, VALIDATOR),
    "CGML-6.9-4-2": Req(MAY, "R", CORE, VALIDATOR),
    "CGML-6.9-4-3": Req(MAY, "R", CORE, VALIDATOR),
    "CGML-6.9-4-4": Req(MAY, "R", CORE, VALIDATOR),
    "CGML-6.9-4-5": Req(MAY, "R", CORE, VALIDATOR),
    "CGML-6.9-4-6": Req(MAY, "R", CORE, VALIDATOR),
    "CGML-6.9-5": Req(MAY, "R", CORE, VALIDATOR),
    # 7.1 Geometry types
    "CGML-7.1-1": Req(MUST, "RWX", CORE, VALIDATOR),
    # 7.2 Base geometry format
    "CGML-7.2-1-1": Req(MUST, "RW", CORE, VALIDATOR),
    "CGML-7.2-1-2": Req(MUST, "RW", CORE, VALIDATOR),
    "CGML-7.2-1-3": Req(MUST, "RW", CORE, VALIDATOR),
    "CGML-7.2-1-4": Req(MUST, "RW", CORE, VALIDATOR),
    "CGML-7.2-1-5": Req(MUST, "RW", CORE, VALIDATOR),
    "CGML-7.2-1-6": Req(MUST, "RW", CORE, VALIDATOR),
    "CGML-7.2-2": Req(MUST, "RWX", CORE, VALIDATOR),
    "CGML-7.2-3": Req(MUST, "R", CORE, INTEGRATION),
    # 8 EXT-COMPLETENESS
    "CGML-8.1-1": Req(MUST, "RW", EXT_COMPLETENESS, INTEGRATION),
    "CGML-8.2-1": Req(MUST, "RW", EXT_COMPLETENESS, INTEGRATION),
    "CGML-8.2-2": Req(MUST, "RW", EXT_COMPLETENESS, INTEGRATION),
    "CGML-8.3-1": Req(MUST, "RW", EXT_COMPLETENESS, INTEGRATION),
    "CGML-8.3-2": Req(MUST, "RW", EXT_COMPLETENESS, INTEGRATION),
    "CGML-8.4-1": Req(MAY, "RW", EXT_COMPLETENESS, INTEGRATION),
    "CGML-8.5-1": Req(MAY, "RWX", EXT_COMPLETENESS, INTEGRATION),
    "CGML-8.5-2": Req(MUST, "X", EXT_COMPLETENESS, VALIDATOR),
    # 9 EXT-DISPLAY
    "CGML-9.1-1": Req(MUST, "RW", EXT_DISPLAY, INTEGRATION),
    "CGML-9.1-2": Req(MUST, "W", EXT_DISPLAY, WRITE_ONLY),
    "CGML-9.2-1": Req(MAY, "RW", EXT_DISPLAY, VALIDATOR),
    "CGML-9.3-1": Req(MAY, "RW", EXT_DISPLAY, VALIDATOR),
    "CGML-9.3-2": Req(MAY, "RW", EXT_DISPLAY, INTEGRATION),
    # 10 EXT-PLATFORM
    "CGML-10.1-1": Req(MAY, "RW", EXT_PLATFORM, INTEGRATION),
    "CGML-10.1-2": Req(MUST, "RWX", EXT_PLATFORM, VALIDATOR),
    "CGML-10.1-3": Req(MUST, "RWX", EXT_PLATFORM, VALIDATOR),
    "CGML-10.2-1": Req(MAY, "RW", EXT_PLATFORM, INTEGRATION),
    "CGML-10.3-1": Req(MUST, "RW", EXT_PLATFORM, INTEGRATION),
    # Appendices
    "CGML-appendix-A-1": Req(MUST, "RWX", CORE, VALIDATOR),
    "CGML-appendix-B-1": Req(MUST, "RWX", CORE, VALIDATOR),
}
