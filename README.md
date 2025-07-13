# Cyberpunk 2077: Breach Protocol (ASCII Remake)
A fan-made, terminal-based remake of the **Breach Protocol** mini-game from *Cyberpunk 2077*, built entirely in ASCII art.

> ⚠️ This is a non-commercial fan project. Not affiliated with CD Projekt RED.
<br>

## Features
- Terminal-based ASCII interface, no GUI required
- Recreates the buffer-matching and sequence selection mechanic
- Randomized game boards for replayability
- Clean-ish Python code — depending on the level of autism easy to read and extend
<br>

## How to Play
- You’re given a **matrix of hex codes** and a list of target sequences.
- Select codes in alternating **row/column** pattern to fill your buffer.
- If your selected codes match one or more target sequences, you succeed.
- Strategy and order matter — you only have a limited number of buffer slots!
<br>

## Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/Cyberpunk-Netrunner-Mini-Game.git
cd Cyberpunk-Netrunner-Mini-Game
```
<br>

2. Install Python 3.13.3 (Windows x64 version recommended)  <br><br>
   > **Note:** ARM-based systems HAVE to have paython x64 version selected since windows-curses is not supported for ARM versions of python  
<br>

3. Install windows-curses:
```console
pip install windows-curses
```
<br>
 
4. Run the game:
```bash
python game.py
```
<br>

## Inspiration / Sources
- https://www.reddit.com/r/cyberpunkgame/comments/khioc0/a_comprehensive_guide_to_breach_protocol/
- https://www.polygon.com/cyberpunk-2077-guide-walkthrough/22163900/breach-protocol-encrypted-shard-militech-datashard-access-point-quickhack-buffer
- https://cyberpunk.fandom.com/wiki/Quickhacking#Access_Points
- https://chatgpt.com/
- https://www.youtube.com/watch?v=nKcOpYEUklg
