# pylint: disable=no-member

import pygame
import pieces as pieces_lib
import math
import time
import sys
from random import shuffle, randint
import network
import json
import pyperclip
from oooooooooooooooooooooooooooooooooooooooooooootils import darken, lighten


from pieces import preview_piece


color_key = {
    'green': (13, 252, 65),
    'blue': (13, 29, 252),
    'teal': (15, 246, 250),
    'red': (250, 15, 15),
    'orange': (255, 128, 43),
    'purple': (168, 24, 245),
    'yellow': (255, 223, 13),
    'gray': (107, 115, 120)
}


class Game:

    def __init__(self):

        # self.volume = 0.05
        # self.lowered_volume = 0.015
        self.volume = 0
        self.lowered_volume = 0

        pygame.init()
        self.font = pygame.font.Font('assets/arial.ttf', 32)

        pygame.mixer.music.load('assets/background_audio.wav')
        #NOTE set volume to 0.15 in final version
        pygame.mixer.music.set_volume(self.lowered_volume)
        pygame.mixer.music.play(-1)


        self.correct_rotateSFX = pygame.mixer.Sound('assets/move_effect_success.wav')
        self.holdSFX = pygame.mixer.Sound('assets/hold_effect.wav')
        self.row_clearedSFX = pygame.mixer.Sound('assets/row_cleared.wav')
        self.row_clearedSFX.set_volume(0.5)
        

        self.width = 750
        self.height = 800
        self.background_color = (0, 20, 39)
        self.foreground_color = (101, 142, 156)


        self.running = True
        self.muted = False

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.width, self.height))

        self.icon = pygame.image.load('./assets/tetris.jpg')
        pygame.display.set_icon(self.icon)

        self.caption = "Tetrium"
        pygame.display.set_caption(self.caption)

        # 30px x 30px is one block

        self.resting = []
        self.last_time = 0
    

        self.continuous = True


        self.level = 1
        self.score = 0
        self.lines = 0


        self.time_started = 0


        # list of numbers, with numbers being attack amounts
        self.meter = []
        self.meter_stage = 1
 

        self.opp_resting = self.opp_meter = self.opp_meter_stage = self.opp_piece_blocks = None
        self.opp_name = None

        self.rows_cleared = []

        self.small_font = pygame.font.Font('assets/arial.ttf', 15)
        self.medium_font = pygame.font.Font('assets/arial.ttf', 20)
        self.big_font = pygame.font.Font('assets/arial.ttf', 30)
        self.very_big_font = pygame.font.Font('assets/arial.ttf', 75)
        self.back_icon = pygame.image.load('assets/arrow-back.png')
        self.back_button = pygame.Rect(10, 10, 75, 65)


        self.default_controls = {
            "Move Right": "d",
            "Move Left": "a",
            "Soft Drop": "s",
            "Hard Drop": "down",
            "Hold Piece": "up",
            "Rotate Clockwise": "right",
            "Rotate Counter-Clockwise": "left",
            "Toggle Movement": "g",
            "Toggle Music": "m"
        }


        # setting controls
        with open('controls.json') as f:
            temp = json.load(f)
       
        self.left_controls = {
            "Move Left": temp["Move Left"],
            "Move Right": temp["Move Right"],
            "Soft Drop": temp["Soft Drop"],
            "Toggle Movement": temp["Toggle Movement"],
            "Toggle Music": temp["Toggle Music"]
        }

        self.right_controls = {
            "Rotate Clockwise": temp["Rotate Clockwise"],
            "Rotate Counter-Clockwise": temp["Rotate Counter-Clockwise"],
            "Hold Piece": temp["Hold Piece"],
            "Hard Drop": temp["Hard Drop"]
        }
      



    def render(self, pieces=None, held=None):
        
        self.screen.fill(self.background_color)
        pygame.draw.rect(self.screen, self.foreground_color, (100, 100, 300, 600))

        for block in self.resting:
            block.render()

        # for piece order
        for x in range(1, 4):
            pygame.draw.circle(self.screen, self.foreground_color, (450, 130*x), 40)

        text = self.font.render('Next', True, (255, 255 ,255))
        textRect = text.get_rect()
        textRect.center = (450, 60)
        self.screen.blit(text, textRect)

        # putting pieces in the circles
        if pieces:
            position = 1
            
            for piece in pieces:
                for color, x, y, width, height in pieces_lib.preview_piece(450, position*130, piece):
                    pygame.draw.rect(self.screen, color_key[color], (x, y, width, height))
                
                position += 1
    
        # for hold area
        pygame.draw.circle(self.screen, self.foreground_color, (50, 130), 40)
        text = self.font.render('Hold', True, (255, 255 ,255))
        textRect = text.get_rect()
        textRect.center = (50, 60)
        self.screen.blit(text, textRect)

        if held:
            for color, x, y, width, height in pieces_lib.preview_piece(50, 130, held):
                pygame.draw.rect(self.screen, color_key[color], (x, y, width, height))


        # for continuous movement indication
        if self.continuous: text = "On"
        else: text = "Off"

        text = self.font.render(f"Continuous Movement: {text}", True, (255, 255 ,255))
        textRect = text.get_rect()
        textRect.center = (300, 780)
        self.screen.blit(text, textRect)

        self.score = int(self.score)
        text = self.font.render(f"Score: {self.score}", True, (255, 255 ,255))
        textRect = text.get_rect()
        textRect.center = (250, 725)
        self.screen.blit(text, textRect)

        font = pygame.font.Font('assets/arial.ttf', 25)

        text = font.render(f"Level: {self.level}", True, (255, 255 ,255))
        textRect = text.get_rect()
        textRect.center = (420, 725)
        self.screen.blit(text, textRect)

        text = font.render(f"Lines: {self.lines}", True, (255, 255 ,255))
        textRect = text.get_rect()
        textRect.center = (75, 725)
        self.screen.blit(text, textRect)

        font = pygame.font.Font('assets/arial.ttf', 20)

        time_elapsed = math.floor(time.time() - self.time_started)

        minutes = time_elapsed // 60
        remaining_seconds = time_elapsed % 60

        time_elapsed = f"{minutes}m {remaining_seconds}s"

        text = font.render(f"Time Elapsed: {time_elapsed}", True, (255, 255 ,255))
        textRect = text.get_rect()
        textRect.center = (250, 25)
        self.screen.blit(text, textRect)


        text = font.render(self.name, True, (255, 255 ,255))
        textRect = text.get_rect()
        textRect.center = (250, 65)
        self.screen.blit(text, textRect)


        text = font.render(self.opp_name, True, (255, 255 ,255))
        textRect = text.get_rect()
        textRect.center = (650, 230)
        self.screen.blit(text, textRect)


        # junk line meter
        pygame.draw.rect(self.screen, (255, 255, 255), (32, 394, 36, 306))
        pygame.draw.rect(self.screen, self.foreground_color, (35, 397, 30, 300))

        meter_block = 0

        for index, amount in enumerate(self.meter):

            if not index and self.meter_stage != 4:
                if self.meter_stage == 1:
                    color = color_key["yellow"]
                elif self.meter_stage  == 2:
                    color = color_key["orange"]
                elif self.meter_stage  == 3:
                    color = color_key["red"]
            else:
                color = color_key["gray"]

            darkened = (tuple(darken(color) for color in color))

            for block in range(amount):

                if meter_block >= 10:
                    break
                pygame.draw.rect(self.screen, darkened, (35, 667 - (30 * meter_block), 30, 30))
                pygame.draw.rect(self.screen, color, (40, 672 - (30 * meter_block), 20, 20))
                meter_block += 1

        
        self.render_second_screen()


    def render_second_screen(self):
        pygame.draw.rect(self.screen, self.foreground_color, (570, 250, 150, 300))

        if self.time_started + 1 > time.time():
            return
        
        for x, y, color in self.opp_resting: # noqa pylint: disable=not-an-iterable
            Block(x, y, color, colorByName=False).render_second()

        
        if self.opp_piece_blocks:
            for x, y, color in self.opp_piece_blocks: # noqa pylint: disable=not-an-iterable
                Block(x, y, color, colorByName = False).render_second()
        
        # junk line meter
        pygame.draw.rect(self.screen, (255, 255, 255), (539, 398, 17, 152))
        pygame.draw.rect(self.screen, self.foreground_color, (540, 399, 15, 150))


        meter_block = 0
        for index, amount in enumerate(self.opp_meter):

            if not index:
                if self.opp_meter_stage == 1:
                    color = color_key["yellow"]
                elif self.opp_meter_stage  == 2:
                    color = color_key["orange"]
                elif self.opp_meter_stage  == 3:
                    color = color_key["red"]
            else:
                color = color_key["gray"]

            darkened = (tuple(darken(color) for color in color))

            for _ in range(amount):

                if meter_block >= 10:
                    break

                pygame.draw.rect(self.screen, darkened, (540, 534 - (15 * meter_block), 15, 15))
                pygame.draw.rect(self.screen, color, (542, 536 - (15 * meter_block), 11, 11)) #type: ignore
                meter_block += 1

        if int(time.time()) % 2:
            self.width += 1
            pygame.display.set_mode((self.width, self.height))

    def draw_back_button(self, pos = (-10, -10)):
        white = (255, 255, 255)
        color = tuple(map(darken, white)) if self.back_button.collidepoint(pos) else white
        pygame.draw.rect(self.screen, color, self.back_button)
        self.screen.blit(self.back_icon, (-3, -7))


    def draw_controls(self, controls, pos, color, keys_bkg_color = (0, 0, 0), underline = False, clicked_index = -1):
    
        replace_keys = {
            'left click': 'lmb',
            'middle click': 'mmb',
            'right click': 'rmb',
            'up': '↑',
            'down': '↓',
            'right': '→',
            'left': '←',
            'left shift': 'lshft',
            'right shift': 'rshft',
            'caps lock': 'caps',
            'return': 'entr',
            'left ctrl': 'lctrl',
            'right ctrl': 'rctrl',
            'left meta': 'wn',
            'right meta': 'wn',
            'left alt': 'lalt',
            'right alt': 'ralt',
            'compose': 'cmp',
            'space': 'spc',
            'escape': 'esc',
            'print screen': 'prnt',
            'scroll lock': 'scrl',
            'break': 'brk',
            'insert': 'insrt',
            'page up': 'pup',
            'page down': 'pdwn',
            'backspace': 'bksp',

        }

        
        text_rects = []
    
       
        #pos 0 = left side, 1 = right side
        for index, values in enumerate(controls):
            description, key = values
            modified_key = replace_keys[key].upper() if key in replace_keys.keys() else key.upper()
            text_1 = self.big_font.render(modified_key, True, (0, 0, 0))
            text_2 = self.medium_font.render(f" = {description}", True, color)
            text_2_rect = text_2.get_rect()
            text_2_rect.center = ((200 if pos == 0 else self.width - 150), (index * 50) + 450)
            text_1_rect = text_1.get_rect()
            text_1_rect.center = (text_2_rect.x - text_1_rect.width/2, text_2_rect.y + 10)
   
                                            #Dw about mechanics of this, just know that This only toggles True/False every half a second
            if underline and index == clicked_index and int(str(round(time.time(), 1))[-1:]) < 5:
                    pygame.draw.rect(self.screen, (240, 240, 166), pygame.Rect(text_1_rect.x, text_1_rect.y + 2, text_1_rect.width, text_1_rect.height + 2))
            
       

            pygame.draw.rect(self.screen, (123, 127, 162), text_1_rect)
            pygame.draw.rect(self.screen, keys_bkg_color, text_2_rect)
            self.screen.blit(text_1, (text_1_rect.x, text_1_rect.y))
            self.screen.blit(text_2, (text_2_rect.x, text_2_rect.y))

            text_rects.append(text_1_rect)


        return text_rects



    def credits_screen(self, pieces, draw_tetris_pieces):

        
        credits_list = ['Made by', 'Zack Ghanbari', 'and Ali Rastegar']
        text_y = 0
        text_offset = 80
        text_scroll_dist = 0.1
        
        def draw_text(tup):
            index, text = tup
            rendered_text = self.font.render(text, True, (255,255,255))
            self.screen.blit(rendered_text, (rendered_text.get_rect(center = (self.width/2, self.height/2))[0], text_y + (index * text_offset)))
        
       

        running = True
        while running:
            mouse = pygame.mouse.get_pos()
            #Game over loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:

                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.back_button.collidepoint(event.pos):
                        running = False


            self.screen.fill((0,0,0))
            draw_tetris_pieces(pieces)
            self.draw_back_button(mouse)

            text_y = text_y + text_scroll_dist if text_y <= self.width + 100 else -1 * (len(credits_list) * text_offset)

            list(map(draw_text, enumerate(credits_list)))
            pygame.display.update()
            
    
    def pick_controls_screen(self):
        

        def draw_reset_button(pos):
            white = (255, 255, 255)
            color = tuple(map(darken, white)) if reset_button.collidepoint(pos) else white
            pygame.draw.rect(self.screen, color, reset_button)
            self.screen.blit(reset_text, (self.width/2 - 50 + 20,  self.height - 45 + 12))
        
        
        
        def reset_controls():
            with open('controls.json', 'w') as f:
                json.dump(self.default_controls, f, indent=2)


            self.left_controls = {
                    
                "Move Left": self.default_controls["Move Left"],
                "Move Right": self.default_controls["Move Right"],
                "Soft Drop": self.default_controls["Soft Drop"],
                "Toggle Movement": self.default_controls["Toggle Movement"],
                "Toggle Music": self.default_controls["Toggle Music"]

            }
           
            self.right_controls = {
                    "Rotate Clockwise": self.default_controls["Rotate Clockwise"],
                    "Rotate Counter-Clockwise": self.default_controls["Rotate Counter-Clockwise"],
                    "Hold Piece": self.default_controls["Hold Piece"],
                    "Hard Drop": self.default_controls["Hard Drop"]
            }

        def draw_title():
            self.screen.blit(title_text_1, (self.width/2 - 140, 100))
            self.screen.blit(title_text_2, (self.width/2 - 200, 160))
        
        def draw_prompt():
            if clicked:
                color = (240, 240, 166) if  int(str(round(time.time(), 1))[-1:]) < 5 else (26, 27, 37)
                prompt_text = self.big_font.render('PRESS A KEY', True, color)
                self.screen.blit(prompt_text, (self.width/2 - 100, 300))

        mouse_number_key = {
            1: 'left click',
            2: 'middle click',
            3: 'right click'
        }

        def get_key_input(key, mouse_clicked=False):

            if not mouse_clicked:
                key = pygame.key.name(key)
            else:
                key = mouse_number_key[key]

            if clicked_index_1 >= 0:
                self.left_controls[list(self.left_controls.keys())[clicked_index_1]] = key

            elif clicked_index_2 >= 0:
                self.right_controls[list(self.right_controls.keys())[clicked_index_2]] = key

            with open('controls.json', 'w') as f:
                full_controls = dict(self.left_controls, **self.right_controls)
                json.dump(full_controls, f, indent=2)

        

        title_text_1 = self.big_font.render('CLICK ON A BOX TO', True, (255, 255, 255))
        title_text_2 = self.big_font.render('CHANGE YOUR CONTROLS', True, (255, 255, 255))
        reset_text = self.medium_font.render('RESET', True, (0, 0, 0))
        text_boxes_1 = []
        text_boxes_2 = []
        clicked = False
        clicked_index_1 = -1
        clicked_index_2 = -1
        reset_button = pygame.Rect(self.width/2 - 50, self.height - 35, 100, 27)
    
        running = True
        while running:
            #bkg color
            self.screen.fill((26, 27, 37))

            mouse = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:

                    pygame.quit()
                    sys.exit()


                elif event.type == pygame.MOUSEBUTTONDOWN:

                    if clicked:
                        if 1 <= event.button <= 3:
                            get_key_input(event.button, mouse_clicked=True)
                            clicked = False
                            
                    elif event.button == 1:
 
                        if self.back_button.collidepoint(event.pos):
                            running = False

                        elif reset_button.collidepoint(event.pos):
                            reset_controls()

                        else:
                            for index, text_box in enumerate(text_boxes_1):
                                if text_box.collidepoint(event.pos):
                                    clicked = True
                                    clicked_index_2 = -1
                                    clicked_index_1 = index
                                


                            for index, text_box in enumerate(text_boxes_2):
                                if text_box.collidepoint(event.pos):
                                    clicked = True
                                    clicked_index_1 = -1
                                    clicked_index_2 = index
                        

                elif event.type == pygame.KEYDOWN:
                    # z = pygame.key.name(event.key)
                    if clicked:
                        get_key_input(event.key)
                    
                    clicked = False
    
            self.draw_back_button(mouse)
            draw_reset_button(mouse)

            draw_title()
            draw_prompt()
            
            text_boxes_1 = self.draw_controls(self.left_controls.items(), 0, (89, 248, 232), keys_bkg_color = (26, 27, 37), underline = clicked, clicked_index = clicked_index_1)
            text_boxes_2 = self.draw_controls(self.right_controls.items(), 1,  (89, 248, 232),  keys_bkg_color =(26, 27, 37), underline = clicked, clicked_index = clicked_index_2)


            pygame.display.update()


    def start_screen(self):

        connected = False

        def draw_start_button():
            nonlocal start_button_text_color, connected

            if not connected:
                #if mouse hovering make it lighter
                if start_button_pos[0] <= mouse[0] <= start_button_pos[0] + start_button_dimensions[0] and start_button_pos[1] <= mouse[1] <= start_button_pos[1] + start_button_dimensions[1]: 
                    pygame.draw.rect(self.screen, (255,255,255), (start_button_pos, start_button_dimensions)) 
                    start_button_text_color = (r, g, b)
                
                else: 
                    pygame.draw.rect(self.screen, (0,0,0), (start_button_pos, start_button_dimensions))
                    start_button_text_color = (255, 255, 255)


        def draw_text():

            nonlocal connected

            if not connected:
                start_button_text = self.font.render('START', True, start_button_text_color)
                start_button_coords = (start_button_pos[0] + 20, start_button_pos[1] + 3)
            
            else:
                start_button_text = self.font.render('Waiting for opponent...', True, start_button_text_color)
                start_button_coords = (start_button_pos[0] - 80, start_button_pos[1])

            title_text = self.very_big_font.render('TETRIUM', True, (r, g, b)) 
            self.screen.blit(start_button_text, start_button_coords)
            self.screen.blit(title_text, (self.width/2 - 165, self.height/2 - 200)) 
         


        def draw_mute_button_background():
            pygame.draw.circle(self.screen, (255,255,255), mute_button_pos,  mute_button_radius)
           

        def check_mute_and_draw_icons():
            draw_mute_button_background()
            if self.muted:
                self.lowered_volume, self.volume = 0, 0
                self.screen.blit(volume_off_icon, volume_icon_pos)
            
            else:
                self.lowered_volume, self.volume = 0.03, 0.1
                self.screen.blit(volume_on_icon, volume_icon_pos)

       
        def draw_input_text():
            nonlocal input_text_width

            if not input_text:
                self.screen.blit(input_box_placeholder, (input_box_x + 25, input_box_y + 12))


            input_text_render = self.big_font.render(input_text, True, (0, 0, 0))
            input_text_width = input_text_render.get_rect().width
            self.screen.blit(input_text_render, (input_box_x + 5, input_box_y + 6))


        def draw_input_box():
            if input_active:
                input_bkg_color = (0, 0, 255)

            else:
                input_bkg_color = (0, 0, 0)

            pygame.draw.rect(self.screen, input_bkg_color, input_box, 10)
            pygame.draw.rect(self.screen, (255,255,255), input_box_bkg)

            draw_input_text()
            
           

        def get_input(key):
            nonlocal input_text
            if input_text_width < input_box_width - 15:
                input_text += key
    
        def start():
            nonlocal connected, input_active, input_text
            input_active = False

            input_text = input_text.strip()
            if not input_text:
                input_text = "Player"

            self.n = network.Network()
            self.player = self.n.p

            if isinstance(self.n.p, str):
                outdated_info = self.n.p.split()
                                            # new version number # download link
                self.outdated_version_screen(outdated_info[2], outdated_info[3])

            connected = True
            self.name = input_text
            self.n.send("name " + input_text)

        def cycle_colors():
        
            nonlocal r, g, b
      
            if g < 255 and r > 0:
                g += 1
                r -= 1

            else:
                if b < 255 and g > 0:
                    b += 1
                    g -= 1
 
                else:
                    r, g, b = 255, 0, 0
            
        def draw_tetris_pieces(pieces):
            for i, piece in enumerate(pieces):
                #means piece is off the screen
                if piece.y >= 28:
                    #Moves it back up
                    piece.move(0, randint(-35, -30))

                piece.render(False)
                if time.time() > last_falls[i]:
                    piece.move(0, 1)
                    last_falls[i] = time.time() + 0.75

        def draw_credits_button(pos):
            color = tuple(map(lighten, (r,g,b))) if credits_button.collidepoint(pos) else (r, g, b)
            pygame.draw.rect(self.screen, color, credits_button)
            self.screen.blit(credits_button_text, (credits_button_pos[0] + 3, credits_button_pos[1] + 5))   


        def draw_controls_button(pos):
            color = tuple(map(lighten, (r,g,b))) if controls_button.collidepoint(pos) else (r, g, b)
            pygame.draw.rect(self.screen, color, controls_button)
            self.screen.blit(controls_button_text, (controls_button_pos[0] + 5, controls_button_pos[1] + 3))
        
      
        #It might seem confusing whats happeneing here but dw about it, just making sure blocks are spaced out
        x_pos = [0, 4, 8, 12, 16, 20, 0, 4, 8]
        shuffle(x_pos)

        pieces = [

            Piece(x_pos[0], randint(-9, -6), 'T'), 
            Piece(x_pos[1], randint(-6, -3), 'L'), 
            Piece(x_pos[2], randint(-3, 0), 'J'), 
            Piece(x_pos[3], randint(0, 3), 'S'), 
            Piece(x_pos[4], randint(3, 6), 'Z'), 
            Piece(x_pos[5], randint(6, 9), 'I'),
            Piece(x_pos[6], randint(9, 12), 'T'),
            Piece(x_pos[7], randint(12, 15), 'L'),
            Piece(x_pos[8], randint(-15, -12), 'J'),
         
        ]
        
        r, g, b = 255, 0, 0

        last_falls = [time.time() for _ in pieces]
        start_button_dimensions = (140, 40)
        start_button_pos = (self.width/2 - 70, self.height/2)
        start_button_text_color = (255, 255, 255)
        mute_button_pos = (int(self.width/2), int(self.height/2 + 100))
        mute_button_radius = 35
        volume_on_icon = pygame.image.load('assets/volume-high.png')
        volume_off_icon = pygame.image.load('assets/volume-off.png')
        volume_icon_pos = (mute_button_pos[0] - 25, mute_button_pos[1] - 25)
        s = pygame.Surface((self.width, self.height), pygame.SRCALPHA) # noqa pylint: disable=too-many-function-args
        input_box_placeholder = self.medium_font.render("Enter a name...", True, (96, 93, 93))
        input_box_y =  self.height/2 - 85
        input_box_width = 300
        input_box_x = (self.width - input_box_width)/2
        input_box_height = 50
        input_box = pygame.Rect(input_box_x, input_box_y, input_box_width, input_box_height)
        input_box_bkg = pygame.Rect((self.width - input_box_width)/2 , self.height/2 - 85, input_box_width, input_box_height)
        input_active = False
        input_text = ''
        input_text_width = 0
        
        controls_button_pos = (0 , self.height - 30)
        controls_button = pygame.Rect(controls_button_pos[0], controls_button_pos[1], 125, 30)
        controls_button_text = self.medium_font.render('CONTROLS', True, (0, 0, 0))
        credits_button_text = self.small_font.render('CREDITS', True, (0, 0, 0))
        credits_button_height = 30
        credits_button_pos = (self.width - 70, self.height - credits_button_height)
        credits_button = pygame.Rect(credits_button_pos[0], credits_button_pos[1], 70, credits_button_height)


        while True:
            #NOTE make sure this is at the top
            s.fill((0,0,0, 2))

            mouse = pygame.mouse.get_pos() 

            #Game over loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:

                    if connected:
                        self.n.disconnect()

                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                   
                    if start_button_pos[0] <= mouse[0] <= start_button_pos[0] + start_button_dimensions[0] and start_button_pos[1] <= mouse[1] <= start_button_pos[1] + start_button_dimensions[1] and not connected:  
                        
                        start()

                        pygame.mixer.music.set_volume(self.volume)
                        self.screen.fill((0, 0, 0))

                    elif mute_button_pos[0] - mute_button_radius <= mouse[0] <= mute_button_pos[0] + mute_button_radius and mute_button_pos[1] - mute_button_radius <= mouse[1] <=  mute_button_pos[1] + mute_button_radius: 
                        self.muted = not self.muted
                    
                    elif credits_button.collidepoint(event.pos):
                        self.credits_screen(pieces, draw_tetris_pieces)
                        #NOTE after we go back from the credits screen, we have to refresh the screen with black so the text doesnt linger over, because our background is opaque
                        s.fill((0, 0, 0))

                    elif controls_button.collidepoint(event.pos):
                        self.pick_controls_screen()
                        #NOTE after we go back from the credits screen, we have to refresh the screen with black so the text doesnt linger over, because our background is opaque
                        s.fill((0, 0, 0))


                    elif input_box.collidepoint(event.pos) and not connected:
                        input_active = True
                    
                    else: 
                        input_active = False

                elif event.type == pygame.KEYDOWN:
                    
                    if input_active:
                        
                        if event.key == pygame.K_RETURN:
                            start()
                            pygame.mixer.music.set_volume(self.volume)
                            self.screen.fill((0, 0, 0))
                                

                        elif event.key == pygame.K_BACKSPACE:
                            input_text = input_text[:-1]

                        else:
                            get_input(event.unicode)

                        
           
            pygame.mixer.music.set_volume(self.lowered_volume)
            self.screen.blit(s, (0, 0))  
            cycle_colors()
            draw_tetris_pieces(pieces)
            check_mute_and_draw_icons()
            draw_credits_button(mouse)
            draw_controls_button(mouse)

            if not connected:
                draw_start_button()
                
            draw_text()
            draw_input_box()

            # checking if game started
            if connected and ( data := self.n.send('get') ).ready:
                self.opp_name = data.opp_name(self.n.p)
                break
            
                
            pygame.display.update()

            self.clock.tick(60)

        self.time_started = time.time()
        self.running = True

    def outdated_version_screen(self, new_version, download_link):

        copy_button_text_color = (0,0,0)
        copy_button_dimensions = (300, 40)
        copy_button_pos = (self.width/2 - copy_button_dimensions[0]/2, self.height/2 - copy_button_dimensions[1]/2)
        copy_button_rect = pygame.Rect(*copy_button_pos, *copy_button_dimensions)


        quit_button_text_color = (0,0,0)
        quit_button_dimensions = (80, 40)
        quit_button_pos = (self.width/2 - quit_button_dimensions[0]/2, 700)
        quit_button_rect = pygame.Rect(*quit_button_pos, *quit_button_dimensions)
    

        def draw_text():
            text1 = self.font.render("You are running an outdated", True, (255, 255, 255))
            text2 = self.font.render("version of the game", True, (255, 255, 255))

            text3 = self.font.render(f"Your Version: {network.version}", True, (255, 255, 255))
            text4 = self.font.render(f"New Version: {new_version}", True, (255, 255, 255))

            self.screen.blit(text1, (self.width/2-200, 100))
            self.screen.blit(text2, (self.width/2-130, 150))
            self.screen.blit(text3, (self.width/2-140, 250))
            self.screen.blit(text4, (self.width/2-140, 290))


        copied_pos = 0
        copy_animation = False

        def draw_buttons():

            nonlocal quit_button_text_color
        
            pygame.draw.rect(self.screen, (255,255,255), copy_button_rect)
                
            copy_button_text = self.font.render("Copy download link", True, copy_button_text_color)
            self.screen.blit(copy_button_text, (copy_button_pos[0] + 10, copy_button_pos[1] + 3))
                

            if quit_button_pos[0] <= mouse[0] <= quit_button_pos[0] + quit_button_dimensions[0] and quit_button_pos[1] <= mouse[1] <= quit_button_pos[1] + quit_button_dimensions[1]: 
                pygame.draw.rect(self.screen, (0,0,0), quit_button_rect)
                quit_button_text_color = (255,255,255)

            
            else: 
                pygame.draw.rect(self.screen, (255,255,255), quit_button_rect)
                quit_button_text_color = (0, 0, 0)


            quit_button_text = self.font.render("Quit", True, quit_button_text_color)
            self.screen.blit(quit_button_text, (quit_button_pos[0] + 10, quit_button_pos[1] + 3))


        def check_click(pos):

            nonlocal copied_pos, copy_animation
            

            if copy_button_rect.collidepoint(pos):
                pyperclip.copy(download_link)

                copied_pos = self.height/2 - copy_button_dimensions[1]/2
                copy_animation = True

            elif quit_button_rect.collidepoint(pos):
                pygame.quit()
                sys.exit()




        while True:

            game.screen.fill((0, 0, 0))

            mouse = pygame.mouse.get_pos() 

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    check_click(event.pos)


            draw_text()
            draw_buttons()

            if copy_animation:
                copied_pos -= 2
                
                copied_text = self.font.render("Copied!", True, (49, 235, 228))
                self.screen.blit(copied_text, (copy_button_pos[0]+100, copied_pos))

                if copied_pos <= 320:
                    copy_animation = False

            pygame.display.update()
            self.clock.tick(60)

    
    def disconnected_screen(self, text1, text2):

        def draw_text():
            dc_text_1 = self.font.render(text1, True, (255, 255, 255))
            dc_text_2 = self.font.render(text2,  True, (255, 255, 255))
            self.screen.blit(dc_text_1, (self.width/2 - 175, 200))
            self.screen.blit(dc_text_2, (self.width/2 - 75, 300))
    
        def cycle_colors():
            
            nonlocal r, g, b

            if g < 255 and r > 0:
                g += 1
                r -= 1

            else:
                if b < 255 and g > 0:
                    b += 1
                    g -= 1
                
                else:
                    r, g, b = 255, 0, 0

           
        def draw_button():
            nonlocal button_text_color

            #if mouse hovering make it yellow
            if button_pos[0] <= mouse[0] <= button_pos[0] + button_dimensions[0] and button_pos[1] <= mouse[1] <= button_pos[1] + button_dimensions[1]: 
                pygame.draw.rect(self.screen, (255,255,255), button_rect)
                cycle_colors()
                button_text_color = (r, g, b)

            
            else: 
                pygame.draw.rect(self.screen, (255,255,255), button_rect)
                button_text_color = (0, 0, 0)
                
            button_text = self.font.render("FIND NEW MATCH", True, button_text_color)
            self.screen.blit(button_text, (button_pos[0] + 10, button_pos[1] + 3))

        def check_click(pos):
            nonlocal disconnected
            if button_rect.collidepoint(pos):
                disconnected = False
                game.running = False


        r, g, b = 255, 0, 0
        button_text_color = (0,0,0)
        button_dimensions = (300, 40)
        button_pos = (self.width/2 - button_dimensions[0]/2, self.height/2 - button_dimensions[1]/2)
        button_rect = pygame.Rect(*button_pos, *button_dimensions)
        disconnected = True
        while disconnected:

            mouse = pygame.mouse.get_pos() 

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    
                    check_click(event.pos)

    
            self.screen.fill((0,0,0))

            draw_text()
            draw_button()

            pygame.display.update()



