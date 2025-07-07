import curses
import random

CHARACTERS = ("55", "BD", "1C", "E9", "FF")

def color_init(stdscr):
    # Initialize colors
    curses.start_color()
    curses.use_default_colors()
    
    # Define color pairs
    # Format: init_pair(pair_number, foreground, background)
    curses.init_pair(1, curses.COLOR_RED, -1)      # Red text
    curses.init_pair(2, curses.COLOR_GREEN, -1)    # Green text
    curses.init_pair(3, curses.COLOR_BLUE, -1)     # Blue text
    curses.init_pair(4, curses.COLOR_YELLOW, -1)   # Yellow text
    curses.init_pair(5, curses.COLOR_MAGENTA, -1)  # Magenta text
    curses.init_pair(6, curses.COLOR_CYAN, -1)     # Cyan text
    
    # Background color pairs (11-16)
    curses.init_pair(11, -1, curses.COLOR_RED)      # Red background
    curses.init_pair(12, -1, curses.COLOR_GREEN)    # Green background
    curses.init_pair(13, -1, curses.COLOR_BLUE)     # Blue background
    curses.init_pair(14, -1, curses.COLOR_YELLOW)   # Yellow background
    curses.init_pair(15, -1, curses.COLOR_MAGENTA)  # Magenta background
    curses.init_pair(16, -1, curses.COLOR_CYAN)     # Cyan background
    
    default_bg_id = 21  # Custom ID for the "transparent" background
    default_fg_id = 22  # Custom ID for the foreground
    very_exact_color_of_bg = 94#.117647058823529411764705882353
    very_exact_color_of_fg = 898#.03921568627450980392156862745
    curses.init_color(default_bg_id, very_exact_color_of_bg, very_exact_color_of_bg, very_exact_color_of_bg)
    curses.init_color(default_fg_id, very_exact_color_of_fg, very_exact_color_of_fg, very_exact_color_of_fg)
    curses.init_pair(default_bg_id, curses.COLOR_WHITE, default_bg_id)  # Transparent background
    
    
    #green, yellow and cyan have wrong fg
    curses.init_color(120, 0, 543, 0)  # Green RGB
    curses.init_pair(12, -1, 120) #fixed green
    #curses.init_pair(2, 120, default_bg_id) #green fg
    
    curses.init_color(140, 470, 470, 0)  # Yellow RGB
    curses.init_pair(14, -1, 140) #fixed yellow
    #curses.init_pair(4, 140, default_bg_id) #yellow fg
        
    curses.init_color(160, 0, 510, 510)  # Cyan RGB
    curses.init_pair(16, -1, 160) #fixed cyan
    #curses.init_pair(6, 160, default_bg_id) #cyan fg
    
    
    #still need brown
    curses.init_color(130, 400, 200, 0)  # Brown RGB
    curses.init_pair(17, curses.COLOR_WHITE, 130) #brown bg
    curses.init_pair(7, 130, default_bg_id) #brown fg
    
    # Define orange color (ID 20)
    orange_id = 20
    #max_r = 935
    #max_g = 543
    #max_b = 1000
    curses.init_color(orange_id, 725, 361, 0)  # Orange RGB
    
    # Create two pairs for orange - one for foreground, one for background
    curses.init_pair(orange_id, orange_id, default_bg_id)       # Orange foreground text
    curses.init_pair(orange_id + 10, curses.COLOR_WHITE, orange_id)  # Orange background
    
    # custom green from cyberpunk breach protocol, rgb(208, 236, 88)
    # converted to curses values (0-1000)
    curses.init_color(277, 816, 925, 345) 
    #curses.init_color(277, 549, 627, 235)
    curses.init_pair(255, 277, default_bg_id)  # Custom color for foreground text
    curses.init_pair(254, curses.COLOR_BLACK, 277) # Custom color for background text
    curses.init_pair(253, default_bg_id, 277) # custom color for background text with default background
    
    curses.init_color(276, 161, 176, 224) # custom gray for bg
    curses.init_pair(252, 277, 276) # gray bg with custom green
    curses.init_pair(251, default_bg_id, 276) # gray bg with default bg as fg
    curses.init_pair(250, 276, default_bg_id) # gray fg with efault bg
    
    curses.init_color(275, 545, 788, 788) # custom blue
    curses.init_pair(249, 275, 276)  # Custom blue for foreground text
    curses.init_pair(248, 275, default_bg_id)  # Custom blue for text with default background
    
    curses.init_color(274, 239, 255, 302) #custom lighter gray
    curses.init_pair(247, 274, 276)  # Custom lighter gray for fg and gray bg
    curses.init_pair(246, 274, default_bg_id)  # Custom lighter gray for fg and default bg
    
    curses.init_color(273, 122, 125, 102) # custom very dark low oppacity green
    curses.init_pair(245, 277, 273)  # Custom very dark low oppacity green for text with default background

