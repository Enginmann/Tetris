# This code works.
# But it contains some bugs.
# However, it they don't affect the gameplay.

import random
from sys import exit
import numpy as np
import pygame as pg
import json
from os import path


class Grid():
    def __init__(self, cols, color):
        self.color = color
        self.line_width = 3
        self.top_panal_height = 100
        self.cols, self.rows = cols, int((screen_height - self.top_panal_height) * cols / screen_width)
        self.grid = np.zeros((self.rows, self.cols))
        self.x_offset = int(screen_width / self.cols)
        self.y_offset = int((screen_height - self.top_panal_height) / self.rows)
        self.grid_height = self.rows * self.y_offset
        self.grid_width = self.cols * self.x_offset
        self.score = 0

    def display_score(self):
        score_surf = font.render(f'Score: {self.score}', False, grey)
        if game_over:
            score_rect = score_surf.get_rect(center=(int(screen_width/2), self.top_panal_height-30))
        else:
            score_rect = score_surf.get_rect(left=20, top=int(self.top_panal_height/2)-20)
        screen.blit(score_surf, score_rect)

    def display_highest_score(self, highest_score):
        highest_score_surf = font.render(f'Highest score: {highest_score}', False, grey)
        if starting:
            highest_score_rect = highest_score_surf.get_rect(center=(int(screen_width/2), int(self.top_panal_height/2)))
        else:
            highest_score_rect = highest_score_surf.get_rect(center=(int(screen_width/2), self.top_panal_height-70))
        screen.blit(highest_score_surf, highest_score_rect)

    def display_next_block(self, next_block, next_color):
        side_length = 20
        text_surf = font.render('Next: ', False, grey)
        text_rect = text_surf.get_rect(left=screen_width - 9 * side_length, top=int(self.top_panal_height / 2) - 20)
        screen.blit(text_surf, text_rect)
        next_block_rows, next_block_cols = next_block.shape
        horizontal_margin = side_length * (next_block_cols) + side_length
        vertical_margin = int(self.top_panal_height / 2 - next_block_rows * side_length / 2)
        for j in range(next_block_rows):
            for i in range(next_block_cols):
                if next_block[j][i] == 1:
                    pg.draw.rect(screen, next_color, [i * side_length + screen_width - horizontal_margin, j * side_length + vertical_margin, side_length, side_length])

    def display_grid(self):
        for j in range(self.cols + 1):
            pg.draw.line(screen, self.color, (j * self.x_offset, self.top_panal_height), (j * self.x_offset, self.grid_height + self.top_panal_height), self.line_width)
        for i in range(self.rows + 1):
            pg.draw.line(screen, self.color, (0, i * self.y_offset + self.top_panal_height), (self.grid_width, i * self.y_offset + self.top_panal_height), self.line_width)
        pg.draw.rect(screen, self.color, [0, 0, screen_width, self.top_panal_height])

    def display_block(self, block):
        indices = np.where(block.grid == 1)
        for i in range(len(indices[0])):
            if len(indices[1]) > 0:
                pg.draw.rect(screen, block.color, [indices[1][i] * self.x_offset, indices[0][i] * self.y_offset + self.top_panal_height, self.x_offset, self.y_offset])
            else:
                pg.draw.rect(screen, block.color, [block.x_pos * self.x_offset, indices[0][i] * self.y_offset + self.top_panal_height, self.x_offset, self.y_offset])

    def display_shadow_block(self, block):
        shadow_color = 0
        if block.color == red:
            shadow_color = shadow_red
        elif block.color == blue:
            shadow_color = shadow_blue
        elif block.color == light_blue:
            shadow_color = shadow_light_blue
        elif block.color == green:
            shadow_color = shadow_green
        elif block.color == orange:
            shadow_color = shadow_orange
        elif block.color == purple:
            shadow_color = shadow_purple
        shadow_grid = grid.grid[0: grid.rows, block.x_pos: block.x_pos + block.shape_cols].copy()
        shadow_grid_rows, shadow_grid_cols = shadow_grid.shape
        shadow_block_y_pos = block.y_pos
        shadow_block_x_pos = block.x_pos
        shadow_grid[0: shadow_block_y_pos + block.shape_rows, 0: block.shape_cols] *= 0
        indecies = np.where(shadow_grid == 1)
        shape_indecies = []
        shape_j_indecies = np.where(block.shape == 1)[0]
        shape_i_indecies = np.where(block.shape == 1)[1]
        for l in range(len(shape_i_indecies)):
            shape_indecies.append((shape_j_indecies[l], shape_i_indecies[l]))
        if len(indecies[0]) > 0 and len(indecies[1]) > 0:
            y_pos = indecies[0][0] - block.shape_rows
            stopped = False
            while not stopped:
                for j in range(block.shape_rows):
                    for i in range(block.shape_cols):
                        if block.shape[j][i] == 1:
                            if j + y_pos + 1 == grid.rows:
                                shadow_block_y_pos = y_pos
                                stopped = True
                            elif shadow_grid[j + y_pos + 1][i] == 1 and (j + 1, i) not in shape_indecies:
                                shadow_block_y_pos = y_pos
                                stopped = True
                y_pos += 1
        else:
            shadow_block_y_pos = grid.rows - block.shape_rows
        shadow_grid[shadow_block_y_pos: shadow_block_y_pos + block.shape_rows, :] += block.shape
        for j in range(shadow_grid_rows):
            for i in range(shadow_grid_cols):
                if shadow_grid[j][i] == 1:
                    pg.draw.rect(screen, shadow_color, [(i + shadow_block_x_pos) * self.x_offset, j * self.y_offset + self.top_panal_height, self.x_offset, self.y_offset])

    def erase_completed_rows(self):
        completed_rows_indecies = []
        grid_copy = self.grid.copy()
        completed_row = np.ones(self.cols)
        for row in range(self.rows):
            if (self.grid[row] == completed_row).all():
                grid_copy[row] *= 0
                completed_rows_indecies.append(row)
        completed_rows_num = len(completed_rows_indecies)
        if completed_rows_num == 0:
            return
        for i in range(self.rows):
            if (completed_rows_num - 1) < i <= completed_rows_indecies[-1]:
                self.grid[i] = grid_copy[i - completed_rows_num]
            elif i > completed_rows_indecies[-1]:
                self.grid[i] = grid_copy[i]
            else:
                self.grid[i] = np.zeros(self.cols)
        self.update_score(completed_rows_num)

    def update_score(self, completed_rows_num):
        score_increment = 100
        if completed_rows_num == 2:
            score_increment = 300
        elif completed_rows_num == 3:
            score_increment = 500
        elif completed_rows_num == 4:
            score_increment = 800
        self.score += score_increment

    def next_color(self):
        colors = [red, blue, light_blue, green, orange, purple]
        next_color = random.choice(colors)
        return next_color

    def next_block(self):
        block_shapes = [
            [[1,1,1,1]],
            [[1,1],[1,1]],
            [[1,1,1],[0,1,0]],
            [[0,0,1],[1,1,1]],
            [[1,0,0],[1,1,1]],
            [[0,1,1],[1,1,0]],
            [[1,1,0],[0,1,1]]
        ]
        next_block = np.array(random.choice(block_shapes))
        return next_block

    def reset_grid(self):
        self.grid *= 0

    def reset_score(self):
        self.score = 0


