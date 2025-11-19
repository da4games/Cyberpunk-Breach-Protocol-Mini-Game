import locale
import curses
import random
import sys
import time
import os


class Game():
    def __init__(self):
        # Available hex characters for the breach protocol game
        self.CHARACTERS = ("55", "BD", "1C", "E9", "FF", "7A")
        
        # Current selectable axis: 1 = horizontal, 0 = vertical
        self.active_axis = 1  # 1 = horizontal, 0 = vertical
        # Last selected position in the matrix
        self.last_selected = [0, 0]  # x, y coordinates in matrix
        # Current mouse hover position
        self.hovering = [0, 0]
        # Previous hover position for change detection
        self.old_hovering = [0, 0]
        
        # Timer management
        self.start_time = None
        self.time_given = 30
        self.time_left = self.time_given
        self.finished_by_completion = False
        
        # 5x5 matrix containing hex codes for selection
        self.code_matrix = [
        ["", "", "", "", ""],
        ["", "", "", "", ""],
        ["", "", "", "", ""],
        ["", "", "", "", ""],
        ["", "", "", "", ""]
        ]

        # Three datamine sequences that need to be completed
        self.datamines = [
            [],
            [],
            []]

        # Player's selected sequence buffer
        self.buffer = []
        self.max_buffer_length = 6

        # Datamine state tracking
        self.dv_firsts = [False, False, False]  # Track datamine animation state
        self.datamine_completed_before = [0, 0, 0]  # Previous completion counts
        self.completed_datamines = [False, False, False]  # Successfully completed datamines
        self.failed_datamines = [False, False, False]  # Failed datamines (impossible to complete)
        self.datamine_current_offsets = [0, 0, 0]  # On-screen position offsets for alignment
        
        # Timer update control
        self.last_timer_update = 0
        self.timer_update_interval = 0.01  # Update every 10ms
        self.animating = False  # Flag to prevent timer refreshes during animations

    def reset_game(self):
        """Reset all game state to initial values for a new round."""
        self.__init__()

    def color_init(self, stdscr):
        """Initialize all color pairs for the cyberpunk-themed interface."""
        if curses.can_change_color() and curses.COLORS >= 256:
            curses.start_color()
            curses.use_default_colors()

            # Base colors for the interface
            default_bg_id = 21
            default_fg_id = 22
            very_exact_color_of_bg = 94
            very_exact_color_of_fg = 898
            curses.init_color(default_bg_id, very_exact_color_of_bg, very_exact_color_of_bg, very_exact_color_of_bg)
            curses.init_color(default_fg_id, very_exact_color_of_fg, very_exact_color_of_fg, very_exact_color_of_fg)
            curses.init_pair(default_bg_id, curses.COLOR_WHITE, default_bg_id)  # (fg=white, bg=default_bg)

            # Cyberpunk green: rgb(53, 60, 22)
            curses.init_color(247, 816, 925, 345)
            curses.init_pair(255, 247, default_bg_id)  # (fg=green, bg=default_bg)
            curses.init_pair(254, curses.COLOR_BLACK, 247)  # (fg=black, bg=green)
            curses.init_pair(253, default_bg_id, 247)  # (fg=default_bg, bg=green)

            # Dark gray-blue: rgb(41, 45, 57) # the gray bar in the matrix
            curses.init_color(246, 161, 176, 224)
            curses.init_pair(252, 247, 246)  # (fg=green, bg=dark_gray_blue)
            curses.init_pair(251, default_bg_id, 246)  # (fg=default_bg, bg=dark_gray_blue)
            curses.init_pair(250, 246, default_bg_id)  # (fg=dark_gray_blue, bg=default_bg)
            curses.init_pair(241, curses.COLOR_WHITE, 246)  # (fg=white, bg=dark_gray_blue)

            # Cyan: rgb(139, 202, 202)
            curses.init_color(245, 545, 788, 788)
            curses.init_pair(249, 245, 246)  # (fg=cyan, bg=dark_gray_blue) --> selected cell in matrix
            curses.init_pair(248, 245, default_bg_id)  # (fg=cyan, bg=default_bg)

            # Dark gray: rgb(61, 65, 76)
            curses.init_color(244, 239, 255, 302)
            curses.init_pair(247, 244, 246)  # (fg=dark_gray, bg=dark_gray_blue)
            curses.init_pair(246, 244, default_bg_id)  # (fg=dark_gray, bg=default_bg)

            # Dark green: rgb(31, 32, 26)
            curses.init_color(243, 122, 125, 102)
            curses.init_pair(245, 247, 243)  # (fg=green, bg=dark_green)
            curses.init_pair(244, 243, default_bg_id)  # (fg=dark_green, bg=default_bg)
            curses.init_pair(243, default_bg_id, 243)  # (fg=default_bg, bg=dark_green)
            curses.init_pair(242, 243, 244)  # (fg=dark_green, bg=dark_gray)

            # Very dark blue: rgb(24, 24, 42)
            curses.init_color(242, 94, 94, 165)
            curses.init_pair(240, curses.COLOR_WHITE, 242)  # (fg=white, bg=very_dark_blue)
            curses.init_pair(239, 242, default_bg_id)  # (fg=very_dark_blue, bg=default_bg)
            curses.init_pair(238, default_bg_id, 242)  # (fg=default_bg, bg=very_dark_blue)
            curses.init_pair(237, 245, 242)  # (fg=cyan, bg=very_dark_blue)

            # Failed red: rgb(253, 97, 81)
            curses.init_color(241, 992, 380, 318)
            # Success green: rgb(49, 211, 126)
            curses.init_color(240, 192, 827, 498)
            curses.init_pair(236, curses.COLOR_BLACK, 241)  # (fg=black, bg=failed_red)
            curses.init_pair(235, curses.COLOR_BLACK, 240)  # (fg=black, bg=success_green)
            curses.init_pair(234, default_bg_id, 241)  # (fg=default_bg, bg=failed_red)
            curses.init_pair(233, default_bg_id, 240)  # (fg=default_bg, bg=success_green)
            curses.init_pair(232, 241, default_bg_id)  # (fg=failed_red, bg=default_bg)
            curses.init_pair(231, 240, default_bg_id)  # (fg=success_green, bg=default_bg)
            curses.init_pair(230, 241, 240)  # (fg=failed_red, bg=success_green)
            curses.init_pair(229, 240, 241)  # (fg=success_green, bg=failed_red)
            curses.init_pair(228, 241, 241)  # (fg=failed_red, bg=failed_red)
            curses.init_pair(227, 240, 240)  # (fg=success_green, bg=success_green) for Green-Green borders
            
            # Additional color pairs for border highlighting between datamines  
            curses.init_pair(226, 240, 242)  # (fg=success_green, bg=very_dark_blue) for green datamine highlighting
            curses.init_pair(225, 241, 242)  # (fg=failed_red, bg=very_dark_blue) for red datamine highlighting
            
            curses.init_color(239, 79, 145, 102)  # Custom darker green for finish screen
            curses.init_pair(224, 240, 239)  # (fg=success_green, bg=darker_green)
            curses.init_color(238, 224, 63, 55)  # Custom dark red for error messages
            curses.init_pair(223, 241, 238)  # (fg=dark_red, bg=default_bg)
        else:
            curses.endwin()
            print("This terminal does not support 256 colors or color changes. You may use a different terminal.")
            time.sleep(5)
            sys.exit(0)

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

        # Generate hex sequences with more realistic connections on first run
        if first:
            # Generate initial random sequences for all datamines
            for i in range(len(self.datamines)):
                self.datamines[i] = []
                for j in range(num_chars[i]):
                    self.datamines[i].append(self.CHARACTERS[random.randint(0, 5)])
            
            # Randomly decide connection strategy with weighted probabilities
            connection_type = random.choices(
                ['full_chain', 'partial_chain', 'independent', 'pairs'],
                weights=[25, 35, 25, 15],  # More realistic distribution
                k=1
            )[0]
            
            if connection_type == 'full_chain':
                # All datamines chain together (original behavior)
                next_datamine = random.randint(1, 2)
                if next_datamine == 1:
                    self.datamines[1][0] = self.datamines[0][-1]
                    self.datamines[2][0] = self.datamines[1][-1]
                else:
                    self.datamines[2][0] = self.datamines[0][-1]
                    self.datamines[1][0] = self.datamines[2][-1]
                    
            elif connection_type == 'partial_chain':
                # Only two datamines chain together
                chain_pair = random.choice([(0, 1), (0, 2), (1, 2)])
                first_dm, second_dm = chain_pair
                self.datamines[second_dm][0] = self.datamines[first_dm][-1]
                
            elif connection_type == 'pairs':
                # Two datamines might share a common hex at different positions
                if random.random() < 0.7:  # 70% chance of having shared hex
                    shared_hex = self.CHARACTERS[random.randint(0, 5)]
                    dm1, dm2 = random.sample(range(3), 2)  # Pick two different datamines
                    pos1 = random.randint(0, len(self.datamines[dm1]) - 1)
                    pos2 = random.randint(0, len(self.datamines[dm2]) - 1)
                    self.datamines[dm1][pos1] = shared_hex
                    self.datamines[dm2][pos2] = shared_hex
                    
            # connection_type == 'independent' means no connections (sequences remain as generated)
        
        # Initialize cell highlighting arrays for different states
        gray = []         # Cells on the selectable axis
        gray_selected = []  # Currently hovered cell (if on selectable axis)
        gray_gray = []     # Already used/clicked cells
        green_bg = []      # Cells on the next potential axis
        datamine_hover_char = ""  # Character being hovered in datamine area

        # Populate selectable axis cells
        if active_axis == 0:  # vertical
            x_coord = last_selected[0]
            for i in range(len(self.code_matrix)):
                gray.append([x_coord, i])

        if active_axis == 1:  # horizontal
            y_coord = last_selected[1]
            for j in range(len(self.code_matrix[y_coord])):
                gray.append([j, y_coord])

        # Handle mouse hover selection within the matrix bounds
        hover_matrix_x = -1
        hover_matrix_y = -1
        # Check if mouse is within matrix area (x: 9-30, y: 6-14)
        if hovering[0] >= 9 and hovering[0] <= 30 and hovering[1] >= 6 and hovering[1] <= 14:
            x_found = False
            y_found = False

            # Matrix rows are on even y coordinates (6, 8, 10, 12, 14)
            if hovering[1] % 2 == 0:
                y_found = True
                hover_matrix_y = (hovering[1] - 6) // 2               
            # Matrix columns are spaced 5 apart, with 2-char width
            if (hovering[0] - 9) % 5 <= 1:
                x_found = True
                hover_matrix_x = (hovering[0] - 9) // 5

            # Only highlight if over a selectable cell that isn't already used
            if x_found and y_found and [hover_matrix_x, hover_matrix_y] in gray:
                if self.code_matrix[hover_matrix_y][hover_matrix_x] != "[]":
                    hovering_over = self.code_matrix[hover_matrix_y][hover_matrix_x]
                    gray_selected = [hover_matrix_x, hover_matrix_y]

        # Handle mouse clicks
        if clicked:
            if hovering_over in self.CHARACTERS:
                if len(self.buffer) < self.max_buffer_length:
                    # Store completion state before adding to buffer
                    self.datamine_completed_before = self.get_datamine_completion(self.buffer, self.datamines)
                    gray_gray.append(gray_selected)
                    self.buffer.append(hovering_over)
                    click_location = gray_selected.copy()
                    # Mark cell as used with empty brackets
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
        else:
            # Make green bar follow cursor when hovering in matrix but not over gray bar
            if (hover_matrix_x != -1 and hover_matrix_y != -1 and 
                [hover_matrix_x, hover_matrix_y] not in gray):
                
                if active_axis == 0:  # current vertical, next would be horizontal
                    y_coord = hover_matrix_y
                    for j in range(len(self.code_matrix[y_coord])):
                        green_bg.append([j, y_coord])

                if active_axis == 1:  # current horizontal, next would be vertical
                    x_coord = hover_matrix_x
                    for i in range(len(self.code_matrix)):
                        green_bg.append([x_coord, i])

        datamine_completed = self.get_datamine_completion(self.buffer, self.datamines)

        # Check datamine completion and failure states FIRST
        datamine_states_changed = False
        for i, datamine in enumerate(self.datamines):
            old_completed = self.completed_datamines[i]
            old_failed = self.failed_datamines[i]
            
            if datamine_completed[i] == len(datamine) and not self.failed_datamines[i] and not self.buffer == []:
                self.completed_datamines[i] = True

            # Mark as failed if buffer space is insufficient to complete
            if self.max_buffer_length - len(self.buffer) < len(datamine) - datamine_completed[i] and not self.completed_datamines[i] and not self.buffer == []:
                self.failed_datamines[i] = True
            
            # Check if any datamine state changed
            if (old_completed != self.completed_datamines[i] or old_failed != self.failed_datamines[i]):
                datamine_states_changed = True

        # Recalculate datamine completion AFTER states are updated
        datamine_completed = self.get_datamine_completion(self.buffer, self.datamines)

        # Update datamine offsets for consistent positioning before hover detection
        if not first and not (clicked and click_executed):
            # Update offsets when not in animation (normal hover/update cases)
            # Allow backwards movement when states changed to enable proper realignment
            self.datamine_current_offsets = self.calculate_datamine_offsets(datamine_completed, allow_backwards=datamine_states_changed)

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
                y_datamine = 7 + i_data * 2
                if hovering[1] == y_datamine:
                    x_offset = self.datamine_current_offsets[i_data]
                    for j_data, char_data in enumerate(datamine):
                        x_datamine = 42 + (j_data + x_offset) * 4
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
                elif datamine_hover_char and data == datamine_hover_char and not is_gray_gray:
                    # Highlight ALL instances of the hovered hex code, not just on selectable axis
                    if is_gray:
                        stdscr.addstr(y, x, data, curses.color_pair(249))
                    else:
                        stdscr.addstr(y, x, data, curses.color_pair(248))
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
        stdscr.addstr(0, 42, "BUFFER", curses.color_pair(255))

        for i in range(len(self.buffer)):
            stdscr.addstr(2, 42+i*4, f"{self.buffer[i]}", curses.color_pair(255))

        for i in range(self.max_buffer_length - len(self.buffer)):
            if i == 5 - len(self.buffer) and hovering_over != "":
                stdscr.addstr(2, 62-i*4, hovering_over, curses.color_pair(248))
            else:
                stdscr.addstr(2, 62-i*4, "░░", curses.color_pair(255))

        #static images ─│┌┐└┘├┤
        # Draw the border box around the datamine area
        stdscr.addstr(4, 42, "SEQUENCE REQUIRED TO UPLOAD", curses.color_pair(255))
        # Left border
        stdscr.addstr(3, 40,  "┌", curses.color_pair(255))
        stdscr.addstr(4, 40,  "│", curses.color_pair(255))
        stdscr.addstr(5, 40,  "├", curses.color_pair(255))
        stdscr.addstr(6, 40,  "│", curses.color_pair(255))
        stdscr.addstr(7, 40,  "│", curses.color_pair(255))
        stdscr.addstr(8, 40,  "│", curses.color_pair(255))
        stdscr.addstr(9, 40,  "│", curses.color_pair(255))
        stdscr.addstr(10, 40, "│", curses.color_pair(255))
        stdscr.addstr(11, 40, "│", curses.color_pair(255))
        stdscr.addstr(12, 40, "│", curses.color_pair(255))
        stdscr.addstr(13, 40, "└", curses.color_pair(255))
        
        # Right border
        stdscr.addstr(3, 85,  "┐", curses.color_pair(255))
        stdscr.addstr(4, 85,  "│", curses.color_pair(255))
        stdscr.addstr(5, 85,  "┤", curses.color_pair(255))
        stdscr.addstr(6, 85,  "│", curses.color_pair(255))
        stdscr.addstr(7, 85,  "│", curses.color_pair(255))
        stdscr.addstr(8, 85,  "│", curses.color_pair(255))
        stdscr.addstr(9, 85,  "│", curses.color_pair(255))
        stdscr.addstr(10, 85, "│", curses.color_pair(255))
        stdscr.addstr(11, 85, "│", curses.color_pair(255))
        stdscr.addstr(12, 85, "│", curses.color_pair(255))
        stdscr.addstr(13, 85, "┘", curses.color_pair(255))
        
        # Horizontal borders
        stdscr.addstr(3, 41,  "─" * 44, curses.color_pair(255))
        stdscr.addstr(5, 41,  "─" * 44, curses.color_pair(255))
        stdscr.addstr(13, 41, "─" * 44, curses.color_pair(255))

        # Datamine animation and display logic
        if clicked and click_executed:
            # Calculate target offsets for datamine alignment (completion states are already finalized)
            # Force allow_backwards=True to ensure proper realignment when datamines complete
            target_offsets = self.calculate_datamine_offsets(datamine_completed, allow_backwards=True)
            initial_offsets = self.datamine_current_offsets.copy()

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
                    
                    # Animate datamines
                    for i in range(len(self.datamines)):
                        y = 7 + i * 2
                        # Clear the entire area (stopping before right border at x=85)
                        stdscr.addstr(y - 1, 41, " " * 44)
                        stdscr.addstr(y, 41, " " * 44)
                        stdscr.addstr(y + 1, 41, " " * 44)

                        # Display completed/failed datamines with top-to-bottom animation
                        if self.completed_datamines[i] or self.failed_datamines[i]:
                            self.draw_fat_datamine_block(stdscr, i, self.completed_datamines[i], 
                                                           self.failed_datamines[i])
                        else:
                            # Animate unfinished datamines
                            start_offset = initial_offsets[i]
                            target_offset = target_offsets[i]
                            
                            progress = min(1.0, frame / shift_animation_frames) if shift_animation_frames > 0 else 1.0
                            current_offset = start_offset + (target_offset - start_offset) * progress

                            for j, char_data in enumerate(self.datamines[i]):
                                x = 42 + round((j + current_offset) * 4)
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

        # Final drawing of datamines (non-animation path)             
        for i in range(len(self.datamines)):
            y = 7 + i * 2
            
            # Only draw hex codes for unfinished datamines
            if not self.completed_datamines[i] and not self.failed_datamines[i]:
                for j in range(num_chars[i]):
                    x = 42 + (j + self.datamine_current_offsets[i]) * 4
                    
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
                        # Check for adjacent completed/failed datamines to avoid overwriting their borders
                        above_datamine_fat = (i > 0 and (self.completed_datamines[i-1] or self.failed_datamines[i-1]))
                        below_datamine_fat = (i < 2 and (self.completed_datamines[i+1] or self.failed_datamines[i+1]))
                        
                        if i == 0:
                            stdscr.addstr(y, x + 2, " ", curses.color_pair(240))
                            stdscr.addstr(y, x - 1, " ", curses.color_pair(240))
                            # Only draw top border if no fat datamine above (which there can't be for i=0)
                            stdscr.addstr(y - 1, x - 1, "▄▄▄▄", curses.color_pair(239))
                        elif i == 1:
                            # Only draw borders if no fat datamines above/below
                            if not above_datamine_fat:
                                stdscr.addstr(y - 1, x - 1, "    ", curses.color_pair(240))
                            if not below_datamine_fat:
                                stdscr.addstr(y + 1, x - 1, "    ", curses.color_pair(240))
                            stdscr.addstr(y, x + 2, " ", curses.color_pair(240))
                            stdscr.addstr(y, x - 1, " ", curses.color_pair(240))
                        elif i == 2:
                            stdscr.addstr(y, x + 2, " ", curses.color_pair(240))
                            stdscr.addstr(y, x - 1, " ", curses.color_pair(240))
                            # Only draw bottom border if no fat datamine below (which there can't be for i=2)
                            stdscr.addstr(y + 1, x - 1, "▄▄▄▄", curses.color_pair(238))

            # Display datamine status with fat block design
            if self.completed_datamines[i] or self.failed_datamines[i]:
                self.draw_fat_datamine_block(stdscr, i, self.completed_datamines[i], 
                                           self.failed_datamines[i])
            else:
                arrow = "∇" * (i + 1)
                y_pos = 7 + i * 2
                stdscr.addstr(y_pos, 73, f"DATAMINE_V{i+1}")
                stdscr.addstr(y_pos, 69, f"{arrow:>3}", curses.color_pair(255))

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

        # Datamine grid: 2 chars wide with 4 char spacing, extended to account for shifted datamines
        # Calculate maximum possible extent: 42 + (max_chars + max_offset) * 4 + 1
        # Assuming max 4 chars + max offset of 4 = 8 * 4 = 32, so max x would be around 74
        is_over_datamines = (y >= 7 and y <= 11 and y % 2 == 1) and \
                            (x >= 42 and x <= 74 and (x - 42) % 4 < 2)

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

    def calculate_datamine_offsets(self, datamine_completed, allow_backwards=False):
        """
        Calculate target offsets for datamine alignment based on current progress.
        
        The goal: Align all ACTIVE datamines so their "next expected character" positions line up.
        Completed/failed datamines stay at their current positions.
        
        Args:
            datamine_completed: List of completion counts for each datamine
            allow_backwards: Whether to allow offsets to move backwards (for forced realignment)
        
        Returns:
            List of target offset values for each datamine
        """
        target_offsets = []
        
        # Step 1: Get the current progress for each datamine and identify active ones
        datamine_progress = []
        active_datamines = []  # Track which datamines are still active
        
        for i in range(len(self.datamines)):
            if self.completed_datamines[i]:
                # Completed datamines: consider their full length as progress
                datamine_progress.append(len(self.datamines[i]))
            elif self.failed_datamines[i]:
                # Failed datamines: freeze at their progress when they failed
                datamine_progress.append(self.datamine_completed_before[i])
            else:
                # Active datamines: use current progress
                datamine_progress.append(datamine_completed[i])
                active_datamines.append(i)  # Track this as an active datamine
        
        # Step 2: Find the maximum progress among ACTIVE datamines only for alignment reference
        if active_datamines:
            max_active_progress = max(datamine_progress[i] for i in active_datamines)
        else:
            max_active_progress = 0
        
        # Step 3: Calculate target offsets for each datamine
        for i in range(len(self.datamines)):
            if self.completed_datamines[i] or self.failed_datamines[i]:
                # Completed/failed datamines: keep their current position
                target_offsets.append(self.datamine_current_offsets[i])
            else:
                # Active datamines: calculate offset to align with max progress among active datamines
                # The offset pushes the datamine to the right so its next character aligns
                progress_difference = max_active_progress - datamine_progress[i]
                new_offset = max(0, progress_difference)  # Never negative
                
                # Check if we should allow this offset (backwards movement protection)
                current_offset = self.datamine_current_offsets[i]
                
                # Allow the new offset if:
                # 1. We explicitly allow backwards movement, OR
                # 2. The sequence restarted (current progress < previous progress), OR  
                # 3. The new offset doesn't move backwards (new_offset >= current_offset)
                sequence_restarted = datamine_completed[i] < self.datamine_completed_before[i]
                
                if allow_backwards or sequence_restarted or new_offset >= current_offset:
                    target_offsets.append(new_offset)
                else:
                    # Don't move backwards, keep current offset
                    target_offsets.append(current_offset)
        
        return target_offsets

    def get_datamine_border_color(self, upper_datamine_idx, lower_datamine_idx):
        """
        Get the appropriate border color between two datamines.
        Colors depend on the status of the neighboring datamines.
        """
        upper_completed = self.completed_datamines[upper_datamine_idx] if not upper_datamine_idx == None else False # enable passing None and therefore default color combination
        upper_failed = self.failed_datamines[upper_datamine_idx] if not upper_datamine_idx == None else False
        lower_completed = self.completed_datamines[lower_datamine_idx] if not lower_datamine_idx == None else False
        lower_failed = self.failed_datamines[lower_datamine_idx] if not lower_datamine_idx == None else False

        # Determine border color based on neighboring datamine states
        if upper_completed and lower_completed:
            return 227  # Green-Green (both completed) - success_green on success_green
        elif upper_failed and lower_failed:
            return 228  # Red-Red (both failed) - failed_red on failed_red
        elif upper_completed and lower_failed:
            return 229  # Green-Red (completed above, failed below)
        elif upper_failed and lower_completed:
            return 230  # Red-Green (failed above, completed below)
        elif upper_completed and not (lower_completed or lower_failed):
            return 231  # Green-Default (completed above, normal below)
        elif upper_failed and not (lower_completed or lower_failed):
            return 232  # Red-Default (failed above, normal below)
        elif lower_completed and not (upper_completed or upper_failed):
            return 233  # Green-Default (normal above, completed below)
        elif lower_failed and not (upper_completed or upper_failed):
            return 234  # Red-Default (normal above, failed below)
        else:
            return None  # No border needed (both normal)

    def draw_fat_datamine_block(self, stdscr, i, is_completed, is_failed):
        """
        Draw the thick block-style datamine completion/failure display.
        Progress goes from 0.0 to 1.0 for top-to-bottom animation.
        """
        y_base = 7 + i * 2
        
        # Main content row
        arrow = "∇" * (i + 1)
        if is_completed:
            content = f"  INSTALLED                {arrow:>3} DATAMINE_V{i+1}  "
            content_color = 235
        elif is_failed:
            content = f"  FAILED                   {arrow:>3} DATAMINE_V{i+1}  "
            content_color = 236
        else:
            content = f"                             {arrow:>3} DATAMINE_V{i+1}  "
            content_color = 255
        
        stdscr.addstr(y_base, 41, content, curses.color_pair(content_color))
        
        # Border between datamines (▀ characters) - calculate colors first
        upper_border_color = None
        lower_border_color = None
        
        # Determine border colors based on adjacent datamine states
        if not i == 0: # First datamine needs special handling for upper border
            upper_border_color = self.get_datamine_border_color(i - 1, i)
        elif i == 0:
            upper_border_color = self.get_datamine_border_color(None, i)
        
        if not i == 2: # Last datamine needs special handling for lower border
            lower_border_color = self.get_datamine_border_color(i, i + 1)
        elif i == 2:
            lower_border_color = self.get_datamine_border_color(i, None)
            
        # Draw both borders immediately after calculation
        if upper_border_color:
            stdscr.addstr(y_base - 1, 41, "▀" * 44, curses.color_pair(upper_border_color))
        if lower_border_color:
            stdscr.addstr(y_base + 1, 41, "▀" * 44, curses.color_pair(lower_border_color))
        
        stdscr.refresh()  # Force immediate display of borders

    def main(self, stdscr):
        stdscr.clear()

        curses.curs_set(0)
        self.color_init(stdscr)

        # Check minimum screen size
        max_y, max_x = stdscr.getmaxyx()
        if max_y < 19 or max_x < 85:
            stdscr.addstr(0, 0, "Screen size too small. Minimum size is 19 rows and 85 columns.", curses.color_pair(1))
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

            # Handle ESC key during gameplay
            if key == 27:  # ESC key
                return False  # Signal to quit immediately

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

        if False:  # collapsable inactive debug block; change to True for debug display
            stdscr.addstr(4, 1,  "▄", curses.color_pair(231))
            stdscr.addstr(4, 2,  "▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀█", curses.color_pair(224))
            stdscr.addstr(5, 1,  "▏ //ROOT                             ▕", curses.color_pair(224))
            stdscr.addstr(6, 1,  "▏ //ACCESS_REQUEST                   ▕", curses.color_pair(224))
            stdscr.addstr(7, 1,  "▏ //ACCESS_REQUEST_SUCCESS           ▕", curses.color_pair(224))
            stdscr.addstr(8, 1,  "▏ //COLLECTING PACKET_1.....COMPLETE ▕", curses.color_pair(224))
            stdscr.addstr(9, 1,  "▏ //COLLECTING PACKET_2.....COMPLETE ▕", curses.color_pair(224))
            stdscr.addstr(10, 1, "▏ //COLLECTING PACKET_3.....COMPLETE ▕", curses.color_pair(224))
            stdscr.addstr(11, 1, "▏ //COLLECTING PACKET_4.....COMPLETE ▕", curses.color_pair(224))
            stdscr.addstr(12, 1, "▏ //LOGIN                            ▕", curses.color_pair(224))
            stdscr.addstr(13, 1, "▏ //LOGIN_SUCCESS                    ▕", curses.color_pair(224))
            stdscr.addstr(14, 1, "▏ //                                 ▕", curses.color_pair(224))
            stdscr.addstr(15, 1, "▏ //UPLOAD_IN_PROGRESS               ▕", curses.color_pair(224))
            stdscr.addstr(16, 1, "▏ //UPLOAD_COMPLETE!                 ▕", curses.color_pair(224))
            stdscr.addstr(17, 1, "█▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█", curses.color_pair(224))
            stdscr.addstr(18, 1, "           DAEMONS UPLOADED           ", curses.color_pair(235))
            stdscr.addstr(19, 1, "▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀", curses.color_pair(224))
            
            stdscr.addstr(4, 1,  "▄", curses.color_pair(232))
            stdscr.addstr(4, 2,  "▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀█", curses.color_pair(223))
            stdscr.addstr(5, 1,  "▏ //ROOT_ATTEMPT_1                   ▕", curses.color_pair(223))
            stdscr.addstr(6, 1,  "▏ //ROOT_ATTEMPT_2                   ▕", curses.color_pair(223))
            stdscr.addstr(7, 1,  "▏ //ROOT_ATTEMPT_3                   ▕", curses.color_pair(223))
            stdscr.addstr(8, 1,  "▏ //ROOT_FAILED                      ▕", curses.color_pair(223))
            stdscr.addstr(9, 1,  "▏ //ROOT_REBOOT                      ▕", curses.color_pair(223))
            stdscr.addstr(10, 1, "▏ //ACCESSING.................FAILED ▕", curses.color_pair(223))
            stdscr.addstr(11, 1, "▏ //ACCESSING.................FAILED ▕", curses.color_pair(223))
            stdscr.addstr(12, 1, "▏ //ACCESSING.................FAILED ▕", curses.color_pair(223))
            stdscr.addstr(13, 1, "▏ //ACCESSING.................FAILED ▕", curses.color_pair(223))
            stdscr.addstr(14, 1, "▏                                    ▕", curses.color_pair(223))
            stdscr.addstr(15, 1, "▏                                    ▕", curses.color_pair(223))
            stdscr.addstr(16, 1, "▏                                    ▕", curses.color_pair(223))
            stdscr.addstr(17, 1, "█▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█", curses.color_pair(223))
            stdscr.addstr(18, 1, "             BUFFER FULL              ", curses.color_pair(236))
            stdscr.addstr(19, 1, "▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀", curses.color_pair(223))
            
            stdscr.refresh()
        
        text_matrixes = [
        [
            ["//ROOT"],
            ["//ACCESS_REQUEST"],
            ["//ACCESS_REQUEST_SUCCESS"],
            ["//COLLECTING PACKET_1.....COMPLETE"],
            ["//COLLECTING PACKET_2.....COMPLETE"],
            ["//COLLECTING PACKET_3.....COMPLETE"],
            ["//COLLECTING PACKET_4.....COMPLETE"],
            ["//LOGIN"],
            ["//LOGIN_SUCCESS"],
            ["//"],
            ["//UPLOAD_IN_PROGRESS"],
            ["//UPLOAD_COMPLETE!"],
            ["DAEMONS UPLOADED"]
        ],
        [
            ["//ROOT_ATTEMPT_1"],
            ["//ROOT_ATTEMPT_2"],
            ["//ROOT_ATTEMPT_3"],
            ["//ROOT_FAILED"],
            ["//ROOT_REBOOT"],
            ["//ACCESSING.................FAILED"],
            ["//ACCESSING.................FAILED"],
            ["//ACCESSING.................FAILED"],
            ["//ACCESSING.................FAILED"],
            ["BUFFER FULL"]
        ]
        ]

        if any(self.completed_datamines):
            main_color = 224
            weird_bit_color = 231
            lower_text_color = 235
        else:
            main_color = 223
            weird_bit_color = 232
            lower_text_color = 236
        
        stdscr.addstr(4, 1,  "▄", curses.color_pair(weird_bit_color))
        stdscr.addstr(4, 2,  "▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀█", curses.color_pair(main_color))
        stdscr.addstr(5, 1,  "▏                                    ▕", curses.color_pair(main_color))
        stdscr.addstr(6, 1,  "▏                                    ▕", curses.color_pair(main_color))
        stdscr.addstr(7, 1,  "▏                                    ▕", curses.color_pair(main_color))
        stdscr.addstr(8, 1,  "▏                                    ▕", curses.color_pair(main_color))
        stdscr.addstr(9, 1,  "▏                                    ▕", curses.color_pair(main_color))
        stdscr.addstr(10, 1, "▏                                    ▕", curses.color_pair(main_color))
        stdscr.addstr(11, 1, "▏                                    ▕", curses.color_pair(main_color))
        stdscr.addstr(12, 1, "▏                                    ▕", curses.color_pair(main_color))
        stdscr.addstr(13, 1, "▏                                    ▕", curses.color_pair(main_color))
        stdscr.addstr(14, 1, "▏                                    ▕", curses.color_pair(main_color))
        stdscr.addstr(15, 1, "▏                                    ▕", curses.color_pair(main_color))
        stdscr.addstr(16, 1, "▏                                    ▕", curses.color_pair(main_color))
        stdscr.addstr(17, 1, "█▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█", curses.color_pair(main_color))
        stdscr.addstr(18, 1, "                                      ", curses.color_pair(lower_text_color))
        stdscr.addstr(19, 1, "▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀", curses.color_pair(weird_bit_color))
        
        stdscr.refresh()
        
        text_matrix = text_matrixes[0 if any(self.completed_datamines) else 1]
        lower_text_len = len(text_matrix[-1][0])  # Access the string inside the nested list
        total_space_available = 38
        lower_text_offset = (total_space_available - lower_text_len) // 2
        
        for i, line in enumerate(text_matrix):
            split_line = [*line[0]]

            for j, char in enumerate(split_line):
                if i < len(text_matrix) - 1:
                    stdscr.addstr(5 + i, j + 3, char, curses.color_pair(main_color))
                else:
                    stdscr.addstr(18, j + lower_text_offset, char, curses.color_pair(lower_text_color))
                stdscr.refresh()
                time.sleep(0.025)

        stdscr.refresh()
        
        # Auto-restart countdown with manual override
        countdown_time = 5.0
        start_countdown = time.time()
        stdscr.nodelay(True)  # Non-blocking input for countdown
        
        while True:
            elapsed = time.time() - start_countdown
            remaining = countdown_time - elapsed
            
            if remaining <= 0:
                return True  # Auto-restart after countdown
            
            # Display countdown message
            stdscr.addstr(0, 42, f"Restarting in {remaining:.1f}s - Press any key to restart now, ESC to quit", curses.color_pair(255))
            stdscr.refresh()
            
            key = stdscr.getch()
            if key == 27:  # ESC key
                return False  # Signal to quit
            elif key != -1:  # Any other key pressed
                return True   # Signal to restart immediately
            
            time.sleep(0.1)  # Small delay to avoid excessive CPU usage
    
