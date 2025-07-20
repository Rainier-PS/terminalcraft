<p align="center">
  <img src="image/Banner.png" alt="Banner">
</p>


# Terminal Zen Garden

Welcome to Terminal Zen Garden — a peaceful, interactive Zen garden for your terminal.  
No coding experience required. Just run, relax, and create.

![Welcome](image/Devlog%20July%2019%202025_2.png)

---

## What is this?

Terminal Zen Garden is a Python-based interactive Zen garden you can design and explore entirely in your terminal.  
Move your rake, place stones, and load different garden templates — all using ASCII art.

![Zen Garden](image/Pebble%20%26%20Sakura%20Path.png)

---

## Why I Make This Project

I created Terminal Zen Garden to introduce more people to the calming practice of Zen gardening. This terminal app offers a similar experience to a physical Zen garden, but without the need for any tools or materials — just your device and a keyboard.

---

## How to Run (Beginner Friendly)

Anyone can use this — follow the steps carefully!

---

### Step 1: Install Python 3.8 or Higher

1. Download Python from the official site:  
   https://www.python.org/downloads/

2. During installation, **make sure to check the box**:
   ```
   ✅ Add Python to PATH
   ```

3. After installation, open a terminal and verify:

```bash
python --version
pip --version
```

---

### Step 2: Download the Project

#### Option A — ZIP Download (Easy for Beginners)

1. Go to the GitHub repository:  
   https://github.com/Rainier-PS/Terminal-Zen-Garden

2. Click the green **[Code]** button → select **Download ZIP**

3. Extract the ZIP file

4. Open the extracted folder, then **go into** the `garden` subfolder  
   (you should see a file named `main.py` inside)

---

### Step 3: Open Terminal in the Garden Folder

#### On Windows:

1. Inside the `garden` folder, **click the address bar**  
2. Type `cmd` and press Enter — it opens Command Prompt in that folder.

#### On macOS or Linux:

Open your terminal and navigate manually, for example:

```bash
cd ~/Downloads/Terminal-Zen-Garden-main/garden
```

(Change the path if you saved it elsewhere.)

---

### Step 4: (Optional) Set Up Virtual Environment

Recommended to keep things clean.

```bash
python -m venv venv
```

Activate it:

- **On Windows**:
  ```bash
  venv\Scripts\activate
  ```

- **On macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```

---

### Step 5: Install Required Packages

You only need one:

```bash
pip install textual
```

(If you get errors, make sure you're online and Python is installed properly.)

---

### Step 6: Run the Program

Finally, launch the Zen Garden:

```bash
python main.py
```

You’ll see a fullscreen terminal interface — you're now inside the garden!

---

## Controls

| Key                | Action                                               |
|--------------------|------------------------------------------------------|
| ← ↑ ↓ →            | Move your rake                                       |
| Space              | Place a Large Stone (O, @, #)                        |
| S                  | Place a Small Pebble (o)                             |
| F                  | Place a Sakura Blossom (*)                           |
| R                  | Rake sand (~) or water (≈), or smooth it back        |
| W                  | Add Still Water (W)                                  |
| I                  | Plant a Reed/Iris (I)                                |
| C                  | Clear a tile (return it to sand)                     |
| D                  | Toggle Drag Rake Mode                                |
| 0-9                | Switch garden templates                              |
| N / P              | Next / Previous garden template                      |
| X                  | Random garden template                               |
| H                  | Show/hide help panel                                 |
| M                  | Show/hide map list overlay                           |
| Q                  | Quit                                                 |
| Ctrl+Z / Ctrl+Y    | Undo / Redo                                          |
| Ctrl+S / Ctrl+O    | Save / Load your garden                              |
| Ctrl+X             | Reset current garden template                        |

---

## Features

- Multiple themed templates: sand, stone paths, bonsai, temples, bridges, and more
- Interactive ASCII garden with keyboard controls
- Save/load and undo/redo support
- Visual help panel
- Peaceful fullscreen terminal experience
- Beginner-friendly code for remixing

---

## Why Try It?

Zen gardens blend calm, focus, and creativity.  
Terminal Zen Garden brings that same joy into your digital workspace — a quiet space to reset, reflect, and express.

---

## Remix & Share

- Fork the repo and add your own tile types or maps
- Share screenshots of your garden designs
- Pull requests and contributions welcome!

---

Created by **Rainier-PS**
