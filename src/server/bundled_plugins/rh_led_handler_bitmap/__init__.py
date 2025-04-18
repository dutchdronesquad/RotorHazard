'''LED visual effects'''

# To use this LED-panel plugin see:
#   https://github.com/RotorHazard/RotorHazard/blob/main/doc/Software%20Setup.md#led-panel-support

import logging
from eventmanager import Evt
from led_event_manager import LEDEffect, Color, effect_delay

logger = logging.getLogger(__name__)

try:
    from PIL import Image
except ModuleNotFoundError as ex:
    logger.debug(str(ex) + " ('pillow' module needed to use '" + __name__ + "')")
    raise ModuleNotFoundError("'pillow' module not found") from ex

class BitmapEffects():
    def __init__(self, rhapi):
        self._rhapi = rhapi

    def showBitmap(self, args):
        if 'strip' in args:
            strip = args['strip']
        else:
            return False

        def setPixels(img, panel_w):
            pos = 0
            for row in range(0, img.height):
                for col in range(0, img.width):
                    if pos >= strip.numPixels():
                        return

                    c = col
                    if args['RHAPI'].config.get('LED', 'INVERTED_PANEL_ROWS'):
                        if row % 2 == 0:
                            c = (panel_w - 1) - col

                    px = img.getpixel((c, row))
                    strip.setPixelColor(pos, Color(px[0], px[1], px[2]))
                    pos += 1

        bitmaps = args['bitmaps']
        if bitmaps and bitmaps is not None:
            for bitmap in bitmaps:
                img = Image.open(bitmap['image'])
                delay = bitmap['delay']

                panel_w = args['RHAPI'].config.get('LED', 'LED_COUNT', as_int=True) // args['RHAPI'].config.get('LED', 'LED_ROWS', as_int=True)
                panel_h = args['RHAPI'].config.get('LED', 'LED_ROWS', as_int=True)

                if args['RHAPI'].config.get('LED', 'PANEL_ROTATE', as_int=True) % 2:
                    output_w = panel_h
                    output_h = panel_w
                else:
                    output_w = panel_w
                    output_h = panel_h

                size = img.size

                ratio_w = output_w / size[0]
                ratio_h = output_h / size[1]

                ratio = min(ratio_w, ratio_h)

                img = img.resize((int(size[0]*ratio), int(size[1]*ratio)))

                output_img = Image.new(img.mode, (output_w, output_h))
                size = img.size
                pad_left = int((output_w - size[0]) / 2)
                pad_top = int((output_h - size[1]) / 2)
                output_img.paste(img, (pad_left, pad_top))
                output_img = output_img.rotate(90 * args['RHAPI'].config.get('LED', 'PANEL_ROTATE', as_int=True), expand=True)

                setPixels(output_img, panel_w)
                strip.show()
                effect_delay(delay, args)

    def register_handlers(self, args):
        for led_effect in [
            LEDEffect("Image: RotorHazard", self.showBitmap, {
                    'recommended': [Evt.STARTUP]
                }, {
                    'bitmaps': [
                        {'image': self._rhapi.server.program_dir + '/static/image/LEDpanel-16x16-RotorHazard.png', 'delay': 0}
                        ],
                    'time': 60
                },
                name='bitmapRHLogo',
            ),
            LEDEffect("Image: Orange Ellipsis", self.showBitmap, {
                    'recommended': [Evt.RACE_STAGE]
                }, {
                    'bitmaps': [
                        {'image': self._rhapi.server.program_dir + '/static/image/LEDpanel-16x16-ellipsis.png', 'delay': 0}
                        ],
                    'time': 8
                },
                name='bitmapOrangeEllipsis',
            ),
            LEDEffect("Image: Green Upward Arrow", self.showBitmap, {
                    'recommended': [Evt.RACE_START]
                }, {
                    'bitmaps': [
                        {'image': self._rhapi.server.program_dir + '/static/image/LEDpanel-16x16-arrow.png', 'delay': 0}
                        ],
                    'time': 8
                },
                name='bitmapGreenArrow',
            ),
            LEDEffect("Image: Red X", self.showBitmap, {
                    'recommended': [Evt.RACE_STOP]
                }, {
                    'bitmaps': [
                        {'image': self._rhapi.server.program_dir + '/static/image/LEDpanel-16x16-X.png', 'delay': 0}
                        ],
                    'time': 8
                },
                name='bitmapRedX',
            ),
            LEDEffect("Image: Checkerboard", self.showBitmap, {
                    'recommended': [Evt.RACE_FINISH, Evt.RACE_STOP]
                }, {
                    'bitmaps': [
                        {'image': self._rhapi.server.program_dir + '/static/image/LEDpanel-16x16-checkerboard.png', 'delay': 0}
                        ],
                'time': 20
                },
                name='bitmapCheckerboard',
            )
        ]:
            args['register_fn'](led_effect)

def initialize(rhapi):
    bitmap_effects = BitmapEffects(rhapi)
    rhapi.events.on(Evt.LED_INITIALIZE, bitmap_effects.register_handlers)