game = Game()


class Block(Game):

    def __init__(self, x, y, color, colorByName=True):

        self.x, self.y = x, y

        if colorByName:
            self.color = color_key[color]
        else:
            self.color = color

        self.size = 30


        self.flash_start = 0
        self.direction = 0


        self.fade_start = 0
    
    def render(self):

        # normal
        if time.time() > self.flash_start + 0.2 and not self.fade_start:

            darker = tuple(map(darken, self.color))
            pygame.draw.rect(game.screen, darker, ((self.x-1) * self.size + 100, (self.y-1)* self.size + 100, 30, 30))
            pygame.draw.rect(game.screen, self.color, ((self.x-1) * self.size + 105, (self.y-1)* self.size + 105, 20, 20))

        # flashing
        elif time.time() <= self.flash_start + 0.2:

            flash_time = self.flash_start + 0.2 - time.time()

            flash_color = []

            # whether it flashes dark or light
            direction = self.direction

            # orange, blue, purple flashes light
            if flash_time >= 0.1:
                direction *= -1

            for color in self.color:

                color = color + (flash_time * 270 * direction)
                
                if color > 255: color = 255
                elif color < 0: color = 0

                flash_color.append(color)

            flash_color = tuple(flash_color)

            darker = tuple(map(darken, flash_color))

            pygame.draw.rect(game.screen, darker, ((self.x-1) * self.size + 100, (self.y-1)* self.size + 100, 30, 30))
            pygame.draw.rect(game.screen, flash_color, ((self.x-1) * self.size + 105, (self.y-1)* self.size + 105, 20, 20))

        # fading
        else:
            fade_time = self.fade_start + 0.5 - time.time()

            if fade_time > 0:
                color_difference = [255 - color for color in self.color]

                fade_color = []
                for x in range(3):
                    fade_color.append((color_difference[x] / 0.5 * (0.5 - fade_time)) + self.color[x])
                fade_color = tuple(fade_color)
            else:
                fade_color = (255, 255, 255)

            
            darker = tuple(map(darken, fade_color))

            pygame.draw.rect(game.screen, darker, ((self.x-1) * self.size + 100, (self.y-1)* self.size + 100, 30, 30))
            pygame.draw.rect(game.screen, fade_color, ((self.x-1) * self.size + 100, (self.y-1)* self.size + 100, 30, 30))


    # for putting blocks on second screen
    def render_second(self):

        darker = tuple(map(darken, self.color))
        pygame.draw.rect(game.screen, darker, ((self.x-1) * self.size/2 + 570, (self.y-1)* self.size/2 + 250, 15, 15))
        pygame.draw.rect(game.screen, self.color, ((self.x-1) * self.size/2 + 572, (self.y-1)* self.size/2 + 252, 11, 11))                    


    def render_preview(self):

        pygame.draw.rect(game.screen, (255, 255, 255), ((self.x-1) * self.size + 100, (self.y-1)* self.size + 100, 30, 30))
        pygame.draw.rect(game.screen, game.foreground_color, ((self.x-1) * self.size + 103, (self.y-1)* self.size + 103, 24, 24))



