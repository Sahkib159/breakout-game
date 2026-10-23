# 🧱 Breakout

A classic Breakout game built with **Python** and **Pygame**, compiled to WebAssembly with **pygbag** so it runs right in the browser.

**▶️ Play it live:** [YOUR-VERCEL-LINK-HERE](https://YOUR-VERCEL-LINK-HERE)

![Gameplay screenshot](screenshot.png)

## Features

- Paddle, ball and rows of colored bricks
- Ball bounce angle depends on where it hits the paddle
- Score, 3 lives, game over and restart
- Multiple levels: more brick rows and a faster ball each level
- The ball speeds up as you break bricks
- Keyboard and mouse/touch controls

## Controls

| Action | Input |
| --- | --- |
| Move paddle | `←` `→` or `A` `D`, or move the mouse / drag on touch |
| Launch ball / restart | `Space` or click / tap |

## Tech stack

- Python 3
- [pygame-ce](https://pyga.me/)
- [pygbag](https://pygame-web.github.io/) (Python to WebAssembly)
- Deployed on [Vercel](https://vercel.com/)

## Run locally

```bash
# 1. Clone the repo
git clone https://github.com/Sahkib159/breakout-game.git
cd breakout-game

# 2. Create and activate a virtual environment
python -m venv venv
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install pygame-ce pygbag

# 4. Run the game on your desktop
python main.py
```

## Build for the web

```bash
pygbag --archive .
```

This creates the `build/web` folder with the files to deploy. To test the web version locally, run `pygbag .` and open http://localhost:8000.

## How the code is organized

| Class | Purpose |
| --- | --- |
| `Paddle` | Player paddle, keyboard and mouse movement |
| `Ball` | Movement, wall bounces, paddle bounce angle, speed-up |
| `Brick` | A single brick with its color and points |
| `Game` | Game state (ready, playing, game over), collisions, score, lives, levels |

## What I learned

- The game loop and frame timing
- Collision detection and velocity-based movement
- Structuring a game with object-oriented design
- Running Python in the browser with WebAssembly
- Deploying a static build on Vercel

## Roadmap

- [ ] Sound effects
- [ ] Power-ups (wide paddle, multi-ball)
- [ ] Saved high score
- [ ] Mobile-friendly layout
- [ ] Global leaderboard

## Author

**Sahkib** – [GitHub](https://github.com/Sahkib159)