import sys
import os
import random
from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Static, Header, Footer, Label, Input
from textual.containers import Container, Vertical
from textual import events
from rich.text import Text
from rich.style import Style
from rich.align import Align

GARDEN_WIDTH = 40
GARDEN_HEIGHT = 20

# --- Updated MAPS with new Tranquil Basin and other creative elements ---
MAPS = {
    "Empty Garden": [["." for _ in range(GARDEN_WIDTH)] for _ in range(GARDEN_HEIGHT)],
    "Stone Path": [[
        ":" if x == GARDEN_WIDTH // 2 else "." for x in range(GARDEN_WIDTH)
    ] for _ in range(GARDEN_HEIGHT)],
    "Bonsai Grove": [[
        "T" if (x, y) in [(8, 5), (22, 5), (15, 8), (10, 12)] else
        "o" if (x, y) in [(7,5), (23,5), (14,8), (11,12), (16,8), (9,12)] else
        "*" if (x, y) in [(9,5), (21,5), (13,8), (12,11)] else
        "." for x in range(GARDEN_WIDTH)
    ] for y in range(GARDEN_HEIGHT)],
    "Sacred Temple": [[
        "Θ" if (x, y) in [(GARDEN_WIDTH//2, 2), (GARDEN_WIDTH//2-5, GARDEN_HEIGHT-3),
                         (GARDEN_WIDTH//2+5, GARDEN_HEIGHT-3)] else
        ":" if (y == GARDEN_HEIGHT-4 and GARDEN_WIDTH//2-6 <= x <= GARDEN_WIDTH//2+6) or # Path leading to temples
               (x == GARDEN_WIDTH//2 and 3 <= y <= GARDEN_HEIGHT-4) else # Central path
        "o" if (x, y) in [(GARDEN_WIDTH//2-7, GARDEN_HEIGHT-3), (GARDEN_WIDTH//2+7, GARDEN_HEIGHT-3)] else
        "*" if (x == GARDEN_WIDTH//2-2 and y == GARDEN_HEIGHT-2) or (x == GARDEN_WIDTH//2+2 and y == GARDEN_HEIGHT-2) else
        "." for x in range(GARDEN_WIDTH)
    ] for y in range(GARDEN_HEIGHT)],
    "Pebble & Sakura Path": [[
        ("o" if (x % 5 == 0 and y % 3 == 0) else "*") if x == GARDEN_WIDTH // 2 -1 or x == GARDEN_WIDTH // 2 + 1 else ("." if x == GARDEN_WIDTH // 2 else ".")
        for x in range(GARDEN_WIDTH)
    ] for y in range(GARDEN_HEIGHT)],
    "Sakura Corner": [[
        "*" if (x < 5 and y < 5) or (x >= GARDEN_WIDTH - 5 and y >= GARDEN_HEIGHT - 5) else "."
        for x in range(GARDEN_WIDTH)
    ] for y in range(GARDEN_HEIGHT)],
    "Concentric Ripples": [[
        "~" if (abs(x - GARDEN_WIDTH // 2) + abs(y - GARDEN_HEIGHT // 2)) % 3 == 0 else "."
        for x in range(GARDEN_WIDTH)
    ] for y in range(GARDEN_HEIGHT)],
    "Zen Circle": [[
        "O" if ((x - GARDEN_WIDTH // 2)**2 + (y - GARDEN_HEIGHT // 2)**2)**0.5 < 5 and
                ((x - GARDEN_WIDTH // 2)**2 + (y - GARDEN_HEIGHT // 2)**2)**0.5 > 4 else "."
        for x in range(GARDEN_WIDTH)
    ] for y in range(GARDEN_HEIGHT)],
    "Tranquil Basin": [[ # New map 9: more like a fountain base
        "+" if (x,y) in [(7,5), (GARDEN_WIDTH-8,5), (7,GARDEN_HEIGHT-6), (GARDEN_WIDTH-8,GARDEN_HEIGHT-6)] else # Corners
        "-" if (7 < x < GARDEN_WIDTH-8) and (y == 5 or y == GARDEN_HEIGHT-6) else # Top/Bottom lines
        "|" if (x == 7 or x == GARDEN_WIDTH-8) and (5 < y < GARDEN_HEIGHT-6) else # Left/Right lines
        "W" if (8 <= x <= GARDEN_WIDTH-9 and 6 <= y <= GARDEN_HEIGHT-7) else # Water inside
        "I" if ((x == GARDEN_WIDTH//2-1) or (x == GARDEN_WIDTH//2)) and (y == 4 or y == GARDEN_HEIGHT-5) else # Reeds at center top/bottom
        "I" if ((y == GARDEN_HEIGHT//2-1) or (y == GARDEN_HEIGHT//2)) and (x == 6 or x == GARDEN_WIDTH-7) else # Reeds at center left/right
        "." for x in range(GARDEN_WIDTH)
    ] for y in range(GARDEN_HEIGHT)],
    "Zen Bridge": [[ # Map 10 (index 9): now with a vertical bridge over horizontal water
        # 1. Place the bridge ('H') vertically in the center, crossing the water - THIS TAKES PRIORITY
        "H" if (x == GARDEN_WIDTH // 2 and GARDEN_HEIGHT // 2 - 5 <= y <= GARDEN_HEIGHT // 2 + 5) else \
        # 2. Else, place water ('W') for the horizontal river
        ("W" if (GARDEN_HEIGHT // 2 - 1 <= y <= GARDEN_HEIGHT // 2 + 1) else \
         # 3. Else, place pebbles ('o') on the banks near the bridge
         ("o" if ((x == GARDEN_WIDTH // 2 - 2 and y == GARDEN_HEIGHT // 2 - 6) or \
                  (x == GARDEN_WIDTH // 2 + 2 and y == GARDEN_HEIGHT // 2 + 6)) else \
          # 4. Else, place sakura ('*') on the outer banks
          ("*" if ((x == GARDEN_WIDTH // 2 - 4 and y == GARDEN_HEIGHT // 2 - 8) or \
                   (x == GARDEN_WIDTH // 2 + 4 and y == GARDEN_HEIGHT // 2 + 8)) else \
           "."))) # 5. Default to sand ('.')
        for x in range(GARDEN_WIDTH)
    ] for y in range(GARDEN_HEIGHT)],
}
# --- End of Updated MAPS ---

# Define styles for legend consistency and new elements
STYLE_SAND = Style(color="rgb(180,170,160)", bgcolor="rgb(30,35,25)")
STYLE_STONE_PATH = Style(color="rgb(200,200,200)", bgcolor="rgb(40,45,35)")
STYLE_PLACED_STONE = Style(color="rgb(150,150,150)", bgcolor="rgb(50,55,45)") # For O, @, #
STYLE_PEBBLE = Style(color="rgb(120,120,120)", bgcolor="rgb(30,35,25)") # For 'o'
STYLE_SAKURA = Style(color="rgb(220,100,180)", bgcolor="rgb(30,35,25)") # For '*'
STYLE_RAKED_SAND = Style(color="rgb(180,180,150)", bgcolor="rgb(35,40,30)")
STYLE_BONSAI_TREE = Style(color="rgb(100,160,80)", bgcolor="rgb(30,35,25)")
STYLE_TEMPLE = Style(color="rgb(220,180,100)", bgcolor="rgb(30,35,25)")
STYLE_RAKE = Style(bold=True, color="rgb(180,160,80)", bgcolor="rgb(50,60,40)")
STYLE_WATER = Style(color="rgb(100,150,220)", bgcolor="rgb(20,25,35)") # New style for 'W'
STYLE_REED = Style(color="rgb(80,120,60)", bgcolor="rgb(30,35,25)") # New style for 'I'
STYLE_RAKED_WATER = Style(color="rgb(150,200,255)", bgcolor="rgb(25,30,40)") # New style for '≈' (raked water)
STYLE_BRIDGE = Style(color="rgb(160,100,60)", bgcolor="rgb(45,35,25)") # New style for 'H' (bridge)


class ZenGardenApp(App):
    CSS = """
    Screen {
        layout: vertical;
        background: rgb(20, 25, 15);
    }

    #narrative-intro {
        width: 100%;
        height: 1fr; /* Take up available vertical space */
        content-align: center middle; /* Center the text */
        background: rgb(10, 15, 5); /* Dark background for a calm feel */
        color: rgb(200, 200, 220); /* Light text color */
        text-style: italic;
        padding: 3;
        display: block; /* Initially visible, then hidden by _hide_narrative */
    }

    #garden-container {
        height: 1fr;
        width: 100%;
        border: round rgb(80, 70, 50);
        background: rgb(30, 35, 25);
        display: none; /* Initially hidden, will be shown after narrative */
    }

    #garden {
        width: auto;
        height: auto;
        padding: 1;
        text-align: center;
    }

    #help {
        width: 100%;
        padding: 1;
        background: rgb(40, 45, 35);
        border: round rgb(80, 70, 50);
        display: none; /* Initially hidden */
        overflow-y: auto; /* Enable scrolling if content is too long */
    }

    .title {
        text-style: bold;
        color: rgb(180, 160, 100);
        margin-top: 1; /* Add some space above titles */
    }
    
    .section-title {
        text-style: bold italic;
        color: rgb(160, 140, 80);
        margin-top: 1;
    }

    Footer {
        background: rgb(40, 45, 35);
        color: rgb(180, 160, 100);
    }
    """

    # Define key bindings as Textual actions
    BINDINGS = [
        ("ctrl+z", "undo", "Undo"),
        ("ctrl+y", "redo", "Redo"),
        ("ctrl+s", "save_garden", "Save"),
        ("ctrl+o", "load_garden", "Load"),
        ("ctrl+x", "reset_map", "Reset Map"), 
        ("n", "next_map", "Next Map"), 
        ("p", "prev_map", "Prev Map"),
        ("x", "random_map", "Random Map"), # <--- Add this line
    ]

    def __init__(self):
        super().__init__()
        self.garden_names = list(MAPS.keys())
        self.current_map_index = 0
        self.garden_name = self.garden_names[self.current_map_index]
        self.initial_grid_state = [row[:] for row in MAPS[self.garden_name]]
        self.grid = [row[:] for row in MAPS[self.garden_name]]
        self.cursor_x = GARDEN_WIDTH // 2
        self.cursor_y = GARDEN_HEIGHT // 2
        self.drag_rake_enabled = False
        self.show_help = False
        self.last_move_direction = "right"

        # History for Undo/Redo
        self.history = []
        self.history_index = -1
        self._push_history() # Push initial state

        self._garden_display = None
        self._help_display = None
        self._narrative_display = None # Initialize new narrative display widget
        self._is_displaying_temp_message = False # NEW: Flag to track temporary messages
        self._map_display = None  # For the new map overlay panel
        self.show_map = False  # Track map overlay state


    def _push_history(self) -> None:
        """Adds the current grid state to the history stack."""
        # Clear any 'future' history if we've undone actions
        self.history = self.history[:self.history_index + 1]
        self.history.append([row[:] for row in self.grid])
        self.history_index = len(self.history) - 1
        # Optional: Limit history size to prevent excessive memory usage
        if len(self.history) > 100: # Keep last 100 states
            self.history.pop(0)
            self.history_index -= 1

    # --- Action Methods for Ctrl+Key Bindings ---
    def action_undo(self) -> None:
        """Textual action to undo the last change."""
        self._undo()
        # The _undo method now handles the display update via _display_temp_message

    def action_redo(self) -> None:
        """Textual action to redo the last undone change."""
        self._redo()
        # The _redo method now handles the display update via _display_temp_message

    def action_save_garden(self) -> None:
        """Textual action to save the current garden."""
        self._save_garden()
        # _save_garden handles display update

    def action_load_garden(self) -> None:
        """Textual action to load a saved garden."""
        self._load_garden()
        # _load_garden handles display update

    def action_reset_map(self) -> None:
        """Textual action to reset the current map."""
        self._reset_current_map()
        # _reset_current_map handles display update
    
    def action_next_map(self) -> None:
        """Textual action to load the next garden template."""
        self.current_map_index = (self.current_map_index + 1) % len(self.garden_names)
        self._load_template_map()

    def action_prev_map(self) -> None:
        """Textual action to load the previous garden template."""
        self.current_map_index = (self.current_map_index - 1 + len(self.garden_names)) % len(self.garden_names)
        self._load_template_map()

    def action_random_map(self) -> None:
        """Textual action to load a random garden template."""
        prev_index = self.current_map_index
        if len(self.garden_names) > 1:
            choices = [i for i in range(len(self.garden_names)) if i != prev_index]
            self.current_map_index = random.choice(choices)
        self._load_template_map()

    # --- End Action Methods ---

    def _display_temp_message(self, message: str, duration: float = 2.0, guidance: str = None) -> None:
        if self._is_displaying_temp_message:
            return

        self._is_displaying_temp_message = True

        original_grid = [row[:] for row in self.grid]
        original_cursor_x = self.cursor_x
        original_cursor_y = self.cursor_y
        original_last_move_direction = self.last_move_direction

        if guidance is None:
            guidance = "\n\n[Press Enter to close this message]"
        message_with_hint = f"{message}{guidance}"

        temp_grid = [[" " for _ in range(GARDEN_WIDTH)] for _ in range(GARDEN_HEIGHT)]
        rich_message = Text(message_with_hint, justify="center", style="bold white on rgb(60,70,50)")
        self.grid = temp_grid
        self.cursor_x = -1
        self.cursor_y = -1

        self._temp_message_restore_args = (original_grid, original_cursor_x, original_cursor_y, original_last_move_direction)

        # Only set timer if duration is not None and > 0
        if duration and duration > 0:
            self._temp_message_timer = self.set_timer(duration, lambda: self._restore_garden(*self._temp_message_restore_args))
        else:
            self._temp_message_timer = None

        self._garden_display.update(Align(rich_message, align="center", vertical="middle", height=GARDEN_HEIGHT, width=GARDEN_WIDTH))

    def _restore_garden(self, grid_state, cursor_x, cursor_y, last_move_direction) -> None:
        """Restores the garden after a temporary message."""
        self.grid = grid_state
        self.cursor_x = cursor_x
        self.cursor_y = cursor_y
        self.last_move_direction = last_move_direction
        self._garden_display.update(self.render_grid())
        self.update_title() # Restore normal title
        self._is_displaying_temp_message = False # Clear the flag


    def _undo(self) -> None:
        """Undoes the last action by reverting to a previous grid state."""
        if self.history_index > 0:
            self.history_index -= 1
            self.grid = [row[:] for row in self.history[self.history_index]]
            self._display_temp_message("A breath taken, a stroke undone.")
        else:
            self._display_temp_message("The path ahead is clear; no steps to retrace.")

    def _redo(self) -> None:
        """Redoes an undone action by moving to a future grid state."""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.grid = [row[:] for row in self.history[self.history_index]]
            self._display_temp_message("A path rediscovered, inviting it back.")
        else:
            self._display_temp_message("All is as it should be, for now.")
    
    def _save_garden(self) -> None:
        """Saves the current garden state to a text file."""
        save_dir = Path("saved_gardens")
        save_dir.mkdir(exist_ok=True) # Ensure directory exists

        # Find the next available save file name
        i = 1
        while (save_dir / f"garden_save_{i}.txt").exists():
            i += 1
        
        filename = save_dir / f"garden_save_{i}.txt"
        try:
            with open(filename, "w") as f:
                for row in self.grid:
                    f.write("".join(row) + "\n")
            self._display_temp_message(f"Your tranquil creation is preserved:\n{filename.name}")
        except Exception as e:
            self._display_temp_message(f"Failed to preserve garden: {e}")


    def _load_garden(self) -> None:
        """Loads a garden state from a text file."""
        save_dir = Path("saved_gardens")
        if not save_dir.exists():
            self._display_temp_message("No echoes of past tranquility found.")
            return

        # List available save files and pick the latest one (or prompt user)
        save_files = sorted(save_dir.glob("garden_save_*.txt"), key=os.path.getmtime, reverse=True)
        if not save_files:
            self._display_temp_message("No echoes of past tranquility found.")
            return

        filename = save_files[0] # Load the most recent save
        
        try:
            new_grid = []
            with open(filename, "r") as f:
                for line in f:
                    row = list(line.strip())
                    if len(row) != GARDEN_WIDTH: # Basic validation
                        raise ValueError(f"Line width mismatch in {filename.name}")
                    new_grid.append(row)
            
            if len(new_grid) != GARDEN_HEIGHT: # Basic validation
                raise ValueError(f"Height mismatch in {filename.name}")
            
            self.grid = new_grid
            self._push_history() # Add loaded state to history
            self._display_temp_message(f"Returning to a cherished sanctuary:\n{filename.name}")
        except Exception as e:
            self._display_temp_message(f"An unexpected ripple: Error loading {filename.name}\n{e}")

    def _reset_current_map(self) -> None:
        """Resets the current map to its initial template state."""
        self.grid = [row[:] for row in MAPS[self.garden_names[self.current_map_index]]]
        self.initial_grid_state = [row[:] for row in MAPS[self.garden_names[self.current_map_index]]] # Update initial state for new map
        self._push_history() # Push reset state to history
        self._display_temp_message("The slate is wiped clean, a fresh canvas awaits.")

    def _load_template_map(self) -> None:
        """Loads a map from the MAPS dictionary based on current_map_index."""
        map_name = self.garden_names[self.current_map_index]
        self.grid = [row[:] for row in MAPS[map_name]]
        self.garden_name = map_name
        self.initial_grid_state = [row[:] for row in MAPS[self.garden_names[self.current_map_index]]]
        self._push_history()
        self._display_temp_message(f"Exploring a new vista: {self.garden_name}")

    def compose(self) -> ComposeResult:
        yield Header()
        self._narrative_display = Static("", id="narrative-intro")
        yield self._narrative_display

        with Container(id="garden-container"):
            self._garden_display = Static(self.render_grid(), id="garden")
            yield self._garden_display
        with Vertical(id="help"):
            yield Label("[b]Zen Garden Help Panel[/b]", classes="title")
            yield Label("Welcome, seeker of tranquility, to your personal Zen Garden. Here, amidst the quiet hum of your terminal, you hold the power to sculpt serenity, one thoughtful rake stroke at a time. Let your mind clear, and your inner landscape unfold.")

            yield Label("[b]Controls[/b]", classes="section-title")
            yield Label("←↑↓→   : Guide your rake with gentle precision, letting your path emerge across the sand and water.")
            yield Label("Space  : With intention, place a [b]Large Stone[/b] (O, @, #), anchoring your design.")
            yield Label("S      : Gently set down a [b]Small Pebble[/b] (o), adding subtle texture.")
            yield Label("F      : Bloom a delicate [b]Sakura[/b] (*), inviting fleeting beauty.")
            yield Label("R      : Begin the rhythmic dance of [b]Raking[/b] (~ on sand, ≈ on water), or smooth away the ripples.")
            yield Label("W      : Introduce [b]Still Water[/b] (W), a mirror for the sky.")
            yield Label("I      : Plant a graceful [b]Iris/Reed[/b] (I), bringing vertical harmony.")
            yield Label("C      : With a cleansing breath, [b]Clear[/b] the tile (.), returning it to its pristine state.")
            yield Label("D      : Activate [b]Drag Rake Mode[/b], allowing your movements to continuously create flowing patterns across the sand or gentle waves upon the water.")
            yield Label(f"0-{len(self.garden_names) - 1}: Explore diverse [b]Garden Templates[/b], each a new beginning for your contemplation.")
            yield Label("N / P  : Navigate to the [b]Next[/b] or [b]Previous[/b] garden template.")
            yield Label("H      : Toggle this [b]Help Panel[/b], finding guidance whenever stillness calls.")
            yield Label("X      : Wander to a [b]Random Garden[/b], letting chance guide your next vista.")
            yield Label("Q      : When your spirit is refreshed, [b]Quit[/b] this tranquil space.")
            yield Label("---")
            yield Label("[b]Advanced Controls[/b]", classes="section-title")
            yield Label("Ctrl+Z : Gently [b]Undo[/b] a previous stroke, returning to a moment past.")
            yield Label("Ctrl+Y : [b]Redo[/b] a path rediscovered, inviting it back.")
            yield Label("Ctrl+S : [b]Save[/b] your cultivated sanctuary to a file, preserving its peaceful essence.")
            yield Label("Ctrl+O : [b]Load[/b] a cherished garden, resuming a journey of peace.")
            yield Label("Ctrl+X : With quiet surrender, [b]Reset[/b] the current map to its pristine, original state.")

            yield Label("[b]Garden Elements Legend[/b]", classes="section-title")

            # Helper to create styled Text for legend entries
            def styled_legend_entry(symbol: str, description: str, style: Style) -> Label:
                text = Text()
                text.append(symbol, style=style)
                text.append(f" : {description}")
                return Label(text)

            yield styled_legend_entry(".", "Empty Sand / Base ground", STYLE_SAND)
            yield styled_legend_entry(":", "Stone Path", STYLE_STONE_PATH)
            yield styled_legend_entry("O", "Large Stone (randomized O, @, #)", STYLE_PLACED_STONE)
            yield styled_legend_entry("o", "Small Pebble", STYLE_PEBBLE)
            yield styled_legend_entry("*", "Sakura", STYLE_SAKURA)
            yield styled_legend_entry("~", "Raked Sand / Ripple", STYLE_RAKED_SAND)
            yield styled_legend_entry("≈", "Raked Water / Wave", STYLE_RAKED_WATER)
            yield styled_legend_entry("W", "Water (Pond/Stream)", STYLE_WATER)
            yield styled_legend_entry("I", "Iris / Reed", STYLE_REED)
            yield styled_legend_entry("H", "Bridge (wooden)", STYLE_BRIDGE) 
            yield styled_legend_entry("T", "Bonsai Tree", STYLE_BONSAI_TREE)
            yield styled_legend_entry("Θ", "Temple Structure", STYLE_TEMPLE)
            yield styled_legend_entry("+", "Basin Corner (Stone)", STYLE_STONE_PATH)
            yield styled_legend_entry("-", "Basin Edge Horizontal (Stone)", STYLE_STONE_PATH)
            yield styled_legend_entry("|", "Basin Edge Vertical (Stone)", STYLE_STONE_PATH)

            rake_example = Text()
            rake_example.append("|---", style=STYLE_RAKE)
            rake_example.append(" : Your rake")
            yield Label(rake_example)

            yield Label("\nEnjoy cultivating your Zen Garden!", classes="title")
        # --- Add a dedicated map overlay panel ---
        self._map_display = Static("", id="map-overlay")
        yield self._map_display

        yield Footer()

    def on_mount(self) -> None:
        self.update_title()
        self._show_ascii_intro()  # Show ASCII bonsai first
        self.show_map = False  # Track map overlay state

    def _show_ascii_intro(self) -> None:
        """Displays the ASCII bonsai tree art for a few seconds before the welcome text."""
        bonsai_art = Text(
            "	        .s.s.                      \n "
            "           ,`'`Y8bso.                    \n"
            "          ,bonsai y'd8l                  \n"
            "           `,8K art?*?b.                 \n"
            "           ,tree_888888o                 \n"
            "       ,r.calm--',' e8b?Y..              \n"
            "       j*Y888P*{ `._. '' 888b            \n"
            "         ``'``,.`'-- relaxP*             \n"
            "  	      db8sld-'., ,):code.              \n"
            "     <sd88P,-d888P'd88888888Rdbc         \n"
            "    `'*J*CJ8*d8888L:'  ``88?bl.o         \n"
            "    .o.sl.rsdP^*8bdbs.. *'?**l888s.      \n"
            "  ,`JYsd88P88ld?\**'`*`-. `  ` `'`       \n"
            "  dPJ88*J?P;Pd888D;=-.  -.l.s.           \n"
            ".'`'*Y,.sbsdkC l.'   (      )            \n"
            "     .Y8888P*'`       )     :            \n"
            "       `'`        _.-'.  ,  k.           \n"
            "                 (    :  '   ('          \n"
            "         _______ ,'`-  )`.` `.l ___      \n"
            "    r================================7   \n"
            "     `\     '-------ZEN------'     ,'    \n"
            "       `\ .. .. .. .. .. .. .. ../         ",
            justify="center",
            style=Style(color="rgb(200,200,220)", bgcolor="rgb(10,15,5)"),
        )
        self._narrative_display.update(bonsai_art)
        self._narrative_display.styles.display = "block" # Ensure it's visible

        # Hide the garden and footer temporarily
        self.query_one("#garden-container").styles.display = "none"
        self.query_one(Footer).styles.display = "none"
        self.query_one(Header).styles.display = "none" # Hide header too for full immersion

        # Schedule the narrative to fade out and garden to appear
        self.set_timer(5, self._hide_narrative) # Display for 5 seconds

    def _hide_narrative(self) -> None:
        """Hides the narrative and shows the main garden view."""
        self._narrative_display.styles.display = "none"
        self.query_one("#garden-container").styles.display = "block"
        self.query_one(Footer).styles.display = "block"
        self.query_one(Header).styles.display = "block" # Show header again
        self._garden_display.update(self.render_grid()) # Ensure garden is rendered
        self.update_title() # Re-render title after showing everything

    def render_grid(self) -> Text:
        text = Text()
        rake_style = Style(bold=True, color="rgb(180,160,80)", bgcolor="rgb(50,60,40)")

        for y in range(GARDEN_HEIGHT):
            for x in range(GARDEN_WIDTH):
                tile = self.grid[y][x]

                is_rake_drawn = False
                
                # Check for horizontal rakes
                if self.last_move_direction in ("right", "left"):
                    if self.cursor_y == y and self.cursor_x <= x < self.cursor_x + 4:
                        if (self.last_move_direction == "right" and x == self.cursor_x) or \
                           (self.last_move_direction == "left" and x == self.cursor_x + 3):
                            text.append("|", style=rake_style)
                        else:
                            text.append("-", style=rake_style)
                        is_rake_drawn = True

                # Check for vertical rakes
                elif self.last_move_direction in ("up", "down"):
                    if self.cursor_x == x:
                        if (self.last_move_direction == "down" and y == self.cursor_y) or \
                           (self.last_move_direction == "up" and y == self.cursor_y):
                            text.append("|", style=rake_style)
                            is_rake_drawn = True
                        elif (self.last_move_direction == "down" and y == self.cursor_y - 1) or \
                              (self.last_move_direction == "up" and y == self.cursor_y + 1):
                            text.append("-", style=rake_style)
                            is_rake_drawn = True
                
                if is_rake_drawn:
                    continue

                # Draw the garden tile if no rake is present
                style = STYLE_SAND # Default sand
                if tile == ":":
                    style = STYLE_STONE_PATH
                elif tile in ["O", "@", "#"]:
                    style = STYLE_PLACED_STONE
                elif tile == "o":
                    style = STYLE_PEBBLE
                elif tile == "*":
                    style = STYLE_SAKURA
                elif tile == "~":
                    style = STYLE_RAKED_SAND
                elif tile == "≈": 
                    style = STYLE_RAKED_WATER
                elif tile == "T":
                    style = STYLE_BONSAI_TREE
                elif tile == "Θ":
                    style = STYLE_TEMPLE
                elif tile == "W": 
                    style = STYLE_WATER
                elif tile == "I": 
                    style = STYLE_REED
                elif tile == "H": 
                    style = STYLE_BRIDGE
                elif tile in ["+", "-", "|"]: 
                    style = STYLE_STONE_PATH

                text.append(tile, style=style)
            text.append("\n")
        return text

    def drag_rake_enabled_str(self) -> str:
        return "ON" if self.drag_rake_enabled else "OFF"

    async def on_key(self, event: events.Key) -> None:
        # --- Narrative close ---
        if self._narrative_display.styles.display == "block":
            if event.key == "enter":
                self._hide_narrative()
            return

        # --- Help panel toggle ---
        if event.key.lower() in ("h", "f1"):
            self.show_help = not self.show_help
            self.query_one("#help").display = "block" if self.show_help else "none"
            return

        # --- Map overlay toggle ---
        if event.key.lower() == "m":
            self.show_map = not getattr(self, "show_map", False)
            if self.show_map:
                map_list = ""
                for idx, name in enumerate(self.garden_names):
                    map_num = f"{idx:02d}"
                    map_list += f"{map_num}: {name}\n"
                self._map_display.update(
                    Text(
                        f"Available Maps:\n{map_list.strip()}\n\nPress [M] again to close.",
                        justify="center",
                        style="rgb(200,200,220) on rgb(40,45,35)"  # Match help panel style
                    )
                )
                self._map_display.styles.display = "block"
            else:
                self._map_display.styles.display = "none"
                self._map_display.update("")
            return

        # --- Random map selection ---
        if event.key.lower() == "x":
            self.action_random_map()
            return

        # --- Ignore all other keys if help or map overlay is open ---
        if getattr(self, "show_map", False) or self.show_help:
            return

        key = event.key.lower()

        # Handle cursor movement and update direction
        moved = False
        if key == "up":
            self.cursor_y = max(0, self.cursor_y - 1)
            self.last_move_direction = "up"
            moved = True
        elif key == "down":
            self.cursor_y = min(GARDEN_HEIGHT - 1, self.cursor_y + 1)
            self.last_move_direction = "down"
            moved = True
        elif key == "left":
            self.cursor_x = max(0, self.cursor_x - 1)
            self.last_move_direction = "left"
            moved = True
        elif key == "right":
            self.cursor_x = min(GARDEN_WIDTH - 4, self.cursor_x + 1) # -4 to keep full rake visible
            self.last_move_direction = "right"
            moved = True
        
        # Determine the rake's "head" position for placing and clearing
        rake_head_x = self.cursor_x
        rake_head_y = self.cursor_y

        if self.last_move_direction == "left":
            rake_head_x = self.cursor_x + 3 # '|' is at the end for left movement

        # Handle tool actions based on the determined rake head position
        action_performed = False

        # Helper to check if a tile is "protected" (cannot be cleared or overwritten by common tools)
        def is_protected(char: str) -> bool:
            return char in ["T", "Θ", "H", "+", "-", "|", ":"] # Trees, Temples, Bridge, Basin borders, Stone Path

        if key == "r": # Rake/Unrake sand or water (contextual)
            if 0 <= rake_head_x < GARDEN_WIDTH and 0 <= rake_head_y < GARDEN_HEIGHT:
                current_tile = self.grid[rake_head_y][rake_head_x]
                if is_protected(current_tile) or current_tile in ["O", "@", "#", "o", "*", "I"]:
                    # Cannot rake over solid objects or plants
                    self._display_temp_message("Cannot rake here.", 1.0)
                elif current_tile == ".": # Rake sand
                    self.grid[rake_head_y][rake_head_x] = "~"
                    action_performed = True
                elif current_tile == "~": # Unrake sand
                    self.grid[rake_head_y][rake_head_x] = "."
                    action_performed = True
                elif current_tile == "W": # Rake water
                    self.grid[rake_head_y][rake_head_x] = "≈"
                    action_performed = True
                elif current_tile == "≈": # Unrake water
                    self.grid[rake_head_y][rake_head_x] = "W"
                    action_performed = True
        elif key == "space": # Place large stone
            if 0 <= rake_head_x < GARDEN_WIDTH and 0 <= rake_head_y < GARDEN_HEIGHT:
                if not is_protected(self.grid[rake_head_y][rake_head_x]) and \
                   self.grid[rake_head_y][rake_head_x] not in ["W", "≈", "I", "o", "*"]: # Can't place on water/plants/small pebbles
                    new_stone = random.choice(["O", "@", "#"])
                    if self.grid[rake_head_y][rake_head_x] != new_stone:
                        self.grid[rake_head_y][rake_head_x] = new_stone
                        action_performed = True
                else:
                    self._display_temp_message("Cannot place a large stone here.", 1.0)
        elif key == "s": # Place small pebble
            if 0 <= rake_head_x < GARDEN_WIDTH and 0 <= rake_head_y < GARDEN_HEIGHT:
                if not is_protected(self.grid[rake_head_y][rake_head_x]) and \
                   self.grid[rake_head_y][rake_head_x] not in ["W", "≈", "I", "O", "@", "#", "*"]: # Can't place on water/plants/large stones/sakura
                    if self.grid[rake_head_y][rake_head_x] != "o":
                        self.grid[rake_head_y][rake_head_x] = "o"
                        action_performed = True
                else:
                    self._display_temp_message("Cannot place a small pebble here.", 1.0)
        elif key == "f": # Place sakura
            if 0 <= rake_head_x < GARDEN_WIDTH and 0 <= rake_head_y < GARDEN_HEIGHT:
                if not is_protected(self.grid[rake_head_y][rake_head_x]) and \
                   self.grid[rake_head_y][rake_head_x] not in ["W", "≈", "I", "O", "@", "#", "o"]: # Can't place on water/plants/stones/pebbles
                    if self.grid[rake_head_y][rake_head_x] != "*":
                        self.grid[rake_head_y][rake_head_x] = "*"
                        action_performed = True
                else:
                    self._display_temp_message("Cannot place a sakura here.", 1.0)
        elif key == "w": # Place still water
            if 0 <= rake_head_x < GARDEN_WIDTH and 0 <= rake_head_y < GARDEN_HEIGHT:
                if not is_protected(self.grid[rake_head_y][rake_head_x]) and \
                   self.grid[rake_head_y][rake_head_x] not in ["O", "@", "#", "o", "*", "I"]: # Can't place water under solid objects/plants
                    if self.grid[rake_head_y][rake_head_x] != "W":
                        self.grid[rake_head_y][rake_head_x] = "W"
                        action_performed = True
                else:
                    self._display_temp_message("Cannot place water here.", 1.0)
        elif key == "i": # Place reeds
            if 0 <= rake_head_x < GARDEN_WIDTH and 0 <= rake_head_y < GARDEN_HEIGHT:
                # Reeds can only be placed on water (W or ≈) or empty sand (.), not on solid objects
                current_tile = self.grid[rake_head_y][rake_head_x]
                if current_tile in ["W", "≈", "."]:
                    if current_tile != "I":
                        self.grid[rake_head_y][rake_head_x] = "I"
                        action_performed = True
                else:
                    self._display_temp_message("Reeds thrive near water or soft sand.", 1.5)
        elif key == "c": # Clear tile
            if 0 <= rake_head_x < GARDEN_WIDTH and 0 <= rake_head_y < GARDEN_HEIGHT:
                current_tile = self.grid[rake_head_y][rake_head_x]
                # Clearing a tile protected by the map (like a temple, bridge, path)
                # should revert it to its initial state, not just '.'
                if is_protected(current_tile):
                    # Find original tile for this position
                    original_tile = self.initial_grid_state[rake_head_y][rake_head_x]
                    if current_tile != original_tile: # Only if it's been changed from original
                        self.grid[rake_head_y][rake_head_x] = original_tile
                        action_performed = True
                    else:
                        self._display_temp_message("Cannot clear this foundational element.", 1.5)
                elif current_tile == "W" or current_tile == "≈": # Clearing water reverts to still water
                    if current_tile != "W": # Only if it's raked water
                        self.grid[rake_head_y][rake_head_x] = "W"
                        action_performed = True
                elif current_tile != ".": # Clear anything else to empty sand
                    self.grid[rake_head_y][rake_head_x] = "."
                    action_performed = True
        elif key == "d":
            self.drag_rake_enabled = not self.drag_rake_enabled
            self.update_title() # Update title to reflect rake mode change

        # Apply drag rake if enabled after movement (contextual for sand or water)
        if self.drag_rake_enabled and moved:
            if 0 <= rake_head_x < GARDEN_WIDTH and 0 <= rake_head_y < GARDEN_HEIGHT:
                current_tile_at_head = self.grid[rake_head_y][rake_head_x]
                if current_tile_at_head == ".":
                    if self.grid[rake_head_y][rake_head_x] != "~":
                        self.grid[rake_head_y][rake_head_x] = "~"
                        action_performed = True
                elif current_tile_at_head == "W":
                    if self.grid[rake_head_y][rake_head_x] != "≈":
                        self.grid[rake_head_y][rake_head_x] = "≈"
                        action_performed = True
        
        # Template selection (now 0-indexed)
        if key.isdigit() and 0 <= int(key) < len(self.garden_names):
            self.current_map_index = int(key)
            self._load_template_map()

        # Quit
        elif key == "q":
            self.exit()
        
        # Push history only if an action that changed the grid was performed
        if action_performed:
            self._push_history()
            self.update_title() # Update title for regular status

        # Always update grid display on key press (unless a temp message is showing)
        # Use the new flag _is_displaying_temp_message
        if not self._is_displaying_temp_message:
            self._garden_display.update(self.render_grid())

    def update_title(self, message: str = None):
        """Updates the application title, optionally with a temporary message."""
        mode_str = self.drag_rake_enabled_str()
        if message:
            self.title = message
        else:
            self.title = f"Zen Garden • {self.garden_name} • Rake Mode: {mode_str} • [H]elp [N]ext [P]rev"


if __name__ == "__main__":
    if sys.platform == "win32":
        os.environ["TERM"] = "xterm-256color" 

    app = ZenGardenApp()
    app.run()