code_matrix = [
    ["", "", "", "", ""],
    ["", "", "", "", ""],
    ["", "", "", "", ""],
    ["", "", "", "", ""],
    ["", "", "", "", ""]
]

datamines = [
    [],
    [],
    []]

completed_datamines = [False, False, False]

buffer = []

def update_gui(stdscr, active_axis: int, last_selected: list[int], hovering: list[int], clicked=False, first=False):
    stdscr.clear()
    debug_GUI = False
    hovering_over = ""
    if debug_GUI:
        #right GUI
        stdscr.addstr(0, 41,  "BUFFER", curses.color_pair(255))
        stdscr.addstr(1, 41,  "░░  ░░  ░░  ░░  ░░  ░░", curses.color_pair(255))
        stdscr.addstr(4, 41,  "SEUENCE REQUIRED TO UPLOAD", curses.color_pair(255))
        stdscr.addstr(6, 41,  "55  1C")
        stdscr.addstr(8, 41,  "1C  E9  BD")
        stdscr.addstr(10, 41, "BD  BD  55")

        #datamine levels
        stdscr.addstr(6, 73,  "DATAMINE_V1")
        stdscr.addstr(8, 73,  "DATAMINE_V2")
        stdscr.addstr(10, 73, "DATAMINE_V3")

        stdscr.addstr(8, 69,  " ∇∇", curses.color_pair(255))
        stdscr.addstr(6, 69,  "  ∇", curses.color_pair(255))
        stdscr.addstr(10, 69, "∇∇∇", curses.color_pair(255))

        #Main GUI
        stdscr.addstr(1, 1,  "BREACH TIME REMAINING", curses.color_pair(255))
        stdscr.addstr(2, 1,  "▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄", curses.color_pair(253))
        stdscr.addstr(4, 1,  "▄", curses.color_pair(255))
        stdscr.addstr(4, 2,   " CODE MATRIX                         ", curses.color_pair(254))
        stdscr.addstr(5, 1,  "                                      ", curses.color_pair(255))
        stdscr.addstr(6, 1,  "        BD   E9   1C   BD   BD        ", curses.color_pair(255))
        stdscr.addstr(7, 1,  "                                      ", curses.color_pair(255))
        stdscr.addstr(8, 1,  "        1C   1C   BD   BD   55        ", curses.color_pair(255))
        stdscr.addstr(9, 1,  "                                      ", curses.color_pair(255))
        stdscr.addstr(10, 1, "        BD   BD   55   BD   BD        ", curses.color_pair(255))
        stdscr.addstr(11, 1, "                                      ", curses.color_pair(255))
        stdscr.addstr(12, 1, "        1C   55   55   E9   BD        ", curses.color_pair(255))
        stdscr.addstr(13, 1, "                                      ", curses.color_pair(255))
        stdscr.addstr(14, 1, "        55   1C   BD   55   55        ", curses.color_pair(255))
    else:                
        #Main GUI
        stdscr.addstr(1, 1,  "BREACH TIME REMAINING", curses.color_pair(255))
        stdscr.addstr(2, 1,  "▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄", curses.color_pair(253))
        stdscr.addstr(4, 1,  "▄", curses.color_pair(255))
        stdscr.addstr(4, 2,   " CODE MATRIX                         ", curses.color_pair(254))
        
        #logic first
        gray = []
        gray_selected = []
        gray_gray = []
        green_bg = []
        
        #fills in gray
        if active_axis == 0: # vertical
            # Get the target column index once, before the loop
            x_coord = last_selected[0]
            # Iterate through each row
            for i in range(len(code_matrix)):
                # Directly access the element at the target column and append it
                for j in range(len(code_matrix[i])):
                    gray.append([j, x_coord])
                                
        if active_axis == 1: # horizontal
            # Get the target row index once, before the loop
            y_coord = last_selected[1]
            # Iterate through each row
            for i in range(len(code_matrix)):
                if y_coord == i:
                    # Add all characters in that row to gray
                    for j in range(len(code_matrix[i])):
                        gray.append([j, i])
                    # Since we found the row, we can stop looping
                    break
                
        #fills in gray_selected
        # Convert screen coordinates to matrix indices
        hover_matrix_y = (hovering[1] - 6) // 2
        hover_matrix_x = (hovering[0] - 9) // 5
        hovering_over = code_matrix[hover_matrix_y][hover_matrix_x]
        gray_selected = [hover_matrix_x, hover_matrix_y]
             
        #fills in gray_gray
        for i in range(len(code_matrix)):
            for j in range(len(code_matrix[i])):
                if code_matrix[i][j] == "[]":
                    gray_gray.append([j, i])
        
        #fills in green_bg
        if active_axis == 0: # vertical
            y_coord = last_selected[1]
            for i in range(len(code_matrix)):
                if i == y_coord:
                    for j in range(len(code_matrix[i])):
                        green_bg.append([j, i])
                    break
        
        if active_axis == 1: # horizontal
            x_coord = last_selected[0]
            for i in range(len(code_matrix)):
                for j in range(len(code_matrix[i])):
                    green_bg.append([j, x_coord])
        
        for i in range(len(code_matrix)):
            y = 6 + i * 2  # Calculate the y position for each row
            for j in range(len(code_matrix[i])):
                # Calculate the position for each character
                x = 9 + j * 5
                if first:
                    data = CHARACTERS[random.randint(0, 4)]
                    code_matrix[i][j] = data
                else:
                    data = code_matrix[i][j]
                    
                #stdscr.addstr(y, x, data, curses.color_pair(247)) #light gray fg with gray bg
                #stdscr.addstr(y, x, data, curses.color_pair(249)) #blue if hovering over
                #stdscr.addstr(y, x, data, curses.color_pair(252)) #noral if not
                #stdscr.addstr(y, x + 2, "   ", curses.color_pair(252)) #custom green fg with gray bg
                #stdscr.addstr(y, x, data, curses.color_pair(245)) #green bg with neon green fg
                
                if last_selected[active_axis] == i:# horizontal
                    if active_axis == 1:
                        if y == hovering[1] and (x == hovering[0] or x == hovering[0] - 1):
                            if clicked:
                                if len(buffer) < 6:
                                    buffer.append(data)
                                data = "[]"
                                code_matrix[i][j] = data
                                stdscr.addstr(y, x, data, curses.color_pair(247)) #light gray fg with gray bg
                            elif data == "[]":
                                stdscr.addstr(y, x, data, curses.color_pair(247)) #light gray fg with gray bg
                            else:
                                hovering_over = code_matrix[i][j]
                                stdscr.addstr(y, x, data, curses.color_pair(249)) #blue if hovering over
                        else:
                            if data == "[]":
                                stdscr.addstr(y, x, data, curses.color_pair(247)) #light gray fg with gray bg
                            else:
                                stdscr.addstr(y, x, data, curses.color_pair(252)) #noral if not

                        if not j == 4:
                            stdscr.addstr(y, x + 2, "   ", curses.color_pair(252)) #custom green fg with gray bg
                        elif j == 4: # little gray at end
                            stdscr.addstr(y, x + 2, "  ", curses.color_pair(252)) #custom green fg with gray bg
                        if j == 0: # little gray at start
                            stdscr.addstr(y, x - 2, "  ", curses.color_pair(252)) #custom green fg with gray bg

                    elif active_axis == 0:
                        if data == "[]":
                            stdscr.addstr(y, x, data, curses.color_pair(247))
                        else:
                            stdscr.addstr(y, x, data, curses.color_pair(245)) #green bg with neon green fg
                        
                        if not j == 4:
                            stdscr.addstr(y, x + 2, "   ", curses.color_pair(245))
                        elif j == 4: # little gray at end
                            stdscr.addstr(y, x + 2, "  ", curses.color_pair(245))
                        if j == 0: # little gray at start
                            stdscr.addstr(y, x - 2, "  ", curses.color_pair(245))
                    
                elif last_selected[active_axis] == j:# vertical
                    if active_axis == 0:
                        if y == hovering[1] and (x == hovering[0] or x == hovering[0] - 1):
                            if clicked:
                                if len(buffer) < 6:
                                    buffer.append(data)
                                data = "[]"
                                code_matrix[i][j] = data
                                stdscr.addstr(y, x, data, curses.color_pair(247))
                            elif data == "[]":
                                stdscr.addstr(y, x, data, curses.color_pair(247))
                            else:
                                hovering_over = code_matrix[i][j]
                                stdscr.addstr(y, x, data, curses.color_pair(249))
                        else:
                            if data == "[]":
                                stdscr.addstr(y, x, data, curses.color_pair(247))
                            else:
                                stdscr.addstr(y, x, data, curses.color_pair(252))
                                
                        stdscr.addstr(y, x - 1, " ", curses.color_pair(252))
                        stdscr.addstr(y, x + 2, " ", curses.color_pair(252))
                        stdscr.addstr(y + 1, x - 1, "    ", curses.color_pair(252))
                        if i == 0:
                            stdscr.addstr(y - 1, x - 1, "▄▄▄▄", curses.color_pair(250))
                        elif i == 4:
                            stdscr.addstr(y + 1, x - 1, "▄▄▄▄", curses.color_pair(251))
                    
                    else:
                        if data == "[]":
                            stdscr.addstr(y, x, data, curses.color_pair(246))
                        else:
                            stdscr.addstr(y, x, data, curses.color_pair(255))
                        
                elif active_axis == 1:
                        if data == "[]":
                            stdscr.addstr(y, x, data, curses.color_pair(247))
                        else:
                            stdscr.addstr(y, x, data, curses.color_pair(245))
                        
                        if not j == 4:
                            stdscr.addstr(y, x + 2, "   ", curses.color_pair(245))
                        elif j == 4: # little gray at end
                            stdscr.addstr(y, x + 2, "  ", curses.color_pair(245))
                        if j == 0: # little gray at start
                            stdscr.addstr(y, x - 2, "  ", curses.color_pair(245))
                
        #right GUI
        stdscr.addstr(0, 41,  "BUFFER", curses.color_pair(255))
        
        for i in range(len(buffer)):
            stdscr.addstr(2, 41+i*4, f"{buffer[i]}", curses.color_pair(255))
        
        for i in range(6 - len(buffer)):
            stdscr.addstr(2, 61-i*4, "░░", curses.color_pair(255))
        
        #stdscr.addstr(1, 41,  "░░  ░░  ░░  ░░  ░░  ░░", curses.color_pair(255))
        stdscr.addstr(4, 41,  "SEUENCE REQUIRED TO UPLOAD", curses.color_pair(255))
                
        #modular datamines
        line2_length = 0
        for i in range(3):
            y = 6 + i * 2  # Calculate the y position for each row
            
            if first:
                num_chars = 0
                if i == 0:  # Line 1: 2 or 3 chars
                    num_chars = random.choices([2, 3], weights=[70, 30], k=1)[0]
                elif i == 1:  # Line 2: 3 or 4 chars
                    num_chars = random.choices([3, 4], weights=[70, 30], k=1)[0]
                    line2_length = num_chars  # Save the length of line 2
                elif i == 2:  # Line 3: 3 or 4 chars, but not less than line 2
                    if line2_length >= 4:
                        num_chars = 4  # Must be 4 if line 2 was 4
                    else:  # If line 2 was 3, line 3 can be 3 or 4
                        num_chars = random.choices([3, 4], weights=[70, 30], k=1)[0]
            else:
                num_chars = len(datamines[i])  # Use the stored characters from datamines
            
            for j in range(num_chars):
                x = 41 + j * 4  # Calculate the x position for each character
                if first:
                    data = CHARACTERS[random.randint(0, 4)]
                    datamines[i].append(data)  # Store the character in the datamines list
                else:
                    data = datamines[i][j]
                if data == hovering_over and j == 0: # j == 0 is a paceholder for later more complicated logic
                    stdscr.addstr(y, x, data, curses.color_pair(248)) #blue if hovering over
                else:
                    stdscr.addstr(y, x, data)
                
        #datamine levels
        stdscr.addstr(6, 73,  "DATAMINE_V1")
        stdscr.addstr(8, 73,  "DATAMINE_V2")
        stdscr.addstr(10, 73, "DATAMINE_V3")

        stdscr.addstr(6, 69,  "  ∇", curses.color_pair(255))
        stdscr.addstr(8, 69,  " ∇∇", curses.color_pair(255))
        stdscr.addstr(10, 69, "∇∇∇", curses.color_pair(255))
        
        stdscr.addstr(17, 1, f"hovering_over = {hovering_over}", curses.color_pair(255))
        
    stdscr.refresh()
            
