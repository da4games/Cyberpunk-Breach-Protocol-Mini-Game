import curses
import random
import time

class game():
    def __init__(self):
        self.CHARACTERS = ("55", "BD", "1C", "E9", "FF", "7A")
        
        self.active_axis = 1  # 1 = horizontal, 0 = vertical
        self.last_selected = [0, 0]  # x, y coordinates in matrix
        self.hovering = [0, 0]
        self.old_hovering = [0, 0]
        
        self.start_time = None
        self.time_given = 30
        self.time_left = self.time_given
        self.finished_by_completion = False
        
        self.code_matrix = [
        ["", "", "", "", ""],
        ["", "", "", "", ""],
        ["", "", "", "", ""],
        ["", "", "", "", ""],
        ["", "", "", "", ""]
        ]

        self.datamines = [
            [],
            [],
            []]

        self.buffer = []
        self.max_buffer_length = 6

        self.dv_firsts = [False, False, False]  # Track datamine animation state
        self.datamine_completed_before = [0, 0, 0]
        self.completed_datamines = [False, False, False]
        self.failed_datamines = [False, False, False]
        self.datamine_current_offsets = [0, 0, 0]  # On-screen position offsets
        
        # Timer update control
        self.last_timer_update = 0
        self.timer_update_interval = 0.01  # Update every 10ms
        self.animating = False  # Flag to prevent timer refreshes during animations

    def color_init(self, stdscr):
        curses.start_color()
        curses.use_default_colors()

        default_bg_id = 21
        default_fg_id = 22
        very_exact_color_of_bg = 94
        very_exact_color_of_fg = 898
        curses.init_color(default_bg_id, very_exact_color_of_bg, very_exact_color_of_bg, very_exact_color_of_bg)
        curses.init_color(default_fg_id, very_exact_color_of_fg, very_exact_color_of_fg, very_exact_color_of_fg)
        curses.init_pair(default_bg_id, curses.COLOR_WHITE, default_bg_id)

        # Cyberpunk green: rgb(208, 236, 88) converted to curses values (0-1000)
        curses.init_color(277, 816, 925, 345) 
        curses.init_pair(255, 277, default_bg_id)
        curses.init_pair(254, curses.COLOR_BLACK, 277)
        curses.init_pair(253, default_bg_id, 277)

        curses.init_color(276, 161, 176, 224)
        curses.init_pair(252, 277, 276)
        curses.init_pair(251, default_bg_id, 276)
        curses.init_pair(250, 276, default_bg_id)
        curses.init_pair(241, curses.COLOR_WHITE, 276)

        curses.init_color(275, 545, 788, 788)
        curses.init_pair(249, 275, 276)
        curses.init_pair(248, 275, default_bg_id)

        curses.init_color(274, 239, 255, 302)
        curses.init_pair(247, 274, 276)
        curses.init_pair(246, 274, default_bg_id)

        curses.init_color(273, 122, 125, 102)
        curses.init_pair(245, 277, 273)
        curses.init_pair(244, 273, default_bg_id)
        curses.init_pair(243, default_bg_id, 273)
        curses.init_pair(242, 273, 274)

        curses.init_color(272, 94, 94, 165)
        curses.init_pair(240, curses.COLOR_WHITE, 272)
        curses.init_pair(239, 272, default_bg_id)
        curses.init_pair(238, default_bg_id, 272)
        curses.init_pair(237, 275, 272)

        curses.init_color(271, 992, 380, 318)  # Failed red
        curses.init_color(270, 192, 827, 498)  # Success green
        curses.init_pair(236, curses.COLOR_BLACK, 271)
        curses.init_pair(235, curses.COLOR_BLACK, 270)
        curses.init_pair(234, default_bg_id, 271)
        curses.init_pair(233, default_bg_id, 270)

    def build_code_matrix(self, datamines):
        """
        Generate a 5x5 Breach-Protocol grid that contains every hex value
        appearing in the supplied Datamine sequences, plus random filler
        hex pairs to reach 25 total cells.

        Args:
            datamines (list[list[str]]): e.g. [['55', '1C', 'BD'],
                                            ['1C', 'E9', 'FF', '55'],
                                            ['BD', '1C']]

        Returns:
            list[list[str]]: 5x5 grid stored in variable `code_matrix`
        """

        # Collect mandatory hexes (keep duplicates for decoys)
        mandatory = [hex_code for seq in datamines for hex_code in seq]

        # Generate filler hex pairs until we have 25 total
        def random_hex_pair():
            return f"{self.CHARACTERS[random.randint(0, 5)]}"

        while len(mandatory) < 25:
            mandatory.append(random_hex_pair())

        # Shuffle and fill the 5×5 grid
        random.shuffle(mandatory)
        code_matrix = [
            mandatory[i*5:(i+1)*5]
            for i in range(5)
        ]

        return code_matrix

    def update_gui(self, stdscr, active_axis: int, last_selected: list[int], hovering: list[int], clicked=False, first=False):
        stdscr.clear()
        hovering_over = ""
        click_executed = False
        click_location = [0, 0]

        # Main GUI elements
        stdscr.addstr(1, 1,  "BREACH TIME REMAINING", curses.color_pair(255))
        stdscr.addstr(4, 1,  "▄", curses.color_pair(255))
        stdscr.addstr(4, 2,   " CODE MATRIX                         ", curses.color_pair(254))

        # Generate datamine lengths for code matrix generation
        line2_length = 0
        num_chars = [0, 0, 0]
        for i in range(len(self.datamines)):
            if first:
                if i == 0:
                    num_chars[i] = random.choices([2, 3], weights=[80, 20], k=1)[0]
                elif i == 1:
                    num_chars[i] = 3
                    line2_length = num_chars[i]
                elif i == 2:
                    if line2_length >= 4:
                        num_chars[i] = 4
                    else:
                        num_chars[i] = random.choices([3, 4], weights=[80, 20], k=1)[0]
            else:
                num_chars[i] = len(self.datamines[i])

        # Generate hex sequences with chain connections on first run
        if first:
            # Create datamine sequences that chain together:
            # Option 1: 1→2→3→1 or Option 2: 1→3→2→1
            
            for i in range(len(self.datamines)):
                self.datamines[i] = []
                for j in range(num_chars[i]):
                    self.datamines[i].append(self.CHARACTERS[random.randint(0, 5)])
            
            next_datamine = random.randint(1, 2)
            
            if next_datamine == 1:
                self.datamines[1][0] = self.datamines[0][-1]
                self.datamines[2][0] = self.datamines[1][-1]
                self.datamines[2][-1] = self.datamines[0][0]
            elif next_datamine == 2:
                self.datamines[2][0] = self.datamines[0][-1]
                self.datamines[1][0] = self.datamines[2][-1]
                self.datamines[1][-1] = self.datamines[0][0]
        
        # Initialize highlighting arrays
        gray = []
        gray_selected = []
        gray_gray = []
        green_bg = []
        datamine_hover_char = ""

        # Populate selectable axis cells
        if active_axis == 0:  # vertical
            x_coord = last_selected[0]
            for i in range(len(self.code_matrix)):
                gray.append([x_coord, i])

        if active_axis == 1:  # horizontal
            y_coord = last_selected[1]
            for j in range(len(self.code_matrix[y_coord])):
                gray.append([j, y_coord])

        # Handle mouse hover selection
        hover_matrix_x = -1
        hover_matrix_y = -1
        if hovering[0] >= 9 and hovering[0] <= 30 and hovering[1] >= 6 and hovering[1] <= 14:
            x_found = False
            y_found = False

            if hovering[1] % 2 == 0:
                y_found = True
                hover_matrix_y = (hovering[1] - 6) // 2               
            if (hovering[0] - 9) % 5 <= 1:
                x_found = True
                hover_matrix_x = (hovering[0] - 9) // 5

            if x_found and y_found and [hover_matrix_x, hover_matrix_y] in gray:
                if self.code_matrix[hover_matrix_y][hover_matrix_x] != "[]":
                    hovering_over = self.code_matrix[hover_matrix_y][hover_matrix_x]
                    gray_selected = [hover_matrix_x, hover_matrix_y]

        if clicked:
            if hovering_over in self.CHARACTERS:
                if len(self.buffer) < self.max_buffer_length:
                    self.datamine_completed_before = self.get_datamine_completion(self.buffer, self.datamines)
                    gray_gray.append(gray_selected)
                    self.buffer.append(hovering_over)
                    click_location = gray_selected.copy()
                    self.code_matrix[gray_selected[1]][gray_selected[0]] = "[]"
                    gray_selected = []
                    click_executed = True

        # Mark used cells
        for i in range(len(self.code_matrix)):
            for j in range(len(self.code_matrix[i])):
                if self.code_matrix[i][j] == "[]":
                    gray_gray.append([j, i])

        # Populate potential next axis cells
        if gray_selected:
            if active_axis == 0:  # current vertical, next horizontal
                y_coord = gray_selected[1]
                for j in range(len(self.code_matrix[y_coord])):
                    green_bg.append([j, y_coord])

            if active_axis == 1:  # current horizontal, next vertical
                x_coord = gray_selected[0]
                for i in range(len(self.code_matrix)):
                    green_bg.append([x_coord, i])

        datamine_completed = self.get_datamine_completion(self.buffer, self.datamines)

        # Check datamine completion and failure states
        for i, datamine in enumerate(self.datamines):
            if datamine_completed[i] == len(datamine) and not self.failed_datamines[i] and not self.buffer == []:
                self.completed_datamines[i] = True

            # Mark as failed if buffer space is insufficient to complete
            if self.max_buffer_length - len(self.buffer) < len(datamine) - datamine_completed[i] and not self.completed_datamines[i] and not self.buffer == []:
                self.failed_datamines[i] = True

        # Handle datamine hover highlighting
        if not first:
            effective_progress = []
            for idx in range(len(self.datamines)):
                if self.completed_datamines[idx]:
                    effective_progress.append(len(self.datamines[idx]))
                elif self.failed_datamines[idx]:
                    effective_progress.append(self.datamine_completed_before[idx])
                else:
                    effective_progress.append(datamine_completed[idx])
            
            max_completed = max(effective_progress) if any(effective_progress) else 0
            for i_data, datamine in enumerate(self.datamines):
                y_datamine = 6 + i_data * 2
                if hovering[1] == y_datamine:
                    x_offset = self.datamine_current_offsets[i_data]
                    for j_data, char_data in enumerate(datamine):
                        x_datamine = 41 + (j_data + x_offset) * 4
                        if hovering[0] >= x_datamine and hovering[0] <= x_datamine + 1:
                            datamine_hover_char = char_data
                            break
                if datamine_hover_char:
                    break
        
        # Generate code matrix on first run
        if first:
            self.code_matrix = self.build_code_matrix(self.datamines)
                
        for i in range(len(self.code_matrix)):
            y = 6 + i * 2
            for j in range(len(self.code_matrix[i])):
                x = 9 + j * 5
                
                data = self.code_matrix[i][j]

                # Determine cell state for styling
                is_gray_selected = [j, i] == gray_selected
                is_gray = [j, i] in gray
                is_green_bg = [j, i] in green_bg
                is_gray_gray = [j, i] in gray_gray

                # Apply character styling based on state
                if is_gray_selected:
                    stdscr.addstr(y, x, data, curses.color_pair(249))
                elif datamine_hover_char and data == datamine_hover_char and is_gray and not is_gray_gray:
                    stdscr.addstr(y, x, data, curses.color_pair(249))
                elif is_gray_gray and is_gray:
                    stdscr.addstr(y, x, data, curses.color_pair(247))
                elif is_gray_gray and is_green_bg:
                    stdscr.addstr(y, x, data, curses.color_pair(243))
                elif is_gray and is_green_bg:
                    stdscr.addstr(y, x, data, curses.color_pair(252))
                elif is_gray:
                    stdscr.addstr(y, x, data, curses.color_pair(252))
                elif is_green_bg:
                    stdscr.addstr(y, x, data, curses.color_pair(245))
                elif is_gray_gray:
                    stdscr.addstr(y, x, data, curses.color_pair(246))
                else:
                    stdscr.addstr(y, x, data, curses.color_pair(255))

                # Cell padding for visual highlighting
                padding_color = -1
                padding_axis = -1

                # Handle axis intersection styling
                if is_gray and is_green_bg:
                    green_padding_axis = 1 if active_axis == 0 else 0
                    if green_padding_axis == 1:
                        if j < 4: stdscr.addstr(y, x + 2, "   ", curses.color_pair(245))
                        else: stdscr.addstr(y, x + 2, "  ", curses.color_pair(245))
                        if j == 0: stdscr.addstr(y, x - 2, "  ", curses.color_pair(245))
                    if green_padding_axis == 0:
                        if i < 4: stdscr.addstr(y + 1, x - 1, "    ", curses.color_pair(245))
                        else: stdscr.addstr(y + 1, x-1, "▄▄▄▄", curses.color_pair(243))
                        if i == 0: stdscr.addstr(y - 1, x-1, "▄▄▄▄", curses.color_pair(244))

                    padding_color = 252
                    padding_axis = active_axis

                elif is_gray:
                    padding_color = 252
                    padding_axis = active_axis
                elif is_green_bg:
                    padding_color = 245
                    padding_axis = 1 if active_axis == 0 else 0

                if padding_color != -1:
                    if padding_axis == 1:
                        stdscr.addstr(y, x - 1, " ", curses.color_pair(padding_color))
                        if j < 4:
                            stdscr.addstr(y, x + 2, "   ", curses.color_pair(padding_color))
                        else:
                            stdscr.addstr(y, x + 2, "  ", curses.color_pair(padding_color))
                        if j == 0:
                            stdscr.addstr(y, x - 2, "  ", curses.color_pair(padding_color))

                    if padding_axis == 0:
                        stdscr.addstr(y, x - 1, " ", curses.color_pair(padding_color))
                        stdscr.addstr(y, x + 2, " ", curses.color_pair(padding_color))
                        if i < 4:
                            stdscr.addstr(y + 1, x - 1, "    ", curses.color_pair(padding_color))
                        else:
                            stdscr.addstr(y + 1, x-1, "▄▄▄▄", curses.color_pair(251 if is_gray else 243))
                        if i == 0:
                            stdscr.addstr(y - 1, x-1, "▄▄▄▄", curses.color_pair(250 if is_gray else 244))

        # Buffer display
        stdscr.addstr(0, 41, "BUFFER", curses.color_pair(255))

        for i in range(len(self.buffer)):
            stdscr.addstr(2, 41+i*4, f"{self.buffer[i]}", curses.color_pair(255))

        for i in range(self.max_buffer_length - len(self.buffer)):
            if i == 5 - len(self.buffer) and hovering_over != "":
                stdscr.addstr(2, 61-i*4, hovering_over, curses.color_pair(248))
            else:
                stdscr.addstr(2, 61-i*4, "░░", curses.color_pair(255))

        stdscr.addstr(4, 41,  "SEQUENCE REQUIRED TO UPLOAD", curses.color_pair(255))

        # Datamine animation and display logic
        if clicked and click_executed:

            max_completed_after = max(datamine_completed) if any(datamine_completed) else 0
            
            # Calculate target offsets for datamine alignment
            progress_on_unfinished = any(
                datamine_completed[i] > 0 or self.datamine_completed_before[i] > 0
                for i in range(len(self.datamines))
                if not self.completed_datamines[i] and not self.failed_datamines[i]
            )

            if not progress_on_unfinished and not any(self.datamine_completed_before):
                target_offsets = [0, 0, 0]
            else:
                effective_progress = []
                for i in range(len(self.datamines)):
                    if self.completed_datamines[i]:
                        effective_progress.append(len(self.datamines[i]))
                    elif self.failed_datamines[i]:
                        effective_progress.append(self.datamine_completed_before[i])
                    else:
                        effective_progress.append(datamine_completed[i])
                
                max_progress = max(effective_progress) if any(effective_progress) else 0
                target_offsets = [max_progress - ep for ep in effective_progress]
                
                # Handle datamine restarts (when progress decreases)
                for i in range(len(target_offsets)):
                    if (not self.completed_datamines[i] and not self.failed_datamines[i] and 
                        datamine_completed[i] < self.datamine_completed_before[i]):
                        pass  # Allow reset for restarted datamines
                    else:
                        target_offsets[i] = max(target_offsets[i], self.datamine_current_offsets[i])
                
                # Special handling: completed datamines should maintain their final offset
                for i in range(len(target_offsets)):
                    if self.completed_datamines[i] or self.failed_datamines[i]:
                        target_offsets[i] = self.datamine_current_offsets[i]

            # Calculate animation frame counts
            max_shift = 0
            for i in range(len(self.datamines)):
                 shift = abs(target_offsets[i] - self.datamine_current_offsets[i])
                 if shift > max_shift:
                     max_shift = shift
            
            shift_animation_frames = max_shift * 4
            swoop_animation_frames = 25
            animation_frames = max(shift_animation_frames, swoop_animation_frames)

            if animation_frames > 0:
                # Set animation flag to prevent timer refreshes
                self.animating = True
                
                for frame in range(animation_frames + 1):
                    # Update timer at the start of each frame
                    self.update_timer_if_needed(stdscr)
                    
                    # Redraw static UI elements
                    stdscr.addstr(0, 41, "BUFFER", curses.color_pair(255))
                    for i_buf in range(len(self.buffer)):
                        stdscr.addstr(2, 41 + i_buf * 4, f"{self.buffer[i_buf]}", curses.color_pair(255))
                    for i_buf in range(self.max_buffer_length - len(self.buffer)):
                        stdscr.addstr(2, 61 - i_buf * 4, "░░", curses.color_pair(255))
                    stdscr.addstr(4, 41, "SEQUENCE REQUIRED TO UPLOAD", curses.color_pair(255))
                    
                    # Animate datamines
                    for i in range(len(self.datamines)):
                        y = 6 + i * 2
                        stdscr.addstr(y, 41, " " * 55)
                        
                        is_newly_completed = self.completed_datamines[i] and not self.dv_firsts[i]
                        is_newly_failed = self.failed_datamines[i] and not self.dv_firsts[i]

                        # Display completed/failed datamines with animation
                        if self.completed_datamines[i] or self.failed_datamines[i]:
                            if is_newly_completed or is_newly_failed:
                                if is_newly_completed:
                                    string_to_draw = f"  INSTALLED                 "
                                    color = 235
                                else:
                                    string_to_draw = f"  FAILED                    "
                                    color = 236
                                
                                swoop_progress = min(1.0, frame / swoop_animation_frames)
                                visible_chars = int(len(string_to_draw) * swoop_progress)
                                stdscr.addstr(y, 41, string_to_draw[:visible_chars], curses.color_pair(color))
                                
                                if swoop_progress >= 0.95:
                                    if is_newly_completed:
                                        stdscr.addstr(y, 41 + 45, "▄", curses.color_pair(233))
                                    else:
                                        stdscr.addstr(y, 41 + 45, "▄", curses.color_pair(234))
                            else:
                                arrow = "∇" * (i + 1)
                                text = arrow * (i + 1)
                                string_INSTALLED = f"  INSTALLED                 {text:>3} DATAMINE_V{i+1}  "
                                string_FAILED = f"  FAILED                    {text:>3} DATAMINE_V{i+1}  "
                                final_string = string_INSTALLED if self.completed_datamines[i] else string_FAILED
                                color = 235 if self.completed_datamines[i] else 236
                                stdscr.addstr(y, 41, final_string, curses.color_pair(color))
                                if self.completed_datamines[i]:
                                    stdscr.addstr(y, 41 + 45, "▄", curses.color_pair(233))
                                else:
                                    stdscr.addstr(y, 41 + 45, "▄", curses.color_pair(234))
                        else:
                            # Animate unfinished datamines
                            start_offset = self.datamine_current_offsets[i]
                            target_offset = target_offsets[i]
                            
                            progress = min(1.0, frame / shift_animation_frames) if shift_animation_frames > 0 else 1.0
                            current_offset = start_offset + (target_offset - start_offset) * progress

                            for j, char_data in enumerate(self.datamines[i]):
                                x = 41 + round((j + current_offset) * 4)
                                is_next_char = (j == datamine_completed[i])
                                if is_next_char:
                                    stdscr.addstr(y, x, char_data, curses.color_pair(240))
                                elif j < datamine_completed[i]:
                                    stdscr.addstr(y, x, char_data, curses.color_pair(255))
                                else:
                                    stdscr.addstr(y, x, char_data)
                            
                            arrow = "∇" * (i + 1)
                            stdscr.addstr(y, 73, f"DATAMINE_V{i+1}")
                            stdscr.addstr(y, 69, f"{arrow:>3}", curses.color_pair(255))

                    stdscr.refresh()
                    
                    # Simple sleep without timer updates to avoid interference
                    time.sleep(0.008)
                
                # Clear animation flag
                self.animating = False
            
            # Update animation state after completion
            self.datamine_current_offsets = target_offsets
            for i in range(len(self.datamines)):
                if self.completed_datamines[i] or self.failed_datamines[i]:
                    self.dv_firsts[i] = True
            
            finished_by_completion = all(
                failed or completed for failed, completed in zip(self.failed_datamines, self.completed_datamines))
            
            stdscr.refresh()
            return click_executed, click_location, finished_by_completion

        # Update datamine offsets for consistent positioning
        effective_progress = []
        for i in range(len(self.datamines)):
            if self.completed_datamines[i]:
                effective_progress.append(len(self.datamines[i]))
            elif self.failed_datamines[i]:
                effective_progress.append(self.datamine_completed_before[i])
            else:
                effective_progress.append(datamine_completed[i])
        
        if any(effective_progress):
            max_progress = max(effective_progress)
            
            progress_on_unfinished = any(
                datamine_completed[i] > 0 or self.datamine_completed_before[i] > 0
                for i in range(len(self.datamines))
                if not self.completed_datamines[i] and not self.failed_datamines[i]
            )
            
            if not progress_on_unfinished and not any(self.datamine_completed_before):
                self.datamine_current_offsets = [0, 0, 0]
            else:
                target_offsets = [max_progress - ep for ep in effective_progress]
                for i in range(len(target_offsets)):
                    if (not self.completed_datamines[i] and not self.failed_datamines[i] and 
                        datamine_completed[i] < self.datamine_completed_before[i]):
                        pass  # Allow reset for restarted datamines
                    else:
                        target_offsets[i] = max(target_offsets[i], self.datamine_current_offsets[i])
                
                # Special handling: completed datamines should maintain their final offset
                for i in range(len(target_offsets)):
                    if self.completed_datamines[i] or self.failed_datamines[i]:
                        target_offsets[i] = self.datamine_current_offsets[i]
                
                self.datamine_current_offsets = target_offsets


        # Final drawing of datamines (non-animation path)             
        for i in range(len(self.datamines)):
            y = 6 + i * 2
            
            # Only draw hex codes for unfinished datamines
            if not self.completed_datamines[i] and not self.failed_datamines[i]:
                for j in range(num_chars[i]):
                    x = 41 + (j + self.datamine_current_offsets[i]) * 4
                    
                    data = self.datamines[i][j]

                    highlight = False
                    is_datamine_hover = (data == datamine_hover_char and hovering[1] == y and hovering[0] >= x and hovering[0] <= x + 1)
                    is_next_char = (j == datamine_completed[i])

                    if is_next_char:
                        highlight = True
                        if data == hovering_over or is_datamine_hover:
                            stdscr.addstr(y, x, data, curses.color_pair(237))
                        else:
                            stdscr.addstr(y, x, data, curses.color_pair(240))
                    elif is_datamine_hover:
                        stdscr.addstr(y, x, data, curses.color_pair(248))
                    elif j < datamine_completed[i]:
                        stdscr.addstr(y, x, data, curses.color_pair(255))
                    else:
                        stdscr.addstr(y, x, data)

                    # Character highlighting
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

            # Display datamine status
            arrow = "∇"
            text = arrow * (i + 1)
            y_offset = 6 + i * 2
            string_INSTALLED = f"  INSTALLED                 {text:>3} DATAMINE_V{i+1}  "
            string_FAILED = f"  FAILED                    {text:>3} DATAMINE_V{i+1}  "
            if self.completed_datamines[i]:
                stdscr.addstr(y_offset, 41, string_INSTALLED, curses.color_pair(235))
                stdscr.addstr(y_offset, 41 + 45, "▄", curses.color_pair(233))
            elif self.failed_datamines[i]:
                stdscr.addstr(y_offset, 41, string_FAILED, curses.color_pair(236))
                stdscr.addstr(y_offset, 41 + 45, "▄", curses.color_pair(234))
            else:
                stdscr.addstr(y_offset, 73, f"DATAMINE_V{i+1}")
                stdscr.addstr(y_offset, 69, f"{text:>3}", curses.color_pair(255))

        stdscr.refresh()

        finished_by_completion = all(
        failed or completed for failed, completed in zip(self.failed_datamines, self.completed_datamines))

        return click_executed, click_location, finished_by_completion

    def is_over_grid(self, pos):
        """Check if a coordinate is within the interactive grid areas."""
        x, y = pos
        # Matrix grid: 2 chars wide with 3 char spacing
        is_over_matrix = (y >= 6 and y <= 14 and y % 2 == 0) and \
                         (x >= 9 and x <= 33 and (x - 9) % 5 < 2)

        # Datamine grid: 2 chars wide with 2 char spacing
        is_over_datamines = (y >= 6 and y <= 10 and y % 2 == 0) and \
                            (x >= 41 and x <= 56 and (x - 41) % 4 < 2)

        return is_over_matrix or is_over_datamines

    def get_datamine_completion(self, current_buffer, current_datamines):
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

    def draw_time(self, stdscr, time_left, time_given):
        seconds = int(time_left)
        milliseconds = int((time_left - seconds) * 100)
        time_left_str = f"{seconds:02}:{milliseconds:02}"

        stdscr.addstr(1, 34, f"{time_left_str:>5}", curses.color_pair(255))

        progress_bar_full_length = 38
        progress_chars_count = int(progress_bar_full_length * (time_left / time_given))
        progress_bar_str = '▄' * progress_chars_count
        stdscr.addstr(2, 1, f"{progress_bar_str:█<{progress_bar_full_length}}", curses.color_pair(253))

        stdscr.refresh()

    def update_timer_if_needed(self, stdscr):
        """Update timer display if enough time has passed"""
        current_time = time.time()
        if current_time - self.last_timer_update >= self.timer_update_interval:
            if self.start_time:
                elapsed_time = current_time - self.start_time
                self.time_left = max(0, self.time_given - elapsed_time)
            # Only refresh if not animating
            if not self.animating:
                self.draw_time(stdscr, self.time_left, self.time_given)
            else:
                # Update timer display without refresh during animations
                self.draw_time_no_refresh(stdscr, self.time_left, self.time_given)
            self.last_timer_update = current_time

    def draw_time_no_refresh(self, stdscr, time_left, time_given):
        """Draw timer without calling refresh (for use during animations)"""
        seconds = int(time_left)
        milliseconds = int((time_left - seconds) * 100)
        time_left_str = f"{seconds:02}:{milliseconds:02}"

        stdscr.addstr(1, 34, f"{time_left_str:>5}", curses.color_pair(255))

        progress_bar_full_length = 38
        progress_chars_count = int(progress_bar_full_length * (time_left / time_given))
        progress_bar_str = '▄' * progress_chars_count
        stdscr.addstr(2, 1, f"{progress_bar_str:█<{progress_bar_full_length}}", curses.color_pair(253))

    # ...existing code...

    def main(self, stdscr):
        stdscr.clear()

        curses.curs_set(0)
        self.color_init(stdscr)

        # Check minimum screen size
        max_y, max_x = stdscr.getmaxyx()
        if max_y < 16 or max_x < 84:
            stdscr.addstr(0, 0, "Screen size too small. Minimum size is 14 rows and 84 columns.", curses.color_pair(1))
            stdscr.refresh()
            stdscr.getch()

        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        stdscr.nodelay(True)

        # Initial timer display
        self.draw_time(stdscr, self.time_left, self.time_given)
        
        self.update_gui(stdscr, self.active_axis, self.last_selected, self.hovering, first=True)

        while len(self.buffer) < 6 and self.finished_by_completion == False:
            # Update timer regularly
            self.update_timer_if_needed(stdscr)

            if self.start_time and self.time_left == 0:
                break

            key = stdscr.getch()
            try:
                _, x, y, _, button = curses.getmouse()
            except curses.error:
                x, y, button = -1, -1, 0

            if key == curses.KEY_MOUSE:
                if button & (curses.BUTTON1_PRESSED | curses.BUTTON1_CLICKED):
                    check, location, self.finished_by_completion = self.update_gui(stdscr, self.active_axis, self.last_selected, self.hovering, clicked=True)
                    if check:
                        if self.start_time is None:
                            self.start_time = time.time()
                        self.last_selected = location
                        self.active_axis = 1 if self.active_axis == 0 else 0
                        self.update_gui(stdscr, self.active_axis, self.last_selected, self.hovering)

            self.hovering = [x, y]

            if not self.hovering == self.old_hovering:
                if self.is_over_grid(self.hovering) or self.is_over_grid(self.old_hovering):
                    _, _, self.finished_by_completion = self.update_gui(stdscr, self.active_axis, self.last_selected, self.hovering)

            self.old_hovering = self.hovering
        
        # Final timer update and display before ending
        self.update_timer_if_needed(stdscr)
        stdscr.refresh()
        time.sleep(2)

if __name__ == "__main__":
    game_instance = game()
    curses.wrapper(game_instance.main)