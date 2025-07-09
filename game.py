import curses
import random
import time

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
    curses.init_pair(250, 276, default_bg_id) # gray fg with default bg
    curses.init_pair(241, curses.COLOR_WHITE, 276) #white fg with gray bg
        
    curses.init_color(275, 545, 788, 788) # custom blue
    curses.init_pair(249, 275, 276)  # Custom blue for foreground text
    curses.init_pair(248, 275, default_bg_id)  # Custom blue for text with default background
    
    curses.init_color(274, 239, 255, 302) #custom lighter gray
    curses.init_pair(247, 274, 276)  # Custom lighter gray for fg and gray bg
    curses.init_pair(246, 274, default_bg_id)  # Custom lighter gray for fg and default bg
    
    curses.init_color(273, 122, 125, 102) # custom very dark low oppacity green
    curses.init_pair(245, 277, 273)  # Custom very dark low oppacity green for text with default background
    curses.init_pair(244, 273, default_bg_id)
    curses.init_pair(243, default_bg_id, 273)
    curses.init_pair(242, 273, 274)
    
    curses.init_color(272, 94, 94, 165) #custom medium gray
    curses.init_pair(240, curses.COLOR_WHITE, 272)  #white fg with medium gray bg
    curses.init_pair(239, 272, default_bg_id)  # medium gray fg with default bg
    curses.init_pair(238, default_bg_id, 272)
    curses.init_pair(237, 275, 272)  # Custom blue fg with medium gray bg
    
    curses.init_color(271, 992, 380, 318)# failed red
    curses.init_color(270, 192, 827, 498)# installed green
    curses.init_pair(236, curses.COLOR_BLACK, 271) # black text on failed red background
    curses.init_pair(235, curses.COLOR_BLACK, 270) # black text on installed green background
    curses.init_pair(234, default_bg_id, 271)
    curses.init_pair(233, default_bg_id, 270)

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

buffer = []
max_buffer_length = 6  # Maximum length of the buffer

dv_firsts = [False, False, False]  # Track if the datamines animation has been executed for each datamine

datamine_completed_before = [0, 0, 0]
completed_datamines = [False, False, False]
failed_datamines = [False, False, False]