def main(stdscr):
    stdscr.clear()
    
    curses.curs_set(0) # Hides the cursor
    color_init(stdscr)
    
    # Get screen dimensions
    max_y, max_x = stdscr.getmaxyx()
    if max_y < 16 or max_x < 84:
        stdscr.addstr(0, 0, "Screen size too small. Minimum size is 14 rows and 84 columns.", curses.color_pair(1))
        stdscr.refresh()
        stdscr.getch()
    
    # Enable mouse tracking with all possible options
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    stdscr.nodelay(True)  # Make getch non-blocking
    
    stdscr.timeout(100)
    
    active_axis = 1 # 1 = horizontal, 0 = vertical
    last_selected = [0, 0] #x, y in matrix
    hovering = [0, 0]
    old_hovering = [0, 0]
    update_gui(stdscr, active_axis, last_selected, hovering, first=True)
    
    while len(buffer) < 6:
            key = stdscr.getch()
            _, x, y, _, button = curses.getmouse()
            
            clicked_in_matrix = False
            if key == curses.KEY_MOUSE:
                if button == curses.BUTTON1_PRESSED or button == curses.BUTTON1_CLICKED:
                    if x >= 9 and x <= 30 and y >= 6 and y <= 14:  # Check if click is within the code matrix area
                        clicked_in_matrix = True
                        
                        # Convert screen coordinates to matrix indices
                        matrix_y = (y - 6) // 2
                        matrix_x = (x - 9) // 5
                        
                        if active_axis == 1 and matrix_y == last_selected[1]:
                            last_selected = [matrix_x, matrix_y]
                            active_axis = 0
                        elif active_axis == 0 and matrix_x == last_selected[0]:
                            last_selected = [matrix_x, matrix_y]
                            active_axis = 1
                        else:
                            clicked_in_matrix = False # Not a valid move
                            
            hovering = [x, y]
            if not hovering == old_hovering or clicked_in_matrix:
                update_gui(stdscr, active_axis, last_selected, hovering, clicked=clicked_in_matrix)
                stdscr.addstr(16, 1, f"You are hovering at {hovering[0], hovering[1]}", curses.color_pair(255))
                stdscr.refresh()
            
            old_hovering = [x, y]

if __name__ == "__main__":
    curses.wrapper(main)