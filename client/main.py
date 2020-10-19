# pylint: disable=no-member, unused-wildcard-import
import pygame
from game import *
import time
import random
import sys


pieces = ["T", "L", "J", "S", "Z", "I", "O"]

bag = pieces.copy()
random.shuffle(bag)
next_bag = pieces.copy()
random.shuffle(next_bag)

fall_speed = 1 # means once per second
speed_up_rate = 30 # every 30 seconds speed up


last_fall = time.time() + fall_speed
fall = 0

current = Piece(5, 1, bag.pop(0))

speedUp = False

avoids = 0

held = ''

last_speed_up = time.time() + speed_up_rate
display_until = 0

canSwitch = True
rotation_last = False


def game_over():

    global bag, next_bag, avoids, current, held

    gameOver = True

    pygame.mixer.music.set_volume(game.lowered_volume)
    button_dimensions = (165, 40)
    button_pos = (int(game.width/2 - button_dimensions[0]/2), int(game.height/2))

   

    while gameOver:

        mouse = pygame.mouse.get_pos()
        #Game over loop

        button_color = (0, 0, 0)
        button_text_color = (255, 255, 255)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                
                if button_pos[0] <= mouse[0] <= button_pos[0] + button_dimensions[0] and button_pos[1] <= mouse[1] <= button_pos[1] + button_dimensions[1]: 

                    gameOver = False
                    game.resting.clear()
                    game.removing.clear()
                    game.level = 0
                    bag = pieces.copy()
                    random.shuffle(bag)
                    next_bag = pieces.copy()
                    random.shuffle(next_bag)
                    avoids = 0
                    current = Piece(5, 1, bag.pop(0))
                    pygame.mixer.music.set_volume(game.volume)
                    held = None

        if button_pos[0] <= mouse[0] <= button_pos[0] + button_dimensions[0] and button_pos[1] <= mouse[1] <= button_pos[1] + button_dimensions[1]: 
            
            button_text_color = (0, 0, 0)
            button_color = (255, 255, 255)



        pygame.draw.rect(game.screen, button_color, (button_pos, button_dimensions))
        s = pygame.Surface((game.width, game.height), pygame.SRCALPHA) # noqa pylint: disable=too-many-function-args
        s.fill((255,255,255, 2))      
        game.screen.blit(s, (0,0))
        game_over_font = pygame.font.Font('assets/arial.ttf', 60)
        button_font  = pygame.font.Font('assets/arial.ttf', 32)
        game_over_text = game_over_font.render(f'Game Over', True, (0, 0, 0), game.screen)
        button_text = button_font.render(f'RESTART', True, button_text_color, game.screen)
        textRect = game_over_text.get_rect() 
        textRect.center = (game.width // 2, 200) 
        game.screen.blit(game_over_text, textRect)
        game.screen.blit(button_text, (button_pos[0] + 10, button_pos[1] + 3))
        pygame.display.update()
        game.clock.tick(60)



moving = 0
last_moved = 0


last_rotation_fall = 0

combo = -1
score_key = [100, 300, 500, 800]
tspin_key = [{"mini": 200, "normal": 800}, {"mini": 400, "normal": 1200}, {"normal": 1600}]
difficult_before = False


last_touched = 0
touched_floor = False

#This runs the start screen loop, it cant be in the main loop or it will mess things up
game.start_screen()

texts = []

speed_up_lines_cleared = 0

while game.running:

    if moving:

        rotation_last = False

        if moving == -1:
            if time.time() - last_moved > 0.1:
                if not current.check_left():
                    current.move(-1, 0)
                    last_moved = time.time()

                    current.move(0, 1)
                    if current.check_floor():
                        if avoids < 15:
                            fall = time.time() + 0.3
                            avoids += 1
                    current.move(0, -1)


        elif moving == 1:
            if time.time() - last_moved > 0.1:
                if not current.check_right():
                    current.move(1, 0)
                    last_moved = time.time()

                    current.move(0, 1)
                    if current.check_floor():
                        if avoids < 15:
                            fall = time.time() + 0.3
                            avoids += 1
                    current.move(0, -1)


    for event in pygame.event.get():


        if event.type == pygame.KEYDOWN:

            # move left
            if event.key == pygame.K_a:

                if not game.continuous:
                    if not current.check_left():
                        current.move(-1, 0)

                        current.move(0, 1)
                        if current.check_floor():
                            if avoids < 15:
                                fall = time.time() + 0.3
                                avoids += 1
                        current.move(0, -1)

                        rotation_last = False

                else:
                    moving = -1
            
            # move right
            elif event.key == pygame.K_d:

                if not game.continuous:
                    if not current.check_right():
                        current.move(1, 0)

                        current.move(0, 1)
                        if current.check_floor():
                            if avoids < 15:
                                fall = time.time() + 0.3
                                avoids += 1
                        current.move(0, -1)

                else:
                    moving = 1

            # rotate clockwise
            elif event.key == pygame.K_RIGHT:
                
    
                current.rotate(0)

                current.move(0, 1)
                if current.check_floor():
                    if avoids < 15:
                        fall = time.time() + 1
                        avoids += 1
                current.move(0, -1)

                rotation_last = True



            # rotate counter-clockwise
            elif event.key == pygame.K_LEFT:
                current.rotate(1)

                current.move(0, 1)
                if current.check_floor():
                    if avoids < 15:
                        fall = time.time() + 1
                        avoids += 1
                
                current.move(0, -1)

                rotation_last = True

            #Pause
            elif event.key == pygame.K_ESCAPE:
                game.pause_screen()   
          
            # hold block
            elif event.key == pygame.K_UP:
                
                
                if canSwitch:
                    game.holdSFX.play()
                    
                    if not held:
                        held = current.piece_type
                        current = Piece(5, 1, bag.pop(0))
                    
                    else:
                        past_held = held
                        held = current.piece_type
                        current = Piece(5, 1, past_held)

                    avoids = 0
                    canSwitch = False
                    rotation_last = False

                    # checking if game is over
                    if current.overlapping_blocks():
                        current.rotate(1)

                        if current.overlapping_blocks():
                            current.rotate(-1)
                            current.rotate(-1)

                            if current.overlapping_blocks():
                                game_over()

                    if current.y <= -2:
                        game_over()

                    


            # speed down
            elif event.key == pygame.K_s:
                if not speedUp:
                    fall_speed /= 10
                    speedUp = True
                    last_fall -= 2
            
            # force down
            elif event.key == pygame.K_DOWN:
                
                downCount = 0
                while not current.check_floor():
                    current.move(0, 1)
                    downCount += 1

                current.move(0,-1)
                downCount -= 1

                last_fall -= 5
                fall -= 5
                touched_floor = True
                last_touched -= 5

                game.score += downCount*2
                rotation_last = False

            elif event.key == pygame.K_g:
                game.continuous = not game.continuous
                moving = 0

        elif event.type == pygame.KEYUP:

            # stop speed down
            if event.key == pygame.K_s:
                if speedUp:
                    fall_speed *= 10
                    speedUp = False

            
            # stop hold moving
            if event.key == pygame.K_a:
                if moving == -1:
                    moving = 0

            if event.key == pygame.K_d:
                if moving == 1:
                    moving = 0


        elif event.type == pygame.QUIT:
            game.running = False
            sys.exit()




    # for getting the next three items
    if len(bag) >= 3:
        game.render(bag[:3], held)

    elif len(bag) > 0:
        amount = len(bag)

        temp = bag.copy()
        temp.extend(next_bag[:3 - amount])
        game.render(temp, held)
    else:
        bag = next_bag.copy()
        next_bag = pieces.copy()
        random.shuffle(next_bag)
        game.render(bag[:3], held)



    # NOTE multiplayer only
    # if time.time() > last_speed_up:
    #     last_speed_up = time.time() + speed_up_rate
    #     fall_speed /= 1.2
    #     game.level += 1
    #     display_until = time.time() + 3


    current.move(0, 1)
    if current.check_floor() and not touched_floor:
        last_touched = time.time() + 0.95
        touched_floor = True
    elif not current.check_floor():
        touched_floor = False
    current.move(0, -1)



    # makes the piece fall by one
    if time.time() > last_fall:
        last_fall = time.time() + fall_speed
        current.move(0, 1)
        
        if speedUp and not current.check_floor():
            game.score += 1


        if not current.check_floor():
            rotation_last = False

        if current.check_floor():


            if time.time() > fall and time.time() > last_touched:

                # turn piece into resting blocks
                for block in current.blocks:
                    block = Block(block.x, block.y-1, block.color, colorByName=False)
                    block.flash_color = list(block.color)
    
                    flash_increments = []

                    if current.piece_type in ('L', 'J', 'Z', 'T'):
                        for color in block.flash_color:
                            target = color + 200
                            if target > 255: target = 255
                            color = (target-color) // 14
                            flash_increments.append(color)
                    else:
                        for color in block.flash_color:
                            target = color - 150
                            if target < 0: target = 0
                            color = (color-target) // 14
                            flash_increments.append(color*-1)
                    
                    block.flash_increments = tuple(flash_increments)
                    
                    game.resting.append(block)

                touched_floor = False

                # detect if a row was made
                lines_cleared = 0
                lowest_y = 0
                for y in range(1, 21):
                    row = list(filter(lambda block: block.y == y, game.resting))

                    # line clear
                    if len(row) == 10:

                        removed_blocks = []
                        # set the fade increments for blocks
                        for block in row:
                            
                            fade_increments = []
                            for color in block.color:
                                fade_increments.append((255 - color) // 15)

                            block.fade_increments = tuple(fade_increments)
                            removed_blocks.append(block)
                        
                        game.removing.append(removed_blocks)

                        lines_cleared += 1
                        if lowest_y < y:
                            lowest_y = y

                tspin = None

                # T-Spin detection
                if current.piece_type == "T" and rotation_last:

                    filled_corners = {}
            
                    # getting all filled corners, either by blocks or walls
                    for name, value in current.corners.items():
                        x, y = value
                        y -= 1

                        if not 0 < x < 10 or y > 20:
                            filled_corners[name] = True
                            continue

                        for block in game.resting:
                            if (block.x, block.y) == (x, y):
                                filled_corners[name] = True
                                break
                        else:
                            filled_corners[name] = False


                    # normal t-spin
                    if (filled_corners["point left"] and filled_corners["point right"]) and (filled_corners["flat right"] or filled_corners["flat left"]):
                        tspin = "normal"

                    # mini t-spin
                    elif (filled_corners["flat right"] and filled_corners["flat left"]) and (filled_corners["point left"] or filled_corners["point right"]):
                        tspin = "mini"


                if lines_cleared:


                    game.lines += lines_cleared

                    # NOTE this code is for singleplayer speed up only 
                    speed_up_lines_cleared += lines_cleared
                    if speed_up_lines_cleared >= 10:
                        speed_up_lines_cleared -= 10
                        game.level += 1
                        display_until = time.time() + 3
                        fall_speed = (0.8 - ((game.level - 1) * 0.007))**(game.level-1) 
                    # ^^^

                    combo += 1

                    if combo > 0:
                        texts.append((f"{combo+1} Combo", time.time() + 3, 20))

                    # calcualting combos
                    game.score += 50 * combo * (21 - lowest_y)


                    if not tspin:
                        # for adding normal value
                        line_clear_value = (21 - lowest_y) * score_key[lines_cleared-1]

        
                        # checking for back-to-back difficult line clear
                        if lines_cleared == 4:

                            texts.append(('Tetris', time.time() + 3, 30))

                            if difficult_before:
                                line_clear_value *= 1.5
                                line_clear_value = int(line_clear_value)
                                texts.append((f"Back to Back", time.time() + 3, 15))
                            else:
                                difficult_before = True

                        game.score += line_clear_value

                    else:
                        # any line clears with t-spins are considered difficult
                         
                        score_value = (21 - lowest_y) * tspin_key[lines_cleared-1][tspin]

                        if tspin == "normal":
                            spin_text, size = "T-Spin", 30
                        else:
                            spin_text, size = "T-Spin Mini", 17

                        if lines_cleared == 1:
                            lines_text = "Single"
                        elif lines_cleared == 2:
                            lines_text = "Double"
                        elif lines_cleared == 3:
                            lines_text = "Triple"

                        texts.append(([spin_text, lines_text], time.time() + 3, size))

                        if difficult_before:
                            score_value *= 1.5
                            texts.append((f"Back to Back", time.time() + 3, 15))
                        else:
                            difficult_before = True

                        game.score += score_value
                    
                
                # no line t-spins
                elif tspin:
                
                    # getting block with lowest y value
                    lowest_y = 0
                    for block in current.blocks:
                        if block.y > lowest_y:
                            lowest_y = block.y

                    lowest_y -= 19

                    if tspin == "normal":
                        game.score += 400 * lowest_y
                        texts.append((f"T-Spin", time.time() + 3, 30))

                    elif tspin == "mini":
                        game.score += 100 * lowest_y
                        texts.append((f"T-Spin Mini", time.time() + 3, 17))
                    
                
                if not lines_cleared:
                    combo = -1
                


    
                # for getting the next three items
                if len(bag) >= 3:
                    game.render(bag[:3], held)



                elif len(bag) > 0:
                    amount = len(bag)
                    temp = bag.copy()
                    temp.extend(next_bag[:3 - amount])
                    game.render(temp, held)
                else:
                    bag = next_bag.copy()
                    next_bag = pieces.copy()
                    random.shuffle(next_bag)
                    game.render(bag[:3], held)


                #TODO play land sound here
                canSwitch = True

                # make new falling piece
                current = Piece(5, 1, bag.pop(0))
                avoids = 0


                # checking if game is over
                if current.overlapping_blocks():
                    current.rotate(1)

                    if current.overlapping_blocks():
                        current.rotate(-1)
                        current.rotate(-1)

                        if current.overlapping_blocks():
                            game_over()

                if current.y <= -2:
                    game_over()


            else:
                current.move(0, -1)

    
    current.render()

    if display_until > time.time():
        text = game.font.render(f'Speed Level {game.level}', True, (0, 0 ,0))
        textRect = text.get_rect() 
        textRect.center = (game.width // 2, game.height // 2) 
        game.screen.blit(text, textRect)


     # queing up special texts
    removed_texts = []
    for text, display_until, size in texts:

        if display_until > time.time():

            font = pygame.font.Font('assets/arial.ttf', size)

            original = text

            if isinstance(text, str):
                text = text,

            textElements = []
            for line in text:
                textElement = font.render(line, True, (255, 255, 255))
                textRect = textElement.get_rect()

                textElements.append((textElement, textRect))

            for index, element in enumerate(textElements):
                textElement, textRect = element

                textRect.center = (450, 500 + (texts.index((original, display_until, size)) * 50) + (index * 25))

                game.screen.blit(textElement, textRect)


        else:
            removed_texts.append((text, display_until, size))
    
    for item in removed_texts:
        texts.remove(item)

    removed_texts.clear()

    
    pygame.display.update()

    game.clock.tick(60)