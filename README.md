# Cyberpunk 2077: Breach Protocol (ASCII Remake)
A fan-made, terminal-based remake of the **Breach Protocol** mini-game from *Cyberpunk 2077*, built entirely in ASCII art.

> ⚠️ This is a non-commercial fan project. Not affiliated with CD Projekt RED.


## Features
- Terminal-based ASCII interface, no GUI required
- Recreates the buffer-matching and sequence selection mechanic
- Randomized game boards for replayability
- Clean-ish Python code — depending on the level of autism easy to read and extend


## How to Play
- You’re given a **matrix of hex codes** and a list of target sequences.
- Select codes in alternating **row/column** pattern to fill your buffer.
- If your selected codes match one or more target sequences, you succeed.
- Strategy and order matter — you only have a limited number of buffer slots!


## Installation
Clone and run the game using the included Venv. This is especialy important on ARM-Based systems since curses isn't available for ARM-Based Python.


## Inspiration / Sources
- https://www.reddit.com/r/cyberpunkgame/comments/khioc0/a_comprehensive_guide_to_breach_protocol/
- https://www.polygon.com/cyberpunk-2077-guide-walkthrough/22163900/breach-protocol-encrypted-shard-militech-datashard-access-point-quickhack-buffer
- https://cyberpunk.fandom.com/wiki/Quickhacking#Access_Points
- https://chatgpt.com/
- https://www.youtube.com/watch?v=nKcOpYEUklg
