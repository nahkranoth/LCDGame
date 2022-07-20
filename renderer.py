import world
import time,sys


class Renderer(object):
    DISPLAY_TEXT_ADDR = 0x3e

    def __init__(self):
        if sys.platform == 'uwp':
            import winrt_smbus as smbus
            self.bus = smbus.SMBus(1)
        else:
            import smbus
            import RPi.GPIO as GPIO
            rev = GPIO.RPI_REVISION
            if rev == 2 or rev == 3:
                self.bus = smbus.SMBus(1)
            else:
                self.bus = smbus.SMBus(0)

        self.command(0x08 | 0x04)  # display on, no cursor
        self.command(0x28)  # display on, no cursor
        print('init renderer')

    def command(self, cmd):
        self.bus.write_byte_data(self.DISPLAY_TEXT_ADDR, 0x80, cmd)

    def create_char(self, locat, pattern):
        """
        Writes a bit pattern to LCD CGRAM
        Arguments:
        location -- integer, one of 8 slots (0-7)
        pattern -- byte array containing the bit pattern, like as found at
                   https://omerk.github.io/lcdchargen/
        """
        locat &= 0x07  # Make sure location is 0-7
        self.command(0x40 | (locat << 3))
        self.bus.write_i2c_block_data(self.DISPLAY_TEXT_ADDR, 0x40, pattern)

    def finish_bootload(self):
        self.bus.write_byte_data(self.DISPLAY_TEXT_ADDR, 0x80, 0x80)  # done loading into buff mem

    def draw(self, buffer):
        self.command(0x01)  # clear screen
        for idx, tile in enumerate(buffer):
            if idx == 16:
                self.command(0xc0)  # next line
            self.bus.write_byte_data(self.DISPLAY_TEXT_ADDR, 0x40, tile)


if __name__ == "__main__":
    world = world.World()
    renderer = Renderer()
    renderer.draw(world.merged())