class Piece(Game):

    def __init__(self, x, y, piece):

        self.x, self.y = x, y

        self.piece_type = piece

        self.blocks = list(map(lambda args: Block(*args), pieces_lib.get_piece(x, y, piece)))

        self.rotation = "0"

        
        if piece == "T":
            self.corners = {"point left": [x-1, y-1], "point right": [x+1, y-1], "flat left": [x-1, y+1], "flat right": [x+1, y+1]}

        elif piece == "I":
            self.x += 0.5
            self.y += 0.5

    
    def move(self, x, y):

        self.x += x
        self.y += y

        for block in self.blocks:
            block.x += x
            block.y += y

        if self.piece_type == "T":
            for coords in self.corners.values():
                coords[0] += x 
                coords[1] += y

    def flash(self):

        if self.piece_type in ("L", "J", "T"):
            direction = -1
        else:
            direction = 1

        for block in self.blocks:
            block.direction = direction
            block.flash_start = time.time()


    def _set_rotation_value(self, direct):

        if direct == 0:
            
            if self.rotation == "0":
                self.rotation = "R"
            
            elif self.rotation == "R":
                self.rotation = "2"
            
            elif self.rotation == '2':
                self.rotation = 'L'

            elif self.rotation == 'L':
                self.rotation = '0'

        else:
            if self.rotation == "0":
                self.rotation = "L"
            
            elif self.rotation == "L":
                self.rotation = "2"
            
            elif self.rotation == '2':
                self.rotation = 'R'

            elif self.rotation == 'R':
                self.rotation = '0'


    def _path_check(self, direct, x, y):

        # invert y direction
        y *= -1

        self.move(x, y)

        if not self.check_overlap():
            game.correct_rotateSFX.play()
            return True

        # reset
        self.move(-1*x, -1*y)
        
        return False



    #0 means clockwise, 1 means counterclockwise
    def rotate(self, direct: int):
       

        if self.piece_type == "O": return game.correct_rotateSFX.play()

        org_block_coords = []

        x, y = self.x, self.y # noqa pylint: disable=unused-variable

        if direct == 0:
            #clockwise
            for block in self.blocks:
                #Math formula
                temp_x, temp_y = block.x, block.y
                org_block_coords.append((temp_x, temp_y))

                block.x = (-1*(temp_y-self.y) + self.x)
                block.y = ((temp_x - self.x) + self.y)

            if self.piece_type == "T":

                org_corner_coords = []
                for coords in self.corners.values():
                    temp_x, temp_y = coords
                    org_corner_coords.append([temp_x, temp_y])

                    coords[0] = (-1*(temp_y-self.y) + self.x)
                    coords[1] = ((temp_x - self.x) + self.y)

            

        else:
            #counter-clockwise
            
            for block in self.blocks:
                #Math formula
                temp_x, temp_y = block.x, block.y
                org_block_coords.append((temp_x, temp_y))
                block.x = (temp_y - self.y + self.x)
                block.y = (-1*(temp_x - self.x) + self.y)

            if self.piece_type == "T":

                org_corner_coords = []
                for coords in self.corners.values():
                    temp_x, temp_y = coords
                    org_corner_coords.append([temp_x, temp_y])

                    coords[0] = (temp_y - self.y + self.x)
                    coords[1] = (-1*(temp_x - self.x) + self.y)


        old_rotation = self.rotation

        self._set_rotation_value(direct)

        if self.check_overlap():

            # all following SRS Tetris guideline

            if self.piece_type == "I":
                
                # clockwise
                if direct == 0:
                    
                    # 0 -> R
                    if old_rotation == "0":
                        if self._path_check(direct, -2, 0): return
                        if self._path_check(direct, 1, 0): return
                        if self._path_check(direct, -2, -1): return
                        if self._path_check(direct, 1, 2): return


                    # R -> 2
                    elif old_rotation == 'R':
                        if self._path_check(direct, -1, 0): return
                        if self._path_check(direct, 2, 0): return
                        if self._path_check(direct, -1, 2): return
                        if self._path_check(direct, 2, -1): return
                    
                    # 2 -> L
                    elif old_rotation == '2':
                        if self._path_check(direct, 2, 0): return
                        if self._path_check(direct, -1, 0): return
                        if self._path_check(direct, 2, 1): return
                        if self._path_check(direct, -1, -2): return

                    # L -> 0
                    elif old_rotation == "L":
                        if self._path_check(direct, 1, 0): return
                        if self._path_check(direct, -2, 0): return
                        if self._path_check(direct, 1, -2): return
                        if self._path_check(direct, -2, 1): return


                # counterclockwise
                else:

                    # R -> 0
                    if old_rotation == "R":
                        if self._path_check(direct, 2, 0): return
                        if self._path_check(direct, -1, 0): return
                        if self._path_check(direct, 2, 1): return
                        if self._path_check(direct, -1, -2): return

                    # 2 -> R
                    elif old_rotation == "2":
                        if self._path_check(direct, 1, 0): return
                        if self._path_check(direct, -2, 0): return
                        if self._path_check(direct, 1, -2): return
                        if self._path_check(direct, -2, 1): return

                    # L -> 2
                    elif old_rotation == "L":
                        if self._path_check(direct, -2, 0): return
                        if self._path_check(direct, 1, 0): return
                        if self._path_check(direct, -2, -1): return
                        if self._path_check(direct, 1, 2): return
                    
                    # 0 -> L
                    elif old_rotation == "0":
                        if self._path_check(direct, -1, 0): return
                        if self._path_check(direct, 2, 0): return
                        if self._path_check(direct, -1, 2): return
                        if self._path_check(direct, 2, -1): return



            else:

                # clockwise
                if direct == 0:

                    
                    # 0 -> R
                    if old_rotation == "0":
                        if self._path_check(direct, -1, 0): return
                        if self._path_check(direct, -1, 1): return
                        if self._path_check(direct, 0, -2): return
                        if self._path_check(direct, -1, -2): return


                    # R -> 2
                    elif old_rotation == 'R':
                        if self._path_check(direct, 1, 0): return
                        if self._path_check(direct, 1, -1): return
                        if self._path_check(direct, 0, 2): return
                        if self._path_check(direct, 1, 2): return
                    
                    # 2 -> L
                    elif old_rotation == '2':
                        if self._path_check(direct, 1, 0): return
                        if self._path_check(direct, 1, 1): return
                        if self._path_check(direct, 0, -2): return
                        if self._path_check(direct, 1, -2): return

                    # L -> 0
                    elif old_rotation == "L":
                        if self._path_check(direct, -1, 0): return
                        if self._path_check(direct, -1, -1): return
                        if self._path_check(direct, 0, 2): return
                        if self._path_check(direct, -1, 2): return


                # counterclockwise
                else:

                    # R -> 0
                    if old_rotation == "R":
                        if self._path_check(direct, 1, 0): return
                        if self._path_check(direct, 1, -1): return
                        if self._path_check(direct, 0, 2): return
                        if self._path_check(direct, 1, 2): return

                    # 2 -> R
                    elif old_rotation == "2":
                        if self._path_check(direct, -1, 0): return
                        if self._path_check(direct, -1, 1): return
                        if self._path_check(direct, 0, -2): return
                        if self._path_check(direct, -1, -2): return

                    # L -> 2
                    elif old_rotation == "L":
                        if self._path_check(direct, -1, 0): return
                        if self._path_check(direct, -1, -1): return
                        if self._path_check(direct, 0, 2): return
                        if self._path_check(direct, -1, 2): return
                    
                    # 0 -> L
                    elif old_rotation == "0":
                        if self._path_check(direct, 1, 0): return
                        if self._path_check(direct, 1, 1): return
                        if self._path_check(direct, 0, -2): return
                        if self._path_check(direct, 1, -2): return
            

            # if all tests fail
            self.rotation = old_rotation
            
            # reset
            for index, block in enumerate(self.blocks):
                block.x, block.y = org_block_coords[index]

            if self.piece_type == "T":
                for index, coords in enumerate(self.corners.values()):
                    coords = org_corner_coords[index]
  

        else:
            game.correct_rotateSFX.play()
            
            
        """
        First move piece in bounds if it is out of bounds.
        If there is any overlapping conflict, then do the following:

        Check if the piece is ok if it moves two blocks up, if not,
        Check if it can move right by two blocks if clockwise, or left if counterclockwise,
        if not,
        check the other direction.
        
        If all of these fail, then the rotation will not occur.
        """

    

    def check_overlap(self):

        for block in self.blocks:

            if block.y > 20 or block.x < 1 or block.x > 10:
                return True


            for resting in game.resting:

                if block.x == resting.x and block.y == resting.y:
                    return True
        
        return False

    def overlapping_blocks(self):

        for block in self.blocks:
            for resting in game.resting:
                if (block.x == resting.x and block.y == resting.y):
                    return True
        
        return False
            
        
    def check_floor(self):

        for block in self.blocks:

            # if hits floor
            if block.y > 20:
                return True

            # if hits another block
            for resting_block in game.resting:
                if resting_block.x == block.x and resting_block.y == block.y:
                    return True
        
        return False


    def check_right(self):

        for block in self.blocks:
            
            # if hits wall
            if block.x > 9:
                return True

            # if hits another block
            for resting_block in game.resting:
                if resting_block.x == block.x+1 and resting_block.y == block.y:
                    return True
        
        return False


    def check_left(self):

        for block in self.blocks:
            
            # if hits wall
            if block.x < 2:
                return True

            # if hits another block
            for resting_block in game.resting:
                if resting_block.x == block.x-1 and resting_block.y == block.y:
                    return True
        
        return False
        
    
    def render(self, preview = True):
        # to render preview
        self.x, self.y
        
        if preview:
            downCount = 0

            while not self.check_floor():
                self.move(0, 1)
                downCount += 1
            self.move(0, -1)
            
            for block in self.blocks:
                block.render_preview()
            
            for x in range(downCount): # noqa pylint: disable=unused-variable
                self.move(0, -1)

            self.move(0, 1)
            
        # for actual piece
        for block in self.blocks:
            block.render()


if __name__ == "__main__":
    import main