class Block():
    def __init__(self, next_block, next_color, wait_time):
        self.shape = next_block
        self.color = next_color
        self.stopped = False
        self.wait_time = wait_time
        self.shape_rows, self.shape_cols = self.shape.shape
        self.x_pos = int(grid.cols / 2) - 1
        self.y_pos = 0
        self.start_time = 0
        self.down = True
        self.right = True
        self.left = True
        self.grid = np.zeros((grid.rows, grid.cols))
        self.add_block_new_pos()

    def add_new_block(self, next_block, next_color, wait_time):
        new_block = Block(next_block, next_color, wait_time)
        blocks.append(new_block)

    def stop_block(self):
        self.down = False
        self.right = False
        self.left = False
        self.stopped = True

    def update_block_shape(self):
        self.shape_rows, self.shape_cols = self.shape.shape

    def add_block_new_pos(self):
        indecies = np.where(self.shape == 1)
        for i in range(len(indecies[0])):
            grid.grid[indecies[0][i] +
                      self.y_pos][indecies[1][i] + self.x_pos] = 1
            self.grid[indecies[0][i] +
                      self.y_pos][indecies[1][i] + self.x_pos] = 1

    def delete_block_past_pos(self):
        indecies = np.where(self.shape == 1)
        for i in range(len(indecies[0])):
            grid.grid[indecies[0][i] +
                      self.y_pos][indecies[1][i] + self.x_pos] = 0
            self.grid[indecies[0][i] +
                      self.y_pos][indecies[1][i] + self.x_pos] = 0

    def check_adjacent_blocks(self):
        if self.stopped:
            return
        if self.y_pos + self.shape_rows >= grid.rows:
            self.stopped = True
            return
        mask_rows_limit_index = grid.rows
        mask_cols_limit_index = grid.cols
        mask_rows_start_index = self.y_pos
        mask_cols_start_index = self.x_pos - 1
        mask_rows_end_index = self.y_pos + self.shape_rows + 1
        mask_cols_end_index = self.x_pos + self.shape_cols + 1
        if mask_cols_end_index > mask_cols_limit_index:
            mask_cols_end_index = mask_cols_limit_index
        if mask_cols_start_index < 0:
            mask_cols_start_index = 0
        mask = grid.grid[mask_rows_start_index: mask_rows_end_index, mask_cols_start_index: mask_cols_end_index].copy()
        mask_rows, mask_cols = mask.shape
        self.down = True
        self.right = True
        self.left = True
        j_indecies = np.where(self.shape == 1)[0]
        i_indecies = np.where(self.shape == 1)[1]
        indecies = []
        for l in range(len(i_indecies)):
            indecies.append((j_indecies[l], i_indecies[l]))
        for j in range(self.shape_rows):
            for i in range(self.shape_cols):
                right_offset = 2
                left_offset = 1
                if self.shape[j][i] == 1:
                    # Touching the right edge of the grid
                    if self.x_pos + self.shape_cols == grid.cols:
                        left_offset = 1
                    elif self.x_pos == 0:
                        left_offset = 0
                    if mask_cols == self.shape_cols + 1:
                        right_offset = 1
                    if mask[j][i + right_offset] == 1 and (i + 1) not in np.where(self.shape == 1)[1]:
                        self.right = False
                    if mask[j][i] == 1 and (i - 1) not in np.where(self.shape == 1)[1]:
                        self.left = False
                    if mask[j + 1][i + left_offset] == 1 and (j + 1, i) not in indecies:
                        self.down = False
                        if (self.y_pos + self.shape_rows) == self.shape_rows:
                            gameover()
        if not self.down:
            self.stopped = True

    def update_block_grid(self, block, grid_copy):
        completed_rows_indecies = []
        completed_row = np.ones(grid.cols)
        block_grid_copy = block.grid.copy()
        for row in range(grid.rows):
            if (grid_copy[row] == completed_row).all():
                block_grid_copy[row] *= 0
                completed_rows_indecies.append(row)
        completed_rows_num = len(completed_rows_indecies)
        if completed_rows_num == 0:
            return
        for i in range(grid.rows):
            if (completed_rows_num - 1) < i <= completed_rows_indecies[-1]:
                block.grid[i] = block_grid_copy[i - completed_rows_num]
            elif i > completed_rows_indecies[-1]:
                block.grid[i] = block_grid_copy[i]
            else:
                block.grid[i] = np.zeros(grid.cols)

    def gravity(self):
        if self.stopped:
            return
        delta_time = (pg.time.get_ticks() - self.start_time) / 1000
        if delta_time >= self.wait_time:
            self.move_block('down')
            self.start_time = pg.time.get_ticks()

    def fall_down(self):
        self.delete_block_past_pos()
        grid_copy = grid.grid[0: grid.rows, self.x_pos: self.x_pos + self.shape_cols].copy()
        grid_copy[0: self.y_pos, self.x_pos: self.x_pos + self.shape_cols] *= 0
        indecies = np.where(grid_copy == 1)
        shape_indecies = []
        shape_j_indecies = np.where(self.shape == 1)[0]
        shape_i_indecies = np.where(self.shape == 1)[1]
        for l in range(len(shape_i_indecies)):
            shape_indecies.append((shape_j_indecies[l], shape_i_indecies[l]))
        if len(indecies[0]) > 0 and len(indecies[1]) > 0:
            y_pos = indecies[0][0] - self.shape_rows
            stopped = False
            while not stopped:
                for j in range(self.shape_rows):
                    for i in range(self.shape_cols):
                        if self.shape[j][i] == 1:
                            if j + y_pos + 1 == grid.rows:
                                self.y_pos = y_pos
                                stopped = True
                            elif grid_copy[j + y_pos + 1][i] == 1 and (j + 1, i) not in shape_indecies:
                                self.y_pos = y_pos
                                stopped = True
                y_pos += 1
        else:
            self.y_pos = grid.rows - self.shape_rows
        self.add_block_new_pos()

    def rotate_block(self):
        self.delete_block_past_pos()
        if self.shape_rows + self.x_pos > grid.cols or self.shape_cols + self.y_pos > grid.rows:
            self.add_block_new_pos()
            return
        self.shape = np.rot90(self.shape, 1)
        self.update_block_shape()
        self.add_block_new_pos()

    def move_block(self, direction):
        self.delete_block_past_pos()
        if direction == 'down' and self.down:
            self.move_block_down()
        elif direction == 'right' and self.right:
            self.move_block_right()
        elif direction == 'left' and self.left:
            self.move_block_left()
        self.add_block_new_pos()

    def move_block_down(self):
        if self.y_pos + self.shape_rows < grid.rows:
            self.y_pos += 1

    def move_block_right(self):
        if self.x_pos + self.shape_cols < grid.cols:
            self.x_pos += 1

    def move_block_left(self):
        if self.x_pos > 0:
            self.x_pos -= 1


