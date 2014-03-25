import interaction_manager, command_list, command_parser
from copy import deepcopy
from State import instance
import re

DEFAULT_MOVEMENTS = command_list.DEFAULT_MOVEMENTS
VISUAL_MOVEMENTS = command_list.VISUAL_MOVEMENTS
BREAK_MOVEMENTS = command_list.BREAK_MOVEMENTS
COMMAND_MAP = command_list.COMMAND_MAP

# parses keyboard input for meaningful instructions
# sends "completed" instructions to interaction_manager router
class user_input():
    def __init__(self):
        self.graphics = None
        self.curr_state, self.command_buffer = 'Default', ''
        self.instances, self.curr_instance = [], 0
        self.undo_buffer, self.copy_buffer, self.undo_index = [], [], 0

    def start_instance(self, filename):
        self.instances.append(instance.instance(filename))

    def set_GUI_reference(self, canvas):
        self.graphics = canvas
        self.instances[self.curr_instance].set_line_height(self.graphics.line_height)
        interaction_manager.render_page([], [], self.graphics, self.instances[self.curr_instance], self)

    def add_copy_buffer(self, l):
        self.copy_buffer = l

    def add_undo_buffer(self):
        inst = self.get_curr_instance()
        x, y, curr_top = inst.get_page_state()
        lines = deepcopy(inst.get_lines())
        line_tokens = deepcopy(inst.get_line_tokens())
        self.undo_buffer.append( { 'x': x, 'y': y, 'curr_top': curr_top, 'lines': lines, 'line_tokens': line_tokens })
        self.undo_index += 1

    def get_undo_state(self):
        if self.undo_buffer >= 0:
            self.undo_index -= 1
            return self.undo_buffer[self.undo_index]
        else:
            return None

    def get_curr_instance(self):
        return self.instances[self.curr_instance]

    def get_copy_buffer(self):
        return self.copy_buffer

    # checks if key input an integer greater than 0 and less than 10
    def is_digit(self, k):
        return (len(k) == 1) and (ord(k) >= 49 and ord(k) <= 57)

    def key(self, event):
        # if key is not in [a-zA-Z0-9] length of keysym will be greater than one
        key = event.keysym
        if key != '??':
            if len(key) > 1:
                try:
                    k = COMMAND_MAP[key]
                    self.user_key_pressed(k)
                except KeyError:
                    pass
            else:
                self.user_key_pressed(key)

    def control_f(self, event):
        # drop on floor for now
        a = 1

    def control_b(self, event):
        # drop on floor for now
        a = 1
    def control_p(self, event):
        if self.curr_state != 'fuzzy_file_selection':
            self.curr_state = 'fuzzy_file_selection'
            self.command_buffer = ''
            self.get_curr_instance().set_visual_anchor(y=2)
            cmd = 's' + self.command_buffer + ':' + 'fuzzy_file_select'
            interaction_manager.input_command(cmd, self.graphics, self.get_curr_instance(), self)

    def escape(self, event):
        self.curr_state = 'Default'
        self.command_buffer = ''
        interaction_manager.render_page([], [], self.graphics, self.instances[self.curr_instance], self)

    # TODO: THIS LOOKS HACKY
    def mouse_scroll(self, event):
        # run up or down command depending on scroll direction
        delta = event.delta * -1
        self.curr_state = 'Default'
        self.command_buffer = ''
        cmd = 'n' + str(delta) + ':mouse_scroll'
        interaction_manager.input_command(cmd, self.graphics, self.get_curr_instance(), None)

    def user_key_pressed(self, key):
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


    # TODO: CLEAN UP THIS MESS
    def user_key_default(self, key):
        # To be buffered
        if key in ['g', 'f', 'd', 'y'] or self.is_digit(key) or len(self.command_buffer):
            self.command_buffer += key
            s_par = command_parser.default_parse(self.command_buffer)

            if s_par != '':
                interaction_manager.input_command(s_par, self.graphics, self.get_curr_instance(), self)
                self.command_buffer = ''
            elif BREAK_MOVEMENTS.has_key(key):
                interaction_manager.input_command(BREAK_MOVEMENTS[key], self.graphics, self.get_curr_instance(), self)
                self.command_buffer = ''

        # default movement requested
        elif DEFAULT_MOVEMENTS.has_key(key):
            interaction_manager.input_command(DEFAULT_MOVEMENTS[key], self.graphics, self.get_curr_instance(), self)
            self.command_buffer = ''

        # this could be a dict, or it could be a bunch of if elses. If elses are slightly more intuitive than the other.
        elif key == 'i':
            self.curr_state = 'Insert'
        elif key == 'v':
            curr_instance = self.get_curr_instance()
            # set once and then never mutate this ever again per visual selection
            self.get_curr_instance().set_visual_anchor()
            self.curr_state = 'Visual'
        elif key == ':':
            self.curr_state = 'Ex'

    # this should be the only state that doesn't change no matter the configuration
    def user_key_insert(self, key):
        if not key in ['BackSpace', 'Return']:
            cmd = 's' + key + ':' + 'insert_text'
            interaction_manager.input_command(cmd, self.graphics, self.get_curr_instance(), self)
        # one of the only few scenarios where the command is the same no matter the configuration?
        elif key == 'BackSpace':
            interaction_manager.input_command('delete_char', self.graphics, self.get_curr_instance(), self)
        # similar to above
        elif key == 'Return':
            interaction_manager.input_command('add_new_line', self.graphics, self.get_curr_instance(), self)

    def user_key_visual(self, key):
        if VISUAL_MOVEMENTS.has_key(key):
            motion = VISUAL_MOVEMENTS[key]
            cmd = 's' + motion + ':visual_movement'
            interaction_manager.input_command(cmd, self.graphics, self.get_curr_instance(), self)
            self.command_buffer = ''

    def user_key_ex(self, key):
        if key == 'Return':
            cmd = command_parser.ex_parse(self.command_buffer)
            interaction_manager.input_command(cmd, self.graphics, self.get_curr_instance(), self)
            self.curr_state = 'Default'
            self.command_buffer = ''
        elif key == 'BackSpace':
            self.command_buffer = self.command_buffer[:-1]
        else:
            self.command_buffer += key

    def user_key_fuzzy_file_select(self, key):
        if key == 'Return':
            self.command_buffer = ''
            self.curr_state = 'Default'
        elif key == 'BackSpace':
            self.command_buffer = self.command_buffer[:-1]
            cmd = 's' + self.command_buffer + ':' + 'fuzzy_file_select'
            interaction_manager.input_command(cmd, self.graphics, self.get_curr_instance(), self)
        elif key == '<Up>' or key == '<Down>':
            inst = self.get_curr_instance()
            _, vy, _ = inst.get_visual_anchors()
            vy = vy + 1 if key == '<Down>' else vy - 1
            vy = min(21, max(vy, 2))
            inst.set_visual_anchor(y=vy)
            cmd = 's' + self.command_buffer + ':' + 'fuzzy_file_select'
            interaction_manager.input_command(cmd, self.graphics, self.get_curr_instance(), self)
        else:
            self.command_buffer += key
            cmd = 's' + self.command_buffer + ':' + 'fuzzy_file_select'
            interaction_manager.input_command(cmd, self.graphics, self.get_curr_instance(), self)