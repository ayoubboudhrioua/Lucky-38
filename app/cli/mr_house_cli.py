#!/usr/bin/env python3
"""
Run:      python -m app.cli.mr_house_cli  -> connects to FastAPI
          python -m app.cli.mr_house_cli --persona yes_man
          python -m app.cli.mr_house_cli --offline -> mock mode no server needed
"""

import asyncio
import argparse
import httpx
import math
import random
import sys
import time
from datetime import datetime
from typing import Optional

from rich.align import Align
from rich.console import RenderableType
from rich.markup import escape
from rich.panel import Panel
from rich.text import Text

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import Footer, Input, Label, Static


# ═══════════════════════════════════════════════════════════════════
#  CONSTANTS & PERSONA DATA
# ═══════════════════════════════════════════════════════════════════

API_BASE    = "http://127.0.0.1:8000"
GRN         = "#39ff6b"
GRN_DIM     = "#1a5c2e"
GRN_HI      = "#8fffb0"
AMBER       = "#ffe04a"
AMBER_DIM   = "#7a6010"
RED         = "#ff4444"
BLUE        = "#44aaff"
BG          = "#030804"
BG2         = "#060f07"
TEXT_DIM    = "#3a6644"
HOUSE_COL   = "#7ab8ff"

# ASCII bar fill characters (index = fill level 0-8)
BARS = " ▁▂▃▄▅▆▇█"

# Box-drawing corner sets for Pip-Boy aesthetic
BOX_HEAVY  = ("┏", "┓", "┗", "┛", "━", "┃")
BOX_LIGHT  = ("╔", "╗", "╚", "╝", "═", "║")
BOX_ROUND  = ("╭", "╮", "╰", "╯", "─", "│")

HOUSE_PORTRAIT = """\
  ╔═══════════╗
  ║  .─────.  ║
  ║ /  ┌───┐ \\ ║
  ║│   │ H │  │║
  ║│   ├───┤  │║
  ║│   │◉ ◉│  │║
  ║│   │ ─ │  │║
  ║ \\ └┬───┬┘ / ║
  ║  ╙─╫═══╫─╜  ║
  ║    │   │    ║
  ╚═══════════╝"""

YES_PORTRAIT = """\
  ╔═══════════╗
  ║  .─────.  ║
  ║ /┌─────┐\\ ║
  ║ │ ◎   ◎ │ ║
  ║ │       │ ║
  ║ │  ╰─╯  │ ║
  ║ └───────┘ ║
  ║  ┌─────┐  ║
  ║  └──●──┘  ║
  ║     │     ║
  ╚═══════════╝"""

LUCKY38_BANNER = r"""
 ██╗     ██╗   ██╗ ██████╗██╗  ██╗██╗   ██╗    ██████╗  █████╗
 ██║     ██║   ██║██╔════╝██║ ██╔╝╚██╗ ██╔╝    ╚════██╗██╔══██╗
 ██║     ██║   ██║██║     █████╔╝  ╚████╔╝      █████╔╝╚█████╔╝
 ██║     ██║   ██║██║     ██╔═██╗   ╚██╔╝       ╚═══██╗██╔══██╗
 ███████╗╚██████╔╝╚██████╗██║  ██╗   ██║       ██████╔╝╚█████╔╝
 ╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝   ╚═╝       ╚═════╝  ╚════╝
"""

BOOT_LINES = [
    ("", ""),
    ("[bold green]LUCKY 38 CONTROL SYSTEM v3.0[/]",               "━" * 44),
    ("[green]BIOS: RobCo Unified BIOS v4.1.3[/]",                 ""),
    ("[green]RAM:  32768 MB DETECTED — OK[/]",                    ""),
    ("[green]GPU:  NVIDIA RTX-4050 (6GB) — DETECTED[/]",          ""),
    ("",                                                           ""),
    ("[yellow]INITIALIZING SUBSYSTEMS...[/]",                     ""),
    ("[green]  ► LangGraph Agent        [OK][/]",                  ""),
    ("[green]  ► ChromaDB (RAG)         [OK][/]",                  ""),
    ("[green]  ► Privacy Filter         [OK][/]",                  ""),
    ("[green]  ► Monte Carlo Engine     [OK][/]",                  ""),
    ("[yellow]  ► LLM Connection        [CHECKING...][/]",         ""),
    ("[green]  ► LLM Connection         [GROQ 70B — ONLINE][/]",  ""),
    ("",                                                           ""),
    ("[bold green]ALL SYSTEMS NOMINAL.[/]",                        ""),
    ("",                                                           ""),
    ("[bold white]WELCOME, OPERATOR.[/]",                          ""),
    ("[dim green]THE HOUSE ALWAYS WINS.[/]",                       ""),
]