def increase_difficulity():
    global wait_time
    if grid.score >= 6000:
        wait_time = 0.3
    elif grid.score >= 5000:
        wait_time = 0.35
    elif grid.score >= 4500:
        wait_time = 0.4
    elif grid.score >= 3000:
        wait_time = 0.5
    elif grid.score >= 2000:
        wait_time = 0.65
    elif grid.score >= 1000:
        wait_time = 0.75
    elif grid.score >= 500:
        wait_time = 0.8


def gameover():
    global playing, game_over
    playing = False
    game_over = True


def restart():
    global blocks
    wait_time = 0.9
    next_block = grid.next_block()
    next_color = grid.next_color()
    for block in blocks:
        block.delete_block_past_pos()
    grid.reset_grid()
    grid.reset_score()
    blocks = []
    blocks.append(Block(next_block, next_color, wait_time))
    next_block = grid.next_block()
    next_color = grid.next_color()


def update_highest_score():
    global highest_score
    if not path.exists('highest_score.json'):
        with open('highest_score.json', 'w') as f:
            json.dump(0, f)
    with open('highest_score.json', 'r') as f:
        highest_score = json.load(f)
    if highest_score < grid.score:
        highest_score = grid.score
        with open('highest_score.json', 'w') as f:
            json.dump(highest_score, f)
    else:
        with open('highest_score.json', 'r') as f:
            highest_score = json.load(f)


