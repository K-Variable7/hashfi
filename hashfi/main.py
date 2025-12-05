import time
import sys
import select
import termios
import tty
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn
from rich.text import Text
from rich.table import Table

from hashfi.core.session import SessionManager
from hashfi.core.monitor import ThreatMonitor
from hashfi.sensors.system_sensor import SystemSensor
from hashfi.sensors.keyboard_sensor import KeyboardPanicSensor

console = Console()


def generate_layout() -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3),
    )
    layout["main"].split_row(Layout(name="status"), Layout(name="monitor"))
    return layout


def make_header():
    return Panel(
        Text("HASHFI SENTINEL v1.0", justify="center", style="bold cyan"), style="cyan"
    )


def make_status_panel(session_manager: SessionManager):
    if session_manager.is_active:
        hash_val = session_manager.get_hash()
        display_hash = f"{hash_val[:8]}...{hash_val[-8:]}" if hash_val else "N/A"
        status_text = Text("ACTIVE", style="bold green")
    else:
        display_hash = "CLEARED"
        status_text = Text("BURNED", style="bold red blink")

    table = Table.grid(padding=1)
    table.add_row("Status:", status_text)
    table.add_row("Session Hash:", Text(display_hash, style="yellow"))
    table.add_row("Panic Key:", Text("'p'", style="bold red"))

    return Panel(
        table,
        title="Session Status",
        border_style="green" if session_manager.is_active else "red",
    )


def make_monitor_panel(threat_level: float):
    # Create a progress bar for threat level
    bar = Progress(
        TextColumn("[bold]Threat Level[/bold]"),
        BarColumn(bar_width=None, complete_style="red", finished_style="red"),
        TextColumn("{task.percentage:>3.0f}%"),
    )
    task_id = bar.add_task("Threat", total=100, completed=threat_level * 100)

    return Panel(
        bar,
        title="Threat Monitor",
        border_style="red" if threat_level > 0.8 else "blue",
    )


def main():
    # Save terminal settings
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())

        session_manager = SessionManager()
        monitor = ThreatMonitor(threshold=0.9)
        monitor.add_sensor(SystemSensor())
        monitor.add_sensor(KeyboardPanicSensor())

        # Callback for auto-burn
        def on_breach():
            session_manager.burn_session()
            # We don't exit here, the loop will catch the state change

        monitor.on_threshold_breach = on_breach

        session_manager.start_session()

        layout = generate_layout()
        layout["header"].update(make_header())

        try:
            with Live(layout, refresh_per_second=4, screen=True) as live:
                while True:
                    # Update Logic
                    if session_manager.is_active:
                        threat = monitor.check_threats()
                    else:
                        threat = 1.0  # Max threat if burned

                    # Update UI
                    layout["main"]["status"].update(make_status_panel(session_manager))
                    layout["main"]["monitor"].update(make_monitor_panel(threat))

                    if not session_manager.is_active:
                        # Session is burned. Break loop to prompt user.
                        time.sleep(1)  # Show the burned state for a second
                        break

                    time.sleep(0.1)  # Faster poll for keyboard
        except KeyboardInterrupt:
            session_manager.burn_session()
            console.print("[bold red]Manually interrupted. Session burned.[/bold red]")
            return

        # Post-loop (Burned state)
        console.clear()
        console.print(
            Panel(
                Text(
                    "SESSION COMPROMISED - AUTO-BURN INITIATED",
                    justify="center",
                    style="bold red blink",
                ),
                style="red",
            )
        )
        console.print(
            f"[bold yellow]Last Hash:[/bold yellow] [strikethrough]{session_manager.get_hash() or 'CLEARED'}[/strikethrough]"
        )

        # Restore settings for input
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

        if (
            console.input(
                "\n[bold cyan]Generate new clean session? (y/n): [/bold cyan]"
            ).lower()
            == "y"
        ):
            main()  # Restart
        else:
            console.print("[bold]Exiting. Stay safe.[/bold]")

    finally:
        # Always restore terminal settings
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


if __name__ == "__main__":
    main()
