import time

import rich
rich.print("Hello, [bold magenta]World[/bold magenta]!", ":vampire:", locals())


from rich import print
from rich.padding import Padding
test = Padding("Hello", (2, 4))
print(test)

test = Padding("Hello", (2, 4), style="on blue", expand=False)
print(test)

time.sleep(3)

from rich.__main__ import make_test_card
from rich.console import Console

console = Console()
with console.pager():
    console.print(make_test_card())
    
    
from time import sleep
from rich.console import Console

console = Console()
with console.screen():
    console.print(locals())
    sleep(5)
    
    
from time import sleep

from rich.console import Console
from rich.align import Align
from rich.text import Text
from rich.panel import Panel

console = Console()

if 0:
    with console.screen(style="bold white on red") as screen:
        for count in range(5, 0, -1):
            text = Align.center(
                Text.from_markup(f"[blink]Don't Panic![/blink]\n{count}", justify="center"),
                vertical="middle",
            )
            screen.update(Panel(text))
            sleep(1)