# Entry point for user input
# Events are bound in graphics intialization to user_input instance
# Events are coerced into a usable form and passed into
# user_input.user_key_pressed
#
# parsed commands are passed in list form over to interaction_manager.py
# the interaction_manager should not have to handle raw user input

import re
from copy import deepcopy
from Backend.State import instance
from Backend import command_list
from Backend import command_parser
from Backend import interaction_manager

DEFAULT_MOVEMENTS = command_list.DEFAULT_MOVEMENTS
DEFAULT_COMMAND_LEADERS = command_list.DEFAULT_COMMAND_LEADERS
VISUAL_MOVEMENTS = command_list.VISUAL_MOVEMENTS
BREAK_MOVEMENTS = command_list.BREAK_MOVEMENTS
COMMAND_MAP = command_list.COMMAND_MAP


class user_input():

    def __init__(self):
        self._graphics = None
        self.curr_state, self.command_buffer = 'Default', ''
        self.instances, self.copy_buffer, self.curr_instance = [], [], 0

    def start_instance(self, filename):
        self.instances.append(instance.instance(filename))

    def set_GUI_reference(self, canvas):
        """
        Set graphics reference for particular instance and render page
        This should really only be done once per instace
        """
        self._graphics = canvas
        self.instances[self.curr_instance].set_line_height(
            self._graphics.line_height)
        interaction_manager.render_page(
            [], [], self._graphics,
            self.get_curr_instance(), self)

    def add_copy_buffer(self, l):
        self.copy_buffer = l

    def get_curr_instance(self):
        return self.instances[self.curr_instance]

    def get_copy_buffer(self):
        return self.copy_buffer

    def go_next_instance(self):
        """
        Go to next instance if there is one available
        """
        if self.curr_instance < len(self.instances) - 1:
            self.curr_instance += 1
            self.set_GUI_reference(self._graphics)

    def go_prev_instance(self):
        """
        Go to previous instance if there is one available
        """
        if self.curr_instance > 0:
            self.curr_instance -= 1
            self.set_GUI_reference(self._graphics)

    def is_digit(self, k):
        """
        checks if key input an integer greater than 0 and less than 10
        """
        return (len(k) == 1) and (ord(k) >= 49 and ord(k) <= 57)

    def key(self, event):
        key = event.keysym
        if key != '??':
            if len(key) > 1:  # length > 1 if not alphanumeric
                try:
                    k = COMMAND_MAP[key]
                    self.user_key_pressed(k)
                except KeyError:
                    pass
            else:
                self.user_key_pressed(key)

    def control_a(self, event):
        self.user_key_pressed('<Control-a>')

    def control_b(self, event):
        self.user_key_pressed('<Control-b>')

    def control_c(self, event):
        self.user_key_pressed('<Control-c>')

    def control_d(self, event):
        self.user_key_pressed('<Control-d>')

    def control_e(self, event):
        self.user_key_pressed('<Control-e>')

    def control_f(self, event):
        self.user_key_pressed('<Control-f>')

    def control_g(self, event):
        self.user_key_pressed('<Control-g>')

    def control_h(self, event):
        self.user_key_pressed('<Control-h>')

    def control_i(self, event):
        self.user_key_pressed('<Control-i>')

    def control_j(self, event):
        self.user_key_pressed('<Control-j>')

    def control_k(self, event):
        self.user_key_pressed('<Control-k>')

    def control_l(self, event):
        self.user_key_pressed('<Control-l>')

    def control_m(self, event):
        self.user_key_pressed('<Control-m>')

    def control_n(self, event):
        self.user_key_pressed('<Control-n>')

    def control_o(self, event):
        self.user_key_pressed('<Control-o>')

    def control_p(self, event):
        self.user_key_pressed('<Control-p>')

    def control_q(self, event):
        self.user_key_pressed('<Control-q>')

    def control_r(self, event):
        self.user_key_pressed('<Control-r>')

    def control_s(self, event):
        self.user_key_pressed('<Control-s>')

    def control_t(self, event):
        self.user_key_pressed('<Control-t>')

    def control_u(self, event):
        self.user_key_pressed('<Control-u>')

    def control_v(self, event):
        self.user_key_pressed('<Control-v>')

    def control_w(self, event):
        self.user_key_pressed('<Control-w>')

    def control_x(self, event):
        self.user_key_pressed('<Control-x>')

    def control_y(self, event):
        self.user_key_pressed('<Control-y>')

    def control_z(self, event):
        self.user_key_pressed('<Control-z>')

    def control_braceright(self, event):
        self.user_key_pressed('<Control-braceright>')

    def control_braceleft(self, event):
        self.user_key_pressed('<Control-braceleft>')

    def escape(self, event):
        self.curr_state = 'Default'
        self.command_buffer = ''
        interaction_manager.render_page(
            [], [], self._graphics, self.instances[self.curr_instance], self)

    def mouse_scroll(self, event):
        """
        Scroll mouse depending on direction moved by
        calling cursor up or cursor down repeatedly.
        TODO: This is clearly not optimal. The calling
        move_cursor_up or down re-renders the page repeatedly and
        is inefficient
        """
        delta = event.delta * -1
        self.curr_state = 'Default'
        self.command_buffer = ''
        cmd = ['n' + str(delta), 'mouse_scroll']
        interaction_manager.input_command(
            cmd, self._graphics, self.get_curr_instance(), None)

    def user_key_pressed(self, key):
        """
        Main input router. Routes key input to appropriate
        key handlers dependent upon global state
        """
        if self.curr_state == 'Default':
            self.user_key_default(key)
        elif self.curr_state == 'Insert':
            self.user_key_insert(key)
        elif self.curr_state == 'Visual':
            self.user_key_visual(key)
        elif self.curr_state == 'Ex':
            self.user_key_ex(key)
        elif self.curr_state == 'fuzzy_file_selection':
            self.user_key_fuzzy_file_select(key)

    def init_insert_mode(self):
        self.curr_state = 'Insert'

    def init_ex_mode(self):
        self.curr_state = 'Ex'

    def init_visual_mode(self):
        curr_instance = self.get_curr_instance()
        # set once and then never mutate this ever again per visual selection
        self.get_curr_instance().set_visual_anchor()
        self.curr_state = 'Visual'

    def user_key_default(self, key):
        """
        Handle keys in default mode
        """
        mode_dict = {
            'i': self.init_insert_mode,
            'v': self.init_visual_mode,
            ':': self.init_ex_mode,
        }

        if key in DEFAULT_COMMAND_LEADERS \
            or self.is_digit(key) \
                or len(self.command_buffer):
            self.command_buffer += key
            s_par = command_parser.default_parse(self.command_buffer)

            if s_par != '' or key in BREAK_MOVEMENTS:
                cmd = s_par if s_par != '' else BREAK_MOVEMENTS[key]
                interaction_manager.input_command(
                    cmd, self._graphics, self.get_curr_instance(), self)
                self.command_buffer = ''

        elif key in DEFAULT_MOVEMENTS:  # default movement requested
            interaction_manager.input_command(
                DEFAULT_MOVEMENTS[key], self._graphics,
                self.get_curr_instance(), self
            )
            self.command_buffer = ''
        elif key in mode_dict:  # mode change requested
            mode_dict[key]()

    def user_key_insert(self, key):
        """
        Handle keys in insert mode

        This should be the only state that should contain
        at least these mappings no matter the configuration
        """
        if key not in ['BackSpace', 'Return']:
            cmd = ['s' + key, 'insert_text']
            interaction_manager.input_command(
                cmd, self._graphics,
                self.get_curr_instance(), self
            )
        elif key == 'BackSpace':
            interaction_manager.input_command(
                ['delete_char'], self._graphics,
                self.get_curr_instance(), self
            )
        # similar to above
        elif key == 'Return':
            interaction_manager.input_command(
                ['add_new_line'], self._graphics,
                self.get_curr_instance(), self
            )

    def user_key_visual(self, key):
        """
        Handle keys in visual mode
        TODO: expand this section to handle multi command
        arguments
        i.e finds should work in visual mode
        Dependent upon a proper command parser however
        """
        if key in VISUAL_MOVEMENTS:
            motion = VISUAL_MOVEMENTS[key]
            cmd = ['s' + motion[0], 'visual_movement']
            interaction_manager.input_command(
                cmd, self._graphics,
                self.get_curr_instance(), self
            )
            self.command_buffer = ''

    def user_key_ex(self, key):
        """
        Handle keys in ex mode
        TODO: expand this section to handle multi command
        arguments
        i.e finds should work in visual mode
        Dependent upon a proper command parser however

        This mode is kind of limited for now since we don't
        have a proper command parser yet
        """
        if key == 'Return':
            cmd = command_parser.ex_parse(self.command_buffer)
            interaction_manager.input_command(
                cmd, self._graphics,
                self.get_curr_instance(), self
            )
            self.curr_state = 'Default'
            self.command_buffer = ''
        elif key == 'BackSpace':
            self.command_buffer = self.command_buffer[:-1]
        else:
            self.command_buffer += key
