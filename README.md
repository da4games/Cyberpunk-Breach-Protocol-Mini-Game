# Cyberpunk 2077: Breach Protocol (ASCII Remake)
A fan-made, terminal-based remake of the **Breach Protocol** mini-game from *Cyberpunk 2077*, built entirely in ASCII art.

> ⚠️ This is a non-commercial fan project. Not affiliated with CD Projekt RED.
<br>

## Notes
- This games is made for Terminals using the consolas font (default for windows 11)
- The game looks best when the terminal used has the background of #181818. This can be changed in colot_init in line 71 by seting it's value to a different one. The correct value can be calculated by converting normal rgb(0-255) to curses rgb(0-1000) (x/255*1000).

## Features
- Terminal-based ASCII interface, no GUI required
- Recreates the buffer-matching and sequence selection mechanic
- Randomized game boards for replayability
- Clean-ish Python code — depending on the level of autism easy to read and extend
  
  <img width="805" height="313" alt="grafik" src="https://github.com/user-attachments/assets/2acd72e5-622a-49ae-8e66-13abeb7fa527" />
<br>

## How to Play
- You’re given a **matrix of hex codes** and a list of target sequences.
- Select codes in alternating **row/column** pattern to fill your buffer.
- If your selected codes match one or more target sequences, you succeed.
- Strategy and order matter — you only have a limited number of buffer slots!
<br>

## Manual installation
> ⚠️ It is important that the bagkground of the chosen terminal is #181818 for better looks though it is not nessecary
> The color corresponds to the terminal bg of VsCode using the Dark Modern Theme

1. Clone the repository:
```bash
git clone https://github.com/da4games/Cyberpunk-Breach-Protocol-Mini-Game
cd Cyberpunk-Breach-Protocol-Mini-Game
```
<br>

2. Install Python 3.13.3 (Windows x64 version recommended)  <br><br>
   > **Note:** ARM-based systems should either use python x64 or install the pre-compiled wheel for curses  
<br>

3. Install curses:
   - For the best experience just download the code with the venv and select it s your python version.
     
   - For python 3.13.3 x64:
```console
pip install windows-curses
```
   - For ARM64 python:
      Download **python_curses-2.2.3-cp313-cp313-win_arm64.whl** from [Experimental Wheels for Python for Windows on ARM64 v2025.3.31](https://github.com/cgohlke/win_arm64-wheels/releases/tag/v2025.3.31) which is contained in the zip file.
     
     > WARNING: This method is experimental and may not work as expected
<br>
 
4. Run the game:
```bash
python game.py
```
<br>

## Manual .exe buid
1. Open a Terminal in the repository directory
<br>

2. Make sure you are either using the .venv or have pyinstaller and pillow installed on your python installation.
<br>

3. Run
   ```bash
   pyinstaller --onefile --noconfirm --strip --clean --console --hidden-import=windows-curses --icon=assets/icon.ico game.py
   ```
   in the Terminal
<br>

4. You can find the new .exe in /dist as it replaces the old one
<br>

## Execution without installation
- Just download the .exe and execute it on your device. I can not guarantee it will work on a non-windowsx64 device.
<br>

## Inspiration / Sources
- https://www.reddit.com/r/cyberpunkgame/comments/khioc0/a_comprehensive_guide_to_breach_protocol/
- https://www.polygon.com/cyberpunk-2077-guide-walkthrough/22163900/breach-protocol-encrypted-shard-militech-datashard-access-point-quickhack-buffer
- https://cyberpunk.fandom.com/wiki/Quickhacking#Access_Points
- https://chatgpt.com/
- https://www.youtube.com/watch?v=nKcOpYEUklg
