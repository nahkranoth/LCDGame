
from world import World
from sound import Sound
from renderer import Renderer
import time
import grovepi


class Game(object):
    minimal_tick_step = 0.05
    initial_tick_step = 0.1
    tick_step = initial_tick_step
    curr_tick = 0

    prev_time = 0
    accum_dtime = 0
    d_time = 0

    buffer = []

    button_port = 2
    button_state = 0

    player_kill_flag = False
    player_alive = True

    custom_character_f1 = [ 0b00000,
                            0b00100,
                            0b01010,
                            0b00100,
                            0b11111,
                            0b00100,
                            0b01010,
                            0b01010]

    custom_character_f2 = [0b00000,
                           0b00100,
                           0b01010,
                           0b00100,
                           0b11111,
                           0b00100,
                           0b01010,
                           0b10001]

    custom_character_died = [0b00000,
                            0b10001,
                            0b01010,
                            0b00100,
                            0b01010,
                            0b10001,
                            0b00000,
                            0b00000]

    def __init__(self):
        self.player_alive = True
        self.player_kill_flag = False
        self.accum_time = 0
        self.world = World()
        self.world.generate_world()
        self.renderer = Renderer()
        self.sound = Sound()
        self.bootload()
        grovepi.pinMode(self.button_port, "INPUT")

    def bootload(self):
        self.buffer = self.world.merged()
        self.load_custom_in_mem()
        self.renderer.finish_bootload()

    def load_custom_in_mem(self):
        self.renderer.create_char(0, self.custom_character_f1)
        self.renderer.create_char(1, self.custom_character_f2)
        self.renderer.create_char(3, self.custom_character_died)

    def draw_player_character(self):
        player_state = 22
        if self.button_state == 1:
            player_state = 8

        if self.buffer[player_state] == self.world.rock:
            print('dead')
            self.player_kill_flag = True
            self.buffer[player_state] = 0x03
            return

        # draw player
        frame = self.curr_tick % 4
        if frame == 0:
            self.buffer[player_state] = 0x00
        else:
            self.buffer[player_state] = 0x01

    def draw_score(self):
        small = self.curr_tick / 10
        small_i = int(small)
        if small_i > 9:
            self.buffer[14] = ord(str(small_i)[0])
            self.buffer[15] = ord(str(small_i)[1])
        else:
            self.buffer[15] = ord(str(small_i))

    def reset(self):
        self.buffer = self.world.generate_world()
        self.tick_step = self.initial_tick_step
        self.curr_tick = 0
        self.accum_time = 0
        self.player_kill_flag = False
        self.player_alive = True
        self.draw_player_character()

    def run(self):
        while True:
            self.button_state = grovepi.digitalRead(self.button_port)
            self.prev_time = time.time()
            self.d_time = time.time() - self.prev_time
            self.accum_time = (self.accum_time + self.d_time)

            if self.accum_time > 0.0004:
                if not self.player_alive:
                    if self.button_state == 1:
                        print('reset ')
                        self.reset()
                    continue
                self.draw_player_character()
                self.draw_score()
                self.renderer.draw(self.buffer)
                self.buffer = self.world.step()

                self.accum_time = 0
                self.curr_tick = self.curr_tick + 1
                if self.player_kill_flag:
                    self.player_alive = False


if __name__ == "__main__":
    game = Game()
    game.run()