pg.init()
screen_width = 400
screen_height = 2 * screen_width + 100
cols = 10
screen = pg.display.set_mode((screen_width, screen_height))
pg.display.set_caption('Tetris')
clock = pg.time.Clock()
fps = 60
font_size = 25
font = pg.font.Font('E:/Coding Projects/Python Projects/Tetris/Fonts/Roboto-Bold.ttf', font_size)

# Colors
white = (250, 250, 250)
red = (238, 21, 1)
shadow_red = (251, 192, 187)
blue = (0, 79, 163)
shadow_blue = (179, 202, 227)
light_blue = (0, 151, 183)
shadow_light_blue = (179, 224, 233)
green = (0, 158, 42)
shadow_green = (179, 226, 191)
orange = (193, 125, 3)
shadow_orange = (236, 217, 179)
purple = (125, 18, 140)
shadow_purple = (216, 184, 221)
grey = (216, 216, 216)
black = (0, 0, 0)
bg_color = white
grid_color = black

# Initailizing variables
grid = Grid(cols, grid_color)
next_block = grid.next_block()
next_color = grid.next_color()
wait_time = 0.9
first_block = Block(next_block, next_color, wait_time)
blocks = [first_block]
next_block = grid.next_block()
next_color = grid.next_color()
playing = False
paused = False
starting = True
game_over = False

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()
        if event.type == pg.KEYDOWN:
            if playing:
                if event.key == pg.K_DOWN:
                    blocks[-1].fall_down()
                elif event.key == pg.K_UP:
                    blocks[-1].rotate_block()
                elif event.key == pg.K_RIGHT:
                    blocks[-1].move_block('right')
                elif event.key == pg.K_LEFT:
                    blocks[-1].move_block('left')
                elif event.key == pg.K_SPACE:
                    paused = True
                    playing = False
            elif paused:
                if event.key == pg.K_SPACE:
                    paused = False
                    playing = True
            else:
                if event.key == pg.K_RETURN:
                    playing = True
                    game_over = False
                    starting = False
                    next_block = grid.next_block()
                    next_color = grid.next_color()
                    restart()
            if event.key == pg.K_ESCAPE:
                pg.quit()
                exit()
    if playing:
        screen.fill(bg_color)
        grid.display_shadow_block(blocks[-1])
        blocks[-1].check_adjacent_blocks()
        blocks[-1].gravity()
        grid_copy = grid.grid.copy()
        if blocks[-1].stopped:
            blocks[-1].stop_block()
            grid.erase_completed_rows()
            increase_difficulity()
            blocks[-1].add_new_block(next_block, next_color, wait_time)
            next_block = grid.next_block()
            next_color = grid.next_color()
        for block in blocks:
            # if len(blocks) > 0:
            block.update_block_grid(block, grid_copy)
            grid.display_block(block)
        grid.display_grid()
        grid.display_score()
        grid.display_next_block(next_block, next_color)
        pg.display.flip()
        clock.tick(fps)
    elif paused:
        screen.fill(bg_color)
        grid.display_shadow_block(blocks[-1])
        for block in blocks:
            grid.display_block(block)
        grid.display_grid()
        grid.display_score()
        grid.display_next_block(next_block, next_color)
        pg.draw.rect(screen, black, [0, int(screen_height/2) - 50, screen_width, 100])
        text_surf_1 = font.render('Paused', False, red)
        text_rect_1 = text_surf_1.get_rect(center=((int(screen_width/2)), int(screen_height/2)-20))
        text_surf_2 = font.render('press Space to resume', False, green)
        text_rect_2 = text_surf_2.get_rect(center=((int(screen_width/2)), int(screen_height/2)+20))
        screen.blit(text_surf_1, text_rect_1)
        screen.blit(text_surf_2, text_rect_2)
        pg.display.flip()
        clock.tick(fps)
    elif game_over:
        update_highest_score()
        screen.fill(bg_color)
        for block in blocks:
            grid.display_block(block)
        grid.display_grid()
        grid.display_highest_score(highest_score)
        grid.display_score()
        pg.draw.rect(screen, black, [0, int(screen_height/2) - 50, screen_width, 100])
        game_over_text_surf = font.render('Game Over', False, red)
        game_over_text_rect = game_over_text_surf.get_rect(center=((int(screen_width/2)), int(screen_height/2)-20))
        play_again_text_surf = font.render('press Enter to play again', False, green)
        play_again_text_rect = play_again_text_surf.get_rect(center=((int(screen_width/2)), int(screen_height/2)+20))
        screen.blit(game_over_text_surf, game_over_text_rect)
        screen.blit(play_again_text_surf, play_again_text_rect)
        pg.display.flip()
        clock.tick(fps)
    elif starting:
        update_highest_score()
        screen.fill(bg_color)
        grid.display_grid()
        grid.display_highest_score(highest_score)
        pg.draw.rect(screen, black, [0, int(screen_height/2) - 50, screen_width, 100])
        text_surf = font.render('Press Enter to Play', False, light_blue)
        text_rect = text_surf.get_rect(center=((int(screen_width/2)), int(screen_height/2)))
        screen.blit(text_surf, text_rect)
        pg.display.flip()
        clock.tick(fps)