if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, "en_GB.UTF-8")

    # --- Cross-platform console window detection and setup ---
    def should_set_console_title_and_size():
        # Windows-specific: check for real console window
        if os.name == "nt":
            try:
                import ctypes
                GetConsoleWindow = ctypes.windll.kernel32.GetConsoleWindow
                GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId
                hwnd = GetConsoleWindow()
                if hwnd:
                    import os as _os
                    pid = ctypes.c_ulong()
                    GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                    if pid.value == _os.getpid():
                        return True  # Real, own console window
            except Exception:
                pass
            # Fallback: check for classic terminal via env vars
            env = os.environ
            if (
                sys.stdout.isatty() and
                'WT_SESSION' not in env and
                'TERM_PROGRAM' not in env and
                'VSCODE_PID' not in env
            ):
                return True
            return False
        else:
            # On Linux/Mac: avoid VS Code/modern terminals
            env = os.environ
            if (
                sys.stdout.isatty() and
                'WT_SESSION' not in env and
                'TERM_PROGRAM' not in env and
                'VSCODE_PID' not in env
            ):
                return True
            return False

    if should_set_console_title_and_size():
        if os.name == "nt":
            os.system('title Breach Protocol')
            os.system('mode con: cols=90 lines=20')
        else:
            # On Linux/Mac, optionally set terminal title (if supported)
            sys.stdout.write("\x1b]2;Breach Protocol\x07")
            sys.stdout.flush()
        
    game_instance = Game()
    while True:
        try:
            should_continue = curses.wrapper(game_instance.main)
            if not should_continue:
                break  # User pressed ESC to quit
            game_instance.reset_game()  # Reset for next round
        except KeyboardInterrupt:
            break  # Allow Ctrl+C to quit