def update_gui(stdscr, active_axis: int, last_selected: list[int], hovering: list[int], time_left=None, time_given=None, start_time=None, clicked=False, first=False):
    stdscr.clear()
    draw_time(stdscr, 0, 30)  # Placeholder for time drawing, will be updated later
    hovering_over = ""
    click_executed = False
    click_location = [0, 0]
    
    #Main GUI
    stdscr.addstr(1, 1,  "BREACH TIME REMAINING", curses.color_pair(255))
    stdscr.addstr(4, 1,  "▄", curses.color_pair(255))
    stdscr.addstr(4, 2,   " CODE MATRIX                         ", curses.color_pair(254))
        
    #logic first
    global datamine_completed_before
    gray = []
    gray_selected = []
    gray_gray = []
    green_bg = []
    datamine_hover_char = ""
        
    #fills in gray (the selectable axis)
    if active_axis == 0: # vertical
        x_coord = last_selected[0]
        for i in range(len(code_matrix)):
            gray.append([x_coord, i])
                                
    if active_axis == 1: # horizontal
        y_coord = last_selected[1]
        for j in range(len(code_matrix[y_coord])):
            gray.append([j, y_coord])
        
    #fills in gray_selected
    hover_matrix_x = -1
    hover_matrix_y = -1
    if hovering[0] >= 9 and hovering[0] <= 30 and hovering[1] >= 6 and hovering[1] <= 14:
        # Convert screen coordinates to matrix indices
        x_found = False
        y_found = False
        
        if hovering[1] % 2 == 0:
            y_found = True
            hover_matrix_y = (hovering[1] - 6) // 2               
        if (hovering[0] - 9) % 5 <= 1:
            x_found = True
            hover_matrix_x = (hovering[0] - 9) // 5
            
        if x_found and y_found and [hover_matrix_x, hover_matrix_y] in gray:
            # Prevent selecting already used cells
            if code_matrix[hover_matrix_y][hover_matrix_x] != "[]":
                hovering_over = code_matrix[hover_matrix_y][hover_matrix_x]
                gray_selected = [hover_matrix_x, hover_matrix_y]
        
    if clicked:
        if hovering_over in CHARACTERS:
            if len(buffer) < max_buffer_length:
                # No need to pop from gray, just mark as used
                datamine_completed_before = get_datamine_completion(buffer, datamines) # Store state before buffer change
                gray_gray.append(gray_selected)
                buffer.append(hovering_over)
                click_location = gray_selected.copy()
                code_matrix[gray_selected[1]][gray_selected[0]] = "[]"
                gray_selected = []
                click_executed = True
             
    #fills in gray_gray
    for i in range(len(code_matrix)):
        for j in range(len(code_matrix[i])):
            if code_matrix[i][j] == "[]":
                gray_gray.append([j, i])
        
    #fills in green_bg (potential next axis)
    if gray_selected:
        if active_axis == 0: # current is vertical, so potential next is horizontal
            y_coord = gray_selected[1]
            for j in range(len(code_matrix[y_coord])):
                green_bg.append([j, y_coord])
        
        if active_axis == 1: # current is horizontal, so potential next is vertical
            x_coord = gray_selected[0]
            for i in range(len(code_matrix)):
                green_bg.append([x_coord, i])
    
    #datamine completion refresh
    datamine_completed = get_datamine_completion(buffer, datamines)
    
    # Check for sequence completion for each datamine
    for i, datamine in enumerate(datamines):
        if datamine_completed[i] == len(datamine) and not failed_datamines[i] and not buffer == []:
            completed_datamines[i] = True
        
        # failed if the buffer is not long enough to complete the datamine
        # This means the buffer is too short to match the remaining characters in the datamine
        if max_buffer_length - len(buffer) < len(datamine) - datamine_completed[i] and not completed_datamines[i] and not buffer == []:
            failed_datamines[i] = True
        
    # Check for hover over datamines to highlight matrix
    if not first:
        max_completed = max(datamine_completed[0], datamine_completed[1], datamine_completed[2]) if any(datamine_completed) else 0
        for i_data, datamine in enumerate(datamines):
            y_datamine = 6 + i_data * 2
            if hovering[1] == y_datamine:
                x_offset = max_completed - datamine_completed[i_data]
                for j_data, char_data in enumerate(datamine):
                    x_datamine = 41 + (j_data + x_offset) * 4
                    if hovering[0] >= x_datamine and hovering[0] <= x_datamine + 1:
                        datamine_hover_char = char_data
                        break
            if datamine_hover_char:
                break
        
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

            # --- New Drawing Logic ---
            is_gray_selected = [j, i] == gray_selected
            is_gray = [j, i] in gray
            is_green_bg = [j, i] in green_bg
            is_gray_gray = [j, i] in gray_gray

            # Determine character color
            if is_gray_selected:
                stdscr.addstr(y, x, data, curses.color_pair(249))  # blue if hovering over
            elif datamine_hover_char and data == datamine_hover_char and is_gray and not is_gray_gray:
                stdscr.addstr(y, x, data, curses.color_pair(249))  # blue if hovering over datamine match
            elif is_gray_gray and is_gray:
                stdscr.addstr(y, x, data, curses.color_pair(247))  # used cell on active axis
            elif is_gray_gray and is_green_bg:
                stdscr.addstr(y, x, data, curses.color_pair(242))  # used cell on inactive axis
            elif is_gray and is_green_bg: # Intersection of active and potential axes
                stdscr.addstr(y, x, data, curses.color_pair(252)) # Draw as active axis
            elif is_gray:
                stdscr.addstr(y, x, data, curses.color_pair(252))  # active axis
            elif is_green_bg:
                stdscr.addstr(y, x, data, curses.color_pair(245))  # inactive axis
            elif is_gray_gray:
                stdscr.addstr(y, x, data, curses.color_pair(246))  # used cell, not on any axis
            else:
                stdscr.addstr(y, x, data, curses.color_pair(255))  # normal

            # Determine padding color and orientation based on priority
            padding_color = -1
            padding_axis = -1 # 0 for vertical, 1 for horizontal
            
            # Handle intersection first
            if is_gray and is_green_bg:
                # Draw green padding behind the gray padding
                green_padding_axis = 1 if active_axis == 0 else 0
                if green_padding_axis == 1: # Horizontal Green Padding
                    if j < 4: stdscr.addstr(y, x + 2, "   ", curses.color_pair(245))
                    else: stdscr.addstr(y, x + 2, "  ", curses.color_pair(245))
                    if j == 0: stdscr.addstr(y, x - 2, "  ", curses.color_pair(245))
                if green_padding_axis == 0: # Vertical Green Padding
                    if i < 4: stdscr.addstr(y + 1, x - 1, "    ", curses.color_pair(245))
                    else: stdscr.addstr(y + 1, x-1, "▄▄▄▄", curses.color_pair(243))
                    if i == 0: stdscr.addstr(y - 1, x-1, "▄▄▄▄", curses.color_pair(244))
                
                padding_color = 252 # Then set up for gray padding
                padding_axis = active_axis

            elif is_gray:
                padding_color = 252  # Active axis gray
                padding_axis = active_axis
            elif is_green_bg:
                padding_color = 245  # Inactive axis green
                padding_axis = 1 if active_axis == 0 else 0 # Flipped axis

            if padding_color != -1:
                if padding_axis == 1:  # Horizontal Padding
                    stdscr.addstr(y, x - 1, " ", curses.color_pair(padding_color))
                    if j < 4:
                        stdscr.addstr(y, x + 2, "   ", curses.color_pair(padding_color))
                    else:
                        stdscr.addstr(y, x + 2, "  ", curses.color_pair(padding_color))
                    if j == 0:
                        stdscr.addstr(y, x - 2, "  ", curses.color_pair(padding_color))
                
                if padding_axis == 0:  # Vertical Padding
                    stdscr.addstr(y, x - 1, " ", curses.color_pair(padding_color))
                    stdscr.addstr(y, x + 2, " ", curses.color_pair(padding_color))
                    if i < 4:
                        stdscr.addstr(y + 1, x - 1, "    ", curses.color_pair(padding_color))
                    else: # last character in col
                        stdscr.addstr(y + 1, x-1, "▄▄▄▄", curses.color_pair(251 if is_gray else 243))
                    if i == 0: # first character in col
                        stdscr.addstr(y - 1, x-1, "▄▄▄▄", curses.color_pair(250 if is_gray else 244))

    #right GUI
    stdscr.addstr(0, 41, "BUFFER", curses.color_pair(255))
        
    for i in range(len(buffer)):
        stdscr.addstr(2, 41+i*4, f"{buffer[i]}", curses.color_pair(255))
        
    for i in range(max_buffer_length - len(buffer)):
        if i == 5 - len(buffer) and hovering_over != "":
            stdscr.addstr(2, 61-i*4, hovering_over, curses.color_pair(248)) #blue if hovering over
        else:
            stdscr.addstr(2, 61-i*4, "░░", curses.color_pair(255))
        
    #stdscr.addstr(1, 41,  "░░  ░░  ░░  ░░  ░░  ░░", curses.color_pair(255))
    stdscr.addstr(4, 41,  "SEUENCE REQUIRED TO UPLOAD", curses.color_pair(255))
                
    #modular datamines
    # --- Animation logic for datamine movement ---
    if clicked and click_executed:
        max_before = max(datamine_completed_before) if any(datamine_completed_before) else 0
        max_after = max(datamine_completed) if any(datamine_completed) else 0
        
        # Calculate start and end offsets in character units (1 unit = 4 screen columns)
        start_offsets = [(max_before - dc_b) for dc_b in datamine_completed_before]
        end_offsets = [(max_after - dc_a) for dc_a in datamine_completed]
        
        # Determine max shift distance to set animation frames
        max_shift = 0
        for i in range(len(datamines)):
            shift = abs(end_offsets[i] - start_offsets[i])
            if shift > max_shift:
                max_shift = shift
        
        animation_frames = max_shift * 4 # 4 steps per character block
        
        if animation_frames > 0:
            for frame in range(animation_frames + 1):
                # Redraw static parts of the screen for clean animation
                # This is a simplified redraw, might need more elements if they are affected
                stdscr.addstr(0, 41, "BUFFER", curses.color_pair(255))
                for i_buf in range(len(buffer)): stdscr.addstr(2, 41+i_buf*4, f"{buffer[i_buf]}", curses.color_pair(255))
                for i_buf in range(max_buffer_length - len(buffer)): stdscr.addstr(2, 61-i_buf*4, "░░", curses.color_pair(255))
                stdscr.addstr(4, 41,  "SEUENCE REQUIRED TO UPLOAD", curses.color_pair(255))
                for i in range(len(datamines)):
                    y = 6 + i * 2
                    stdscr.addstr(y, 41, " " * 42) # Clear previous datamine line
                    stdscr.addstr(y, 73, f"DATAMINE_V{i+1}")
                    arrow = "∇" * (i + 1)
                    stdscr.addstr(y, 69, f"{arrow:>3}", curses.color_pair(255))


                for i in range(len(datamines)):
                    y = 6 + i * 2
                    # Interpolate offset for current frame
                    current_offset_pix = start_offsets[i] * 4 + (end_offsets[i] - start_offsets[i]) * 4 * (frame / animation_frames)
                    
                    if not completed_datamines[i] and not failed_datamines[i]:
                        for j, char_data in enumerate(datamines[i]):
                            x = 41 + round(j * 4 + current_offset_pix)
                            
                            is_next_char = (j == datamine_completed[i])
                            if is_next_char:
                                stdscr.addstr(y, x, char_data, curses.color_pair(240))
                            elif j < datamine_completed[i]:
                                stdscr.addstr(y, x, char_data, curses.color_pair(255))
                            else:
                                stdscr.addstr(y, x, char_data)
                
                if time_left is not None: draw_time(stdscr, time_left, time_given)
                stdscr.refresh()
                time.sleep(0.008)

    # Final drawing of datamines after animation or for non-click updates
    line2_length = 0
    for i in range(len(datamines)):
        y = 6 + i * 2  # Calculate the y position for each row
        
        if first:
            num_chars = 0
            if i == 0:  # Line 1: 2 or 3 chars
                num_chars = random.choices([2, 3], weights=[80, 20], k=1)[0]
            elif i == 1:  # Line 2: 3 or 4 chars
                num_chars = random.choices([3, 4], weights=[80, 20], k=1)[0]
                line2_length = num_chars  # Save the length of line 2
            elif i == 2:  # Line 3: 3 or 4 chars, but not less than line 2
                if line2_length >= 4:
                    num_chars = 4  # Must be 4 if line 2 was 4
                else:  # If line 2 was 3, line 3 can be 3 or 4
                    num_chars = random.choices([3, 4], weights=[70, 30], k=1)[0]
        else:
            num_chars = len(datamines[i])  # Use the stored characters from datamines
        
        #viasuals
        if not completed_datamines[i] and not failed_datamines[i]:
            max_completed = max(datamine_completed) if any(datamine_completed) else 0
            for j in range(num_chars):#j = x; i = y <-- positions in gridspaces
                x = 41 + (j + (max_completed - datamine_completed[i])) * 4  # Calculate the x position for each character
                if first:
                    data = CHARACTERS[random.randint(0, 4)]
                    datamines[i].append(data)  # Store the character in the datamines list
                else:
                    data = datamines[i][j]

                highlight = False
                is_datamine_hover = (data == datamine_hover_char and hovering[1] == y and hovering[0] >= x and hovering[0] <= x + 1)
                is_next_char = (j == datamine_completed[i])

                if is_next_char:
                    highlight = True
                    if data == hovering_over or is_datamine_hover:
                        stdscr.addstr(y, x, data, curses.color_pair(237)) # blue fg with gray bg
                    else:
                        stdscr.addstr(y, x, data, curses.color_pair(240)) # white fg with gray bg
                elif is_datamine_hover:
                    stdscr.addstr(y, x, data, curses.color_pair(248)) # blue fg with default bg
                elif j < datamine_completed[i]:
                    stdscr.addstr(y, x, data, curses.color_pair(255)) # green
                else:
                    stdscr.addstr(y, x, data)

                #highlighting depending on i aka y
                #much simpler then the matrix highlighting because it is always the same
                if highlight:
                    if i == 0:
                        stdscr.addstr(y, x + 2, " ", curses.color_pair(240))
                        stdscr.addstr(y, x - 1, " ", curses.color_pair(240))
                        stdscr.addstr(y - 1, x - 1, "▄▄▄▄", curses.color_pair(239))
                    elif i == 1:
                        stdscr.addstr(y - 1, x - 1, "    ", curses.color_pair(240))
                        stdscr.addstr(y + 1, x - 1, "    ", curses.color_pair(240))
                        stdscr.addstr(y, x + 2, " ", curses.color_pair(240))
                        stdscr.addstr(y, x - 1, " ", curses.color_pair(240))
                    elif i == 2:
                        stdscr.addstr(y, x + 2, " ", curses.color_pair(240))
                        stdscr.addstr(y, x - 1, " ", curses.color_pair(240))
                        stdscr.addstr(y + 1, x - 1, "▄▄▄▄", curses.color_pair(238))
        
        #datamine completion
        arrow = "∇"
        text = arrow * (i + 1)
        y_offset = 6 + i * 2  # Offset each datamine's label to its row
        string_INSTALLED = f"  INSTALLED                 {text:>3} DATAMINE_V{i+1}  "
        string_FAILED = f"  FAILED                    {text:>3} DATAMINE_V{i+1}  "
        if completed_datamines[i]:
            for j in range(len(string_INSTALLED)):
                stdscr.addstr(y_offset, j + 41, string_INSTALLED[j], curses.color_pair(235))
                if not dv_firsts[i]:
                    if time_left and time_given and start_time:
                        elapsed_time = time.time() - start_time
                        time_left = max(0, time_given - elapsed_time)
                        draw_time(stdscr, time_left, time_given)  # Update time display
                    stdscr.refresh()
                    time.sleep(0.005)  # Slow down the rendering for visual effect
            stdscr.addstr(y, 41 + 45, "▄", curses.color_pair(233))
            dv_firsts[i] = True  # Mark that the datamine animation has been executed
        elif failed_datamines[i]:
            for j in range(len(string_FAILED)):
                stdscr.addstr(y_offset, j + 41, string_FAILED[j], curses.color_pair(236))
                if not dv_firsts[i]:
                    if time_left and time_given and start_time:
                        elapsed_time = time.time() - start_time
                        time_left = max(0, time_given - elapsed_time)
                        draw_time(stdscr, time_left, time_given)  # Update time display
                    stdscr.refresh()
                    time.sleep(0.005)  # Slow down the rendering for visual effect
            stdscr.addstr(y, 41 + 45, "▄", curses.color_pair(234))
            dv_firsts[i] = True  # Mark that the datamine animation has been executed
        else:
            stdscr.addstr(y_offset, 73, f"DATAMINE_V{i+1}")
            stdscr.addstr(y_offset, 69, f"{text:>3}", curses.color_pair(255))
        
    stdscr.refresh()
    
    finished_by_completion = all(
    failed or completed for failed, completed in zip(failed_datamines, completed_datamines))
    
    return click_executed, click_location, finished_by_completion