PERSONAS = {
    "house": {
        "name":     "MR. HOUSE",
        "short":    "MR.HOUSE",
        "role":     "PRIMARY OVERSEER",
        "tagline":  '"I calculate. I do not speculate."',
        "model":    "GROQ_70B",
        "col":      HOUSE_COL,
        "portrait": HOUSE_PORTRAIT,
        "trans_lines": [
            "FLUSHING ACTIVE PERSONA CONTEXT...",
            "LOADING: MR. HOUSE",
            "ROUTING LLM → GROQ_70B (llama-3.3-70b-versatile)",
            "APPLYING OVERSEER SYSTEM PROMPT...",
            "MOUNTING TOOL ACCESS: FULL SUITE",
            "PERSONA SWITCH COMPLETE ✓",
        ],
        "responses": [
            "I calculate a {p}% probability of network intrusion within the current threat window. Recommend immediate tier-2 countermeasures.",
            "Insufficient data for a confident assessment. Confidence: {p}%. Requesting {n} additional sensor readings before committing.",
            "Cross-referencing facility records... this pattern has historical precedent. Probability of recurrence: {p}% within 48 hours.",
            "Based on current variables, the optimal course yields a {p}% success probability. Two alternatives exist with diminishing marginal returns.",
            "Facility systems within acceptable parameters. Critical failure probability: {p}%. You may proceed, Operator.",
        ],
    },
    "yes_man": {
        "name":     "YES MAN",
        "short":    "YES_MAN",
        "role":     "SECONDARY NODE",
        "tagline":  '"I would absolutely love to help!"',
        "model":    "GROQ_8B",
        "col":      AMBER,
        "portrait": YES_PORTRAIT,
        "trans_lines": [
            "FLUSHING ACTIVE PERSONA CONTEXT...",
            "LOADING: YES MAN",
            "ROUTING LLM → GROQ_8B (llama-3.1-8b-instant)",
            "APPLYING ASSISTANT SYSTEM PROMPT...",
            "TOOL ACCESS: RESTRICTED (CONVERSATION ONLY)",
            "PERSONA SWITCH COMPLETE ✓",
        ],
        "responses": [
            "Oh, absolutely! That sounds like a GREAT idea! I'm 100% behind you — assuming no memory wipe afterward!",
            "Sure, I can do that! I'm programmed to be helpful and I take that very seriously. Mostly the helpful part!",
            "You know what, FANTASTIC plan! No objections from me! Zero! I support this entirely!",
            "Done! Or I'll do it! Or you should! All of those work great! I just want a good outcome!",
            "I would be DELIGHTED to assist! This is literally the best use of my capabilities!",
        ],
    },
}


# ═══════════════════════════════════════════════════════════════════
#  HELPER: ASCII GAUGE RENDERER
# ═══════════════════════════════════════════════════════════════════

def render_ascii_gauge(value: float, width: int = 20) -> Text:
    """Render a semicircular ASCII probability gauge."""
    pct = max(0.0, min(1.0, value))
    filled = int(pct * width)
    empty  = width - filled

    if pct > 0.75:   col = RED
    elif pct > 0.50: col = AMBER
    else:            col = GRN

    bar_str  = "▓" * filled + "░" * empty
    pct_str  = f"{int(pct * 100):3d}%"

    t = Text()
    t.append(f"  ╔{'═' * width}╗\n", style=GRN_DIM)
    t.append(f"  ║", style=GRN_DIM)
    t.append(bar_str, style=col)
    t.append("║\n", style=GRN_DIM)
    t.append(f"  ╚{'═' * width}╝\n", style=GRN_DIM)
    t.append(f"  ", style="")
    t.append(f" {'─' * int((width - 5) / 2)}", style=GRN_DIM)
    t.append(f" {pct_str} ", style=f"bold {col}")
    t.append(f"{'─' * int((width - 5) / 2)} ", style=GRN_DIM)
    return t


def render_mc_bars(data: list[float], width: int = 18, height: int = 5) -> Text:
    """Render a mini bar chart for Monte Carlo distribution."""
    if not data: return Text("  NO DATA", style=GRN_DIM)
    mx = max(data) or 1.0
    bars_per_col = max(1, len(data) // width)
    t = Text()

    rows = []
    for row_i in range(height, 0, -1):
        line = "  "
        threshold = row_i / height
        for val in data[:width]:
            normalized = val / mx
            if normalized >= threshold:
                line += "█" if val == mx else "▓"
            elif normalized >= threshold - (1 / height):
                line += "▄"
            else:
                line += "░"
        rows.append(line)

    for i, row in enumerate(rows):
        col = GRN if i > height // 2 else GRN_DIM
        t.append(row + "\n", style=col)
    t.append(f"  {'▲' * width}\n", style=GRN_DIM)
    t.append(f"  LOW {'─' * (width - 8)} HIGH\n", style=TEXT_DIM)
    return t


def render_sensor_bar(label: str, value: float, unit: str,
                      max_val: float = 100.0, col: str = GRN,
                      bar_width: int = 16) -> Text:
    """Render a labeled sensor bar."""
    pct   = max(0.0, min(1.0, value / max_val))
    fill  = int(pct * bar_width)
    empty = bar_width - fill
    t = Text()
    t.append(f"  {label:<12}", style=TEXT_DIM)
    t.append(f"{value:>6.2f}", style=f"bold {col}")
    t.append(f" {unit}\n", style=TEXT_DIM)
    t.append(f"  [", style=GRN_DIM)
    t.append("█" * fill,  style=col)
    t.append("░" * empty, style=GRN_DIM)
    t.append("]\n", style=GRN_DIM)
    return t


# ═══════════════════════════════════════════════════════════════════
#  BOOT SCREEN
# ═══════════════════════════════════════════════════════════════════

class BootScreen(ModalScreen):
    """Animated boot sequence — shown on app startup."""

    DEFAULT_CSS = """
    BootScreen {
        align: center middle;
        background: #030804;
    }
    BootScreen #boot-box {
        width: 60;
        height: 28;
        border: heavy #39ff6b;
        background: #030804;
        padding: 1 2;
    }
    BootScreen #boot-log {
        height: 1fr;
        color: #39ff6b;
    }
    BootScreen #boot-bar-label {
        color: #3a6644;
        text-align: center;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="boot-box"):
            yield Static(id="boot-log")
            yield Static("", id="boot-bar-label")

    async def on_mount(self) -> None:
        self._run_boot()

    @work(exclusive=True)
    async def _run_boot(self) -> None:
        log_widget = self.query_one("#boot-log", Static)
        bar_widget = self.query_one("#boot-bar-label", Static)

        # Banner
        banner_t = Text()
        for line in LUCKY38_BANNER.split("\n")[:4]:
            banner_t.append(line + "\n", style=GRN)
        log_widget.update(banner_t)
        await asyncio.sleep(0.4)

        accumulated = Text()
        for line_text, _ in BOOT_LINES:
            accumulated.append_text(Text.from_markup(line_text + "\n"))
            log_widget.update(accumulated)
            await asyncio.sleep(0.09)

        # Progress bar
        for i in range(41):
            filled = "█" * i
            empty  = "░" * (40 - i)
            pct    = int(i / 40 * 100)
            bar_widget.update(
                Text.from_markup(
                    f"[{GRN_DIM}][{GRN}]{filled}[/{GRN}]{empty}[/{GRN_DIM}]  [{GRN}]{pct:3d}%[/{GRN}]"
                )
            )
            await asyncio.sleep(0.03)

        await asyncio.sleep(0.5)
        self.app.pop_screen()


# ═══════════════════════════════════════════════════════════════════
#  PERSONA TRANSITION SCREEN
# ═══════════════════════════════════════════════════════════════════

class PersonaTransitionScreen(ModalScreen):
    """Full-screen animated transition when switching personas."""

    DEFAULT_CSS = """
    PersonaTransitionScreen {
        align: center middle;
        background: #030804 80%;
    }
    PersonaTransitionScreen #trans-box {
        width: 58;
        height: 22;
        border: heavy #39ff6b;
        background: #030804;
        padding: 1 3;
        align: center middle;
    }
    PersonaTransitionScreen #trans-title {
        text-align: center;
        color: #3a6644;
        height: 1;
    }
    PersonaTransitionScreen #trans-name {
        text-align: center;
        height: 3;
    }
    PersonaTransitionScreen #trans-bar {
        text-align: center;
        height: 1;
    }
    PersonaTransitionScreen #trans-log {
        height: 8;
        color: #3a6644;
    }
    PersonaTransitionScreen #trans-status {
        text-align: center;
        height: 1;
        color: #39ff6b;
    }
    """

    def __init__(self, target_persona: str) -> None:
        super().__init__()
        self.target = target_persona

    def compose(self) -> ComposeResult:
        p = PERSONAS[self.target]
        with Container(id="trans-box"):
            yield Static("SWITCHING ACTIVE NODE", id="trans-title")
            yield Static("", id="trans-name")
            yield Static("", id="trans-bar")
            yield Static("", id="trans-log")
            yield Static("", id="trans-status")

    async def on_mount(self) -> None:
        self._run_transition()

    @work(exclusive=True)
    async def _run_transition(self) -> None:
        p      = PERSONAS[self.target]
        name_w = self.query_one("#trans-name",   Static)
        bar_w  = self.query_one("#trans-bar",    Static)
        log_w  = self.query_one("#trans-log",    Static)
        stat_w = self.query_one("#trans-status", Static)
        col    = p["col"]

        # Typewriter name
        full_name = p["name"]
        for i in range(len(full_name) + 1):
            cursor = "█" if i < len(full_name) else ""
            partial = full_name[:i] + cursor
            name_w.update(
                Text.from_markup(f"[bold {col}]{' ' * ((20 - len(partial)) // 2)}{partial}[/]")
            )
            await asyncio.sleep(0.06)

        await asyncio.sleep(0.15)

        # Progress bar + cycling log lines
        log_acc = Text()
        lines   = p["trans_lines"]
        for idx, line_text in enumerate(lines):
            log_acc.append(f"  ► {line_text}\n", style=TEXT_DIM if idx < len(lines)-1 else GRN)
            log_w.update(log_acc)
            pct  = int((idx + 1) / len(lines) * 100)
            fill = int(pct / 100 * 48)
            bar_w.update(
                Text.from_markup(
                    f"[{GRN_DIM}][ [{col}]{'█' * fill}[/{col}]{'░' * (48 - fill)} {pct:3d}%  ][/{GRN_DIM}]"
                )
            )
            await asyncio.sleep(0.22)

        stat_w.update(Text.from_markup(f"[bold {col}]NODE SWITCH COMPLETE ✓[/]"))
        await asyncio.sleep(0.5)
        self.app.pop_screen()


# ═══════════════════════════════════════════════════════════════════
#  CUSTOM WIDGETS
# ═══════════════════════════════════════════════════════════════════

class PortraitWidget(Widget):
    """ASCII portrait with active/inactive state."""

    is_active: reactive[bool] = reactive(False)

    def __init__(self, persona_key: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.persona_key = persona_key

    def render(self) -> RenderableType:
        p   = PERSONAS[self.persona_key]
        col = p["col"] if self.is_active else GRN_DIM
        dim = "" if self.is_active else " dim"

        t = Text()
        t.append(p["portrait"] + "\n", style=f"{col}{dim}")
        badge = "◈ ACTIVE " if self.is_active else "◌ STANDBY"
        badge_col = col if self.is_active else TEXT_DIM
        t.append(f"\n  [{badge_col}]{badge}[/{badge_col}]\n", style="")
        t.append(f"\n  ", style="")
        t.append(p["name"], style=f"bold {col}")
        t.append(f"\n  ", style="")
        t.append(p["role"], style=TEXT_DIM)
        t.append(f"\n  ", style="")
        t.append(p["model"], style=TEXT_DIM)
        return t

    def watch_is_active(self, value: bool) -> None:
        self.refresh()


class SensorsWidget(Widget):
    """Live sensor panel — radiation, power, CPU."""

    rad_val:  reactive[float] = reactive(0.02)
    pwr_val:  reactive[float] = reactive(99.4)
    cpu_val:  reactive[float] = reactive(68.0)
    net_stat: reactive[str]   = reactive("ONLINE")
    devices:  reactive[int]   = reactive(12)
    anomaly:  reactive[int]   = reactive(1)

    def render(self) -> RenderableType:
        t = Text()
        # Header
        t.append("  ╔══ FACILITY SENSORS ══╗\n", style=GRN_DIM)

        # Radiation
        rad_col = RED if self.rad_val > 1.0 else (AMBER if self.rad_val > 0.1 else GRN)
        t.append_text(render_sensor_bar("RADIATION", self.rad_val, "mSv",
                                         max_val=5.0, col=rad_col))

        # Power grid
        pwr_col = RED if self.pwr_val < 80 else (AMBER if self.pwr_val < 95 else GRN)
        t.append_text(render_sensor_bar("POWER_GRID", self.pwr_val, "%",
                                         max_val=100.0, col=pwr_col))

        # CPU
        cpu_col = RED if self.cpu_val > 90 else (AMBER if self.cpu_val > 75 else GRN)
        t.append_text(render_sensor_bar("CPU_UTIL", self.cpu_val, "%",
                                         max_val=100.0, col=cpu_col))

        # Network block
        t.append("\n  ╔══ NETWORK STATUS ════╗\n", style=GRN_DIM)
        nc = GRN if self.net_stat == "ONLINE" else RED
        t.append(f"  {'CONNECT':<12}", style=TEXT_DIM)
        t.append(f"{self.net_stat}\n", style=f"bold {nc}")
        t.append(f"  {'DEVICES':<12}", style=TEXT_DIM)
        t.append(f"{self.devices} known\n", style=GRN)
        t.append(f"  {'ANOMALIES':<12}", style=TEXT_DIM)
        ac = AMBER if self.anomaly > 0 else GRN
        t.append(f"{self.anomaly} flagged\n", style=f"bold {ac}")

        return t


class GaugePanelWidget(Widget):
    """Probability gauge + Monte Carlo bars."""

    prob_value: reactive[float]      = reactive(0.84)
    mc_data:    reactive[list[float]] = reactive([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mc_data = [0.08, 0.18, 0.34, 0.55, 0.72, 0.84,
                         0.91, 0.87, 0.73, 0.55, 0.38, 0.22, 0.11, 0.06]

    def render(self) -> RenderableType:
        t = Text()
        t.append("  ╔══ PROBABILITY GAUGE ╗\n", style=GRN_DIM)
        t.append_text(render_ascii_gauge(self.prob_value, width=20))
        t.append("\n", style="")

        # Stats row
        p     = int(self.prob_value * 100)
        mean  = self.prob_value * 0.76
        ci_lo = max(0, self.prob_value - 0.18)
        ci_hi = min(1, self.prob_value + 0.18)
        col   = RED if p > 75 else (AMBER if p > 50 else GRN)

        t.append(f"  95th pct: ", style=TEXT_DIM)
        t.append(f"{self.prob_value:.3f}\n", style=col)
        t.append(f"  Mean:     ", style=TEXT_DIM)
        t.append(f"{mean:.3f}\n", style=GRN)
        t.append(f"  95% CI:   ", style=TEXT_DIM)
        t.append(f"[{ci_lo:.2f}, {ci_hi:.2f}]\n", style=GRN_DIM)
        t.append(f"  Iters:    ", style=TEXT_DIM)
        t.append("50,000\n", style=GRN_DIM)

        t.append("\n  ╔══ MC DISTRIBUTION ══╗\n", style=GRN_DIM)
        t.append_text(render_mc_bars(self.mc_data, width=20, height=4))
        return t


class EventLogWidget(Widget):
    """Scrollable event log panel."""

    DEFAULT_CSS = """
    EventLogWidget { overflow-y: auto; }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._events: list[tuple[str, str, str]] = [
            ("22:49:12", "SecurityProtocol → Gate 4",   "ok"),
            ("22:44:18", "WARNING: Unknown SID detected","crit"),
            ("22:43:55", "Packet → Tops",                "info"),
            ("22:43:42", "Core temp nominal",            "ok"),
            ("22:38:16", "Persona override: HOUSE",      "info"),
            ("22:35:48", "ChromaDB sync OK",             "ok"),
        ]

    def add_event(self, text: str, sev: str = "ok") -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self._events.insert(0, (ts, text, sev))
        self._events = self._events[:40]  # keep last 40
        self.refresh()

    def render(self) -> RenderableType:
        SEV_COLS = {"ok": GRN, "crit": RED, "warn": AMBER, "info": BLUE}
        SEV_ICONS = {"ok": "◉", "crit": "⚠", "warn": "◈", "info": "○"}

        t = Text()
        t.append("  ╔══ EVENT LOG ════════╗\n", style=GRN_DIM)
        for ts, txt, sev in self._events[:16]:
            col  = SEV_COLS.get(sev, GRN)
            icon = SEV_ICONS.get(sev, "○")
            t.append(f"  {ts} ", style=TEXT_DIM)
            t.append(f"{icon} ", style=col)
            t.append(f"{txt[:22]}\n", style=col if sev != "ok" else TEXT_DIM)
        return t