def is_over_grid(pos):
    """Check if a coordinate is within the interactive grid areas."""
    x, y = pos
    # Check if over the 5x5 matrix grid
    # Each cell is 2 chars wide, with 3 chars padding (total 5).
    # We check if the cursor is on the 2 chars of data.
    is_over_matrix = (y >= 6 and y <= 14 and y % 2 == 0) and \
                     (x >= 9 and x <= 33 and (x - 9) % 5 < 2)
    
    # Check if over the 4x3 datamine grid
    # Each cell is 2 chars wide, with 2 chars padding (total 4).
    is_over_datamines = (y >= 6 and y <= 10 and y % 2 == 0) and \
                        (x >= 41 and x <= 56 and (x - 41) % 4 < 2)
    
    return is_over_matrix or is_over_datamines

def get_datamine_completion(current_buffer, current_datamines):
    completion = [0] * len(current_datamines)
    for i, datamine in enumerate(current_datamines):
        completed_count = 0
        for length in range(min(len(current_buffer), len(datamine)), 0, -1):
            buffer_suffix = current_buffer[-length:]
            datamine_prefix = datamine[:length]
            if buffer_suffix == datamine_prefix:
                completed_count = length
                break
        completion[i] = completed_count
    return completion

def draw_time(stdscr, time_left, time_given):
    seconds = int(time_left)
    milliseconds = int((time_left - seconds) * 100)
    time_left_str = f"{seconds:02}:{milliseconds:02}"
        
    stdscr.addstr(1, 34, f"{time_left_str:>5}", curses.color_pair(255))
        
    progress_bar_full_length = 38
    progress_chars_count = int(progress_bar_full_length * (time_left / time_given))
    progress_bar_str = '▄' * progress_chars_count
    stdscr.addstr(2, 1, f"{progress_bar_str:█<{progress_bar_full_length}}", curses.color_pair(253))
    
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
        
    active_axis = 1 # 1 = horizontal, 0 = vertical
    last_selected = [0, 0] #x, y in matrix
    hovering = [0, 0]
    old_hovering = [0, 0]
    update_gui(stdscr, active_axis, last_selected, hovering, first=True)
    
    start_time = None
    time_given = 30 #seconds
    finished_by_completion = False
    
    while len(buffer) < 6 and finished_by_completion == False:
        if start_time:
            elapsed_time = time.time() - start_time
            time_left = max(0, time_given - elapsed_time)
        else:
            time_left = time_given
            
        if start_time and time_left == 0:
            break
        
        draw_time(stdscr, time_left, time_given)
        
        key = stdscr.getch()
        try:
            _, x, y, _, button = curses.getmouse()
        except curses.error:
            # No mouse event, or invalid event
            x, y, button = -1, -1, 0
            
        if key == curses.KEY_MOUSE:
            if button & (curses.BUTTON1_PRESSED | curses.BUTTON1_CLICKED):
                check, location, finished_by_completion = update_gui(stdscr, active_axis, last_selected, hovering, time_left=time_left, time_given=time_given, start_time=start_time, clicked=True)
                if check:
                    if start_time is None:
                        start_time = time.time()
                    last_selected = location
                    active_axis = 1 if active_axis == 0 else 0
                    update_gui(stdscr, active_axis, last_selected, hovering)
            
        hovering = [x, y]

        if not hovering == old_hovering:
            # Refresh if the mouse enters or leaves a grid area.
            if is_over_grid(hovering) or is_over_grid(old_hovering):
                _, _, finished_by_completion = update_gui(stdscr, active_axis, last_selected, hovering, time_left=time_left, time_given=time_given, start_time=start_time)
                stdscr.addstr(16, 0, f"Hovering over: {hovering}      ", curses.color_pair(255))
        
        old_hovering = hovering

        #9,6; 30, 14 #matrix dimenstions
        #41, 6; 55, 10 #datamine dimensions
        
        #frame cap at 60 fps
        time.sleep(1/60)

if __name__ == "__main__":
    curses.wrapper(main)