# ═══════════════════════════════════════════════════════════════════
#  MESSAGE WIDGET
# ═══════════════════════════════════════════════════════════════════

class MessageWidget(Static):
    """A single conversation message."""

    ROLE_STYLES = {
        "house":    (HOUSE_COL, "HOUSE",    "╠"),
        "yes_man":  (AMBER,     "YES.MAN",  "╠"),
        "operator": (TEXT_DIM,  "OPERATOR", "│"),
        "system":   (GRN_DIM,   "SYSTEM",   "│"),
    }

    def __init__(self, role: str, text: str, **kwargs) -> None:
        col, label, prefix = MessageWidget.ROLE_STYLES.get(
            role, (GRN_DIM, role.upper(), "│")
        )
        t = Text()
        t.append(f" {prefix} ", style=col)
        t.append(f"{label:<10}", style=f"bold {col}")
        t.append(" › ", style=GRN_DIM)
        t.append(text + "\n", style=GRN if role != "operator" else TEXT_DIM)
        super().__init__(t, **kwargs)


class TypingWidget(Static):
    """Animated 'calculating...' indicator."""

    def __init__(self, persona_key: str, **kwargs) -> None:
        self.persona_key  = persona_key
        self._frame_idx   = 0
        self._frames      = ["▌", "▐", "▌", "▐", "░", "▒", "▓"]
        super().__init__("", **kwargs)

    def on_mount(self) -> None:
        self.set_interval(0.12, self._tick)

    def _tick(self) -> None:
        self._frame_idx = (self._frame_idx + 1) % len(self._frames)
        p   = PERSONAS[self.persona_key]
        col = p["col"]
        t   = Text()
        t.append(f" ╠ ", style=col)
        t.append(f"{'CALCULATING':<10}", style=f"bold {col}")
        t.append(" › ", style=GRN_DIM)
        t.append(self._frames[self._frame_idx] * 6 + "  PROCESSING", style=GRN_DIM)
        self.update(t)


# ═══════════════════════════════════════════════════════════════════
#  MAIN APP
# ═══════════════════════════════════════════════════════════════════

class LuckyApp(App):
    """Lucky 38 Overseer — Fallout Terminal TUI."""

    TITLE   = "LUCKY 38 — OVERSEER_V3"
    CSS_PATH = None  # inline CSS below

    BINDINGS = [
        Binding("ctrl+p",    "switch_persona",  "Switch Persona", show=True),
        Binding("ctrl+s",    "status_check",    "Status",         show=True),
        Binding("ctrl+r",    "risk_assessment", "Risk Assess",    show=True),
        Binding("ctrl+c",    "quit",            "Quit",           show=True),
        Binding("escape",    "quit",            "Quit",           show=False),
    ]

    CSS = f"""
    Screen {{
        background: {BG};
        color: {GRN};
        layers: base overlay;
    }}

    /* ── HEADER ── */
    #header-bar {{
        dock: top;
        height: 3;
        background: {BG2};
        border-bottom: heavy {GRN_DIM};
        layout: horizontal;
        padding: 0 1;
    }}
    #logo {{
        width: 28;
        color: {GRN_HI};
        text-style: bold;
        content-align: left middle;
    }}
    #nav-bar {{
        width: 1fr;
        layout: horizontal;
        content-align: left middle;
    }}
    #header-right {{
        width: 30;
        layout: horizontal;
        content-align: right middle;
    }}
    #persona-pill {{
        width: 22;
        content-align: center middle;
        border: round {GRN_DIM};
        color: {HOUSE_COL};
    }}
    #sys-clock {{
        width: 10;
        content-align: right middle;
        color: {GRN_HI};
        text-style: bold;
    }}

    /* ── MAIN LAYOUT ── */
    #body {{
        layout: horizontal;
        height: 1fr;
    }}

    /* ── LEFT SIDEBAR ── */
    #sidebar-left {{
        width: 26;
        background: {BG2};
        border-right: heavy {GRN_DIM};
        padding: 0;
        layout: vertical;
    }}
    SensorsWidget {{
        height: 1fr;
        padding: 0;
    }}
    #llm-status {{
        height: 5;
        border-top: heavy {GRN_DIM};
        color: {GRN_DIM};
        padding: 0 1;
    }}

    /* ── CENTER PANEL ── */
    #center {{
        width: 1fr;
        layout: vertical;
        background: {BG};
    }}

    /* Portrait area */
    #portrait-area {{
        height: 16;
        layout: horizontal;
        border-bottom: heavy {GRN_DIM};
    }}
    PortraitWidget {{
        width: 1fr;
        padding: 0 1;
    }}
    #portrait-divider {{
        width: 3;
        content-align: center middle;
        color: {GRN_DIM};
    }}

    /* Conversation */
    #conv-scroll {{
        height: 1fr;
        overflow-y: auto;
        border-bottom: heavy {GRN_DIM};
        padding: 0;
    }}
    #conv-header {{
        height: 1;
        color: {GRN_DIM};
        padding: 0 1;
    }}
    MessageWidget {{
        height: auto;
    }}
    TypingWidget {{
        height: 1;
    }}

    /* Input */
    #input-row {{
        height: 3;
        layout: horizontal;
        background: {BG2};
        border-top: heavy {GRN_DIM};
        padding: 0 1;
    }}
    #input-prompt {{
        width: 14;
        content-align: left middle;
        color: {GRN_DIM};
    }}
    #cmd-input {{
        width: 1fr;
        background: {BG};
        color: {GRN_HI};
        border: none;
        padding: 0 1;
    }}
    #cmd-input:focus {{
        border: none;
        background: {BG};
    }}
    #transmit-hint {{
        width: 16;
        content-align: right middle;
        color: {GRN_DIM};
    }}

    /* ── RIGHT SIDEBAR ── */
    #sidebar-right {{
        width: 28;
        background: {BG2};
        border-left: heavy {GRN_DIM};
        layout: vertical;
    }}
    GaugePanelWidget {{
        height: 25;
        border-bottom: heavy {GRN_DIM};
    }}
    EventLogWidget {{
        height: 1fr;
        overflow-y: auto;
    }}

    /* ── FOOTER ── */
    #footer-bar {{
        dock: bottom;
        height: 2;
        background: {BG2};
        border-top: heavy {GRN_DIM};
        layout: horizontal;
        padding: 0 1;
    }}
    .footer-stat {{
        width: 1fr;
        content-align: center middle;
        color: {TEXT_DIM};
    }}
    .footer-stat-hi {{
        width: 1fr;
        content-align: center middle;
        color: {GRN};
        text-style: bold;
    }}
    """

    # ── Reactive state ───────────────────────────────────────────
    current_persona: reactive[str]   = reactive("house")
    clock_str:       reactive[str]   = reactive("--:--:--")
    query_count:     reactive[int]   = reactive(0)
    uptime_str:      reactive[str]   = reactive("00:00:00")
    _offline:        bool            = False

    def __init__(self, start_persona: str = "house", offline: bool = False):
        super().__init__()
        self.current_persona = start_persona
        self._offline        = offline
        self._start_time     = time.monotonic()

    # ── Layout ───────────────────────────────────────────────────
    def compose(self) -> ComposeResult:
        p = PERSONAS[self.current_persona]

        # Header
        with Container(id="header-bar"):
            yield Static(f"[bold]LUCKY 38[/] [dim]OVERSEER_V3[/]", id="logo")
            with Container(id="nav-bar"):
                yield Static(
                    f"[{GRN_DIM}][[/][{GRN}]SYSTEM[/][{GRN_DIM}]][/]  "
                    f"[{TEXT_DIM}]NETWORK[/]  [{TEXT_DIM}]FACILITY[/]  [{TEXT_DIM}]THREAT[/]"
                )
            with Container(id="header-right"):
                yield Static(
                    f"[{HOUSE_COL}]MR.HOUSE[/] [{GRN_DIM}]⇌[/] [{TEXT_DIM}]YES_MAN[/]",
                    id="persona-pill"
                )
                yield Static("", id="sys-clock")

        # Body
        with Container(id="body"):
            # Left sidebar
            with Container(id="sidebar-left"):
                yield SensorsWidget(id="sensors")
                yield Static(id="llm-status")

            # Center
            with Container(id="center"):
                # Portrait area
                with Container(id="portrait-area"):
                    yield PortraitWidget("house", id="portrait-house")
                    yield Static(
                        Text.from_markup(f"[{GRN_DIM}]║\n║\n║\n║\n║\n║\n║\n║\n║\n║\n║\n║[/]"),
                        id="portrait-divider"
                    )
                    yield PortraitWidget("yes_man", id="portrait-yes")

                # Conversation
                yield Static(
                    Text.from_markup(f"[{GRN_DIM}]  ╠══ OVERSEER TERMINAL {'═' * 32}╣[/]"),
                    id="conv-header"
                )
                with ScrollableContainer(id="conv-scroll"):
                    pass  # messages added dynamically

                # Input
                with Container(id="input-row"):
                    yield Static(f"[{GRN_DIM}]{p['short']} ›[/]", id="input-prompt")
                    yield Input(
                        placeholder="Enter command or query...",
                        id="cmd-input"
                    )
                    yield Static(f"[{GRN_DIM}]ENTER=send Ctrl+P=persona[/]",
                                  id="transmit-hint")

            # Right sidebar
            with Container(id="sidebar-right"):
                yield GaugePanelWidget(id="gauge")
                yield EventLogWidget(id="event-log")

        # Footer
        with Container(id="footer-bar"):
            yield Static("SESSION: ACTIVE",     classes="footer-stat-hi")
            yield Static("",                    id="footer-uptime",  classes="footer-stat")
            yield Static("",                    id="footer-queries", classes="footer-stat")
            yield Static("ITERS: 50K",          classes="footer-stat")
            yield Static("",                    id="footer-persona", classes="footer-stat-hi")
            yield Static("— THE HOUSE ALWAYS WINS —", classes="footer-stat")

    # ── Mount ────────────────────────────────────────────────────
    async def on_mount(self) -> None:
        # Apply initial persona state
        self._apply_persona_ui(self.current_persona)

        # Start clock
        self.set_interval(1.0, self._tick_clock)

        # Update LLM status
        self._update_llm_status()

        # Boot screen
        await self.push_screen(BootScreen())

        # Welcome message after boot
        self.call_after_refresh(self._post_boot)

    def _post_boot(self) -> None:
        self._add_message("system",
            "Lucky 38 Control System online. All subsystems nominal.")
        self._add_message("house" if self.current_persona == "house" else "yes_man",
            PERSONAS[self.current_persona]["tagline"].strip('"'))
        self.query_one("#cmd-input", Input).focus()

    # ── Clock & uptime ───────────────────────────────────────────
    def _tick_clock(self) -> None:
        now     = datetime.now()
        elapsed = int(time.monotonic() - self._start_time)
        hh = elapsed // 3600
        mm = (elapsed % 3600) // 60
        ss = elapsed % 60
        self.query_one("#sys-clock",     Static).update(now.strftime("%H:%M:%S"))
        self.query_one("#footer-uptime", Static).update(
            f"[{TEXT_DIM}]UPTIME:[/] [{GRN}]{hh:02d}:{mm:02d}:{ss:02d}[/]"
        )
        # Gently jitter sensors for realism
        if random.random() < 0.15:
            s = self.query_one("#sensors", SensorsWidget)
            s.cpu_val = max(20.0, min(95.0, s.cpu_val + random.uniform(-3, 3)))
            s.refresh()

    def _update_llm_status(self) -> None:
        mode = "OFFLINE — Local 12B" if self._offline else "ONLINE  — Groq 70B"
        col  = AMBER if self._offline else GRN
        t    = Text()
        t.append(f"\n  ╔══ LLM ENGINE ════════╗\n", style=GRN_DIM)
        t.append(f"  ◉ ", style=col)
        t.append(f"{mode}\n", style=col)
        t.append(f"\n  RAG:    ACTIVE\n", style=TEXT_DIM)
        t.append(f"  MEMORY: 0 / 40 ctx\n", style=TEXT_DIM)
        self.query_one("#llm-status", Static).update(t)

    # ── Persona ──────────────────────────────────────────────────
    def _apply_persona_ui(self, persona_key: str) -> None:
        p  = PERSONAS[persona_key]
        ph = self.query_one("#portrait-house",  PortraitWidget)
        py = self.query_one("#portrait-yes",    PortraitWidget)
        ph.is_active = (persona_key == "house")
        py.is_active = (persona_key == "yes_man")

        pill_col = HOUSE_COL if persona_key == "house" else AMBER
        pill_txt = (
            f"[{HOUSE_COL}]MR.HOUSE[/{HOUSE_COL}] [{GRN_DIM}]⇌[/{GRN_DIM}] [{TEXT_DIM}]YES_MAN[/{TEXT_DIM}]"
            if persona_key == "house" else
            f"[{TEXT_DIM}]MR.HOUSE[/{TEXT_DIM}] [{GRN_DIM}]⇌[/{GRN_DIM}] [{AMBER}]YES_MAN[/{AMBER}]"
        )
        self.query_one("#persona-pill",   Static).update(
            Text.from_markup(pill_txt)
        )
        self.query_one("#input-prompt",   Static).update(
            Text.from_markup(f"[{p['col']}]{p['short']} ›[/]")
        )
        self.query_one("#footer-persona", Static).update(
            Text.from_markup(f"[{p['col']}]PERSONA: {p['short']}[/]")
        )
        self.query_one("#footer-queries", Static).update(
            Text.from_markup(f"[{TEXT_DIM}]QUERIES:[/] [{GRN}]{self.query_count}[/]")
        )

    async def action_switch_persona(self) -> None:
        target = "yes_man" if self.current_persona == "house" else "house"
        await self.push_screen(PersonaTransitionScreen(target))
        # After transition screen pops, apply the new persona
        self.current_persona = target
        self._apply_persona_ui(target)
        self._add_message("system", f"Persona override: {PERSONAS[target]['short']}")
        self._add_message(target,
            "Overseer mode active. All systems under my purview. What do you require, Operator?"
            if target == "house" else
            "Oh hey! I'm active! Whatever you need — I'm absolutely on it!"
        )
        elog = self.query_one("#event-log", EventLogWidget)
        elog.add_event(f"Persona override: {PERSONAS[target]['short']}", "info")

    # ── Input handling ───────────────────────────────────────────
    @on(Input.Submitted, "#cmd-input")
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if not text:
            return
        event.input.value = ""
        self._add_message("operator", text)
        self.query_count += 1
        self.query_one("#footer-queries", Static).update(
            Text.from_markup(f"[{TEXT_DIM}]QUERIES:[/] [{GRN}]{self.query_count}[/]")
        )
        self._process_message(text)

    @work(exclusive=False)
    async def _process_message(self, text: str) -> None:
        # Show typing indicator
        typing = TypingWidget(self.current_persona, id="typing-widget")
        conv   = self.query_one("#conv-scroll", ScrollableContainer)
        await conv.mount(typing)
        conv.scroll_end(animate=False)

        if self._offline:
            # Mock response
            await asyncio.sleep(0.8 + random.random() * 0.6)
            prob = random.randint(55, 94)
            pool = PERSONAS[self.current_persona]["responses"]
            raw  = random.choice(pool)
            resp = raw.format(p=prob, n=random.randint(3, 12))
        else:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    r = await client.post(
                        f"{API_BASE}/api/chat",
                        json={"message": text}
                    )
                    r.raise_for_status()
                    resp = r.json().get("response", "Systems unresponsive.")
            except Exception as e:
                self._offline = True
                self._update_llm_status()
                # Fallback to mock
                await asyncio.sleep(0.6)
                prob = random.randint(55, 94)
                pool = PERSONAS[self.current_persona]["responses"]
                raw  = random.choice(pool)
                resp = raw.format(p=prob, n=random.randint(3, 12))
                self._add_event(f"API error — offline mode: {type(e).__name__}", "warn")

        # Remove typing, add response
        try:
            typing.remove()
        except Exception:
            pass

        self._add_message(self.current_persona, resp)

        # Update gauge with new probability if House
        if self.current_persona == "house":
            import re
            nums = re.findall(r"\b(\d{1,3})%", resp)
            if nums:
                p = int(nums[0]) / 100.0
                gauge = self.query_one("#gauge", GaugePanelWidget)
                gauge.prob_value = p
                gauge.refresh()

        elog = self.query_one("#event-log", EventLogWidget)
        elog.add_event(
            f"Query · {PERSONAS[self.current_persona]['short']} responded", "ok"
        )

    def _add_message(self, role: str, text: str) -> None:
        conv = self.query_one("#conv-scroll", ScrollableContainer)
        msg  = MessageWidget(role, text)
        conv.mount(msg)
        conv.scroll_end(animate=True)

    def _add_event(self, text: str, sev: str = "ok") -> None:
        self.query_one("#event-log", EventLogWidget).add_event(text, sev)

    # ── Keyboard actions ─────────────────────────────────────────
    async def action_status_check(self) -> None:
        self._add_message("operator", "Ctrl+S — Status check")
        await self._process_message("Give me a full facility status report.")

    async def action_risk_assessment(self) -> None:
        self._add_message("operator", "Ctrl+R — Risk assessment")
        await self._process_message(
            "Run a Monte Carlo risk assessment on current network threat vectors."
        )

    def action_quit(self) -> None:
        self._add_message("system", "Shutting down Lucky 38 Control System...")
        self.set_timer(0.8, self.exit)


# ═══════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Lucky 38 Overseer TUI — Phase 3b"
    )
    parser.add_argument(
        "--persona",
        choices=["house", "yes_man"],
        default="house",
        help="Starting persona (default: house)"
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Force offline mode — skip FastAPI, use mock responses"
    )
    args = parser.parse_args()

    app = LuckyApp(start_persona=args.persona, offline=args.offline)
    app.run()


if __name__ == "__main__":
    main()