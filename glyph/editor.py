# Copyright (c) 2011, Chandler Armstrong (omni dot armstrong at gmail dot com)
# see LICENSE.txt for details



from collections import deque
from pygame import Rect, Surface
from pygame import font
from pygame.font import Font
from pygame.sprite import Sprite
from pygame.locals import *
import re



######################################################################
# inits
font.init()



######################################################################
# constants
DIRECTION_KEYS = [K_UP, K_DOWN, K_LEFT, K_RIGHT]
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
FONT = Font(None, 8)



######################################################################
# functions
def _iswhitespace(char):
    # determine if char is whitespace
    # accepts a char, if char is not a string then it is always
    # considered whitespace
    # returns true if char is whitespace, else returns false
    whitespace = re.compile('\s+') # re to detect whitespace
    if isinstance(char, str):
        assert len(char) == 1
        if whitespace.search(char): return True
        return False
    return False



class _Line(object):


    def __init__(self, image, rect):
        self.image = image
        self.rect = rect


    def clear(self, surface_dest, background):
        # draws background over surface_dest using self.rect
        # accepts surface_dest: the destination surface that self.image has
        # been drawn to
        # background: the background to draw over the areas that self.image was
        # drawn to on surface_dest
        # returns nothing
        rect = self.rect
        self.image = Surface(rect.size)
        surface_dest.blit(background, rect, rect)



######################################################################
class EditorGroup(dict):
    """a dictionary that assumes editors as values.  adds methods to retrieve
    editors given a position"""


    def get_focus(self, pos):
        for k, v in self.items():
            if v.rect.collidepoint(pos): return k, v
        return None, None



class Editor(object):


    def __init__(self, rect, txt=None,
                 bkg=BLACK, color=WHITE, font=FONT, spacing=0):
        self.image = Surface(rect.size)
        self._image = Surface(rect.size)
        self.rect = rect
        if txt is None: self.txt = [' ']
        else: self.txt = txt
        self._lines = [_Line(Surface((0, 0)), Rect(0, 0, 0, 0))]
        self._wraps = [0]
        self._cursor = 0
        self._dest = Rect(0, 0, 0, 0)
        self.bkg = bkg
        self.color = color
        self.font = font
        self.spacing = spacing


    def get_cursor(self):
        """
        get a rect representing the position of the cursor on the editor image
        """
        k, font, txt = self._cursor, self.font, self.txt
        index2pixel = self._index2pixel

        return Rect(index2pixel(k), font.size(txt[k]))


    def clear(self):
        """clear the editor image of all lines and reset the cursor"""
        lines = self._lines
        image, bkg_image = self.image, self._image
        for line in lines: line.clear(image, bkg_img)
        self._cursor = 0


    def _index2line(self, i):
        wraps = self._wraps

        for l, wrap in enumerate(wraps):
            if wrap > i: return l - 1

        return len(wraps) - 1


    def _index2pixel(self, i):
        font, lines, txt = self.font, self._lines, self.txt
        wraps = self._wraps + [len(txt)]
        index2line = self._index2line

        l = index2line(i)

        x = font.size(''.join(txt[wraps[l]:i]))[0]
        y = lines[l].rect.y

        return x, y


    def _pixel2index(self, pixel):
        font, txt, wraps = self.font, self.txt, self._wraps
        pixel2line = self._pixel2line

        l = pixel2line(pixel)
        if l == len(wraps) - 1: m, n = wraps[l], len(txt)

        else: m, n = wraps[l:l + 2]

        pixel_x = pixel[0]
        d = deque([0, 0], 2)
        for i in xrange(m, n):
            font_size_x = font.size(''.join(txt[m:i]))[0]
            d.append(font_size_x)
            if font_size_x > pixel_x: break

        l = [abs(font_size_x - pixel_x) for font_size_x in d]

        if l.index(min(l)) == 1: return i

        return i - 1


    def _pixel2line(self, pixel):
        lines = self._lines

        for l, line in enumerate(lines):
            if line.rect.y > pixel[1]: return l - 1

        return l


    def _draw_line(self, l):
        image, lines = self.image, self._lines

        line = lines[l]
        image.blit(line.image, line.rect)


    def redraw(self):
        image, lines = self.image, self._lines
        for line in lines: image.blit(line.image, line.rect)


    def input(self, event):
        """
        accept a user KEYDOWN event and add the text associated with the
        keypress to the editor image

        event-- a user KEYDOWN event

        return None
        """
        k, font, lines = self._cursor, self.font, self._lines
        rect_w, txt, wraps = self.rect.w, self.txt, self._wraps
        image, bkg_img = self.image, self._image
        draw_line, index2line = self._draw_line, self._index2line
        pixel2index, update = self._pixel2index, self._update
        Line = _Line

        if event.type == KEYDOWN:
            l = index2line(k)

            # handle cursor navigation
            if event.key in DIRECTION_KEYS:
                draw_line(l) #to clear the cursor?
                if event.key == K_UP:
                    if l > 0:
                        pixel = (font.size(''.join(txt[wraps[l]:k]))[0],
                                 lines[l - 1].rect.y)
                        self._cursor = pixel2index(pixel)

                    else: self._cursor = 0

                elif event.key == K_DOWN:
                    if (len(wraps) - 1) > l:
                        pixel = (font.size(''.join(txt[wraps[l]:k]))[0],
                                 lines[l + 1].rect.y)
                        self._cursor = pixel2index(pixel)

                    else: self._cursor = len(txt) - 1

                elif event.key == K_LEFT:
                    self._cursor -= 1
                    if self._cursor < 0: self._cursor = 0

                elif event.key == K_RIGHT:
                    self._cursor += 1
                    if self._cursor > (len(txt) - 1):
                        self._cursor = len(txt) - 1

            # handle newlines
            elif event.key == K_RETURN:
                txt.insert(k, '\n')
                self._cursor += 1
                lines.insert(l + 1, Line(Surface((0, 0)), Rect(0, 0, 0, 0)))
                update(l)

            # handle backspaces
            elif event.key == K_BACKSPACE:
                if k == 0: pass

                else:
                    lines[l].clear(image, bkg_img)
                    self._cursor -= 1
                    k = self._cursor
                    char = txt.pop(k)
                    # if l> index2line(k) then the line no longer exists
                    if l > index2line(k): del lines[l]
                    if l == 0: update(l)
                    else: update(l - 1)

            # handle ascii input
            else:
                if event.unicode:
                    txt.insert(k, event.unicode.encode("ascii"))
                    self._cursor += 1
                    if k == wraps[l]: # wrapped to a new line
                        if l == 0: update(l) # update line
                        else: update(l - 1)  # else: update from previous line
                    else: update(l)


    ##################################################################
    def _tokenize(self, txt):
        charbuff = []
        for char in txt:
            if _iswhitespace(char):
                if charbuff: yield ''.join(charbuff)
                charbuff = []
                yield char

            else: charbuff.append(char)

        if charbuff: yield ''.join(charbuff)


    def _update(self, l):
        bkg, color, font = self.bkg, self.color, self.font
        spacing, dest, rect_w = self.spacing, self._dest, self.rect.w
        bkg_img, image = self._image, self.image
        lines, txt, wraps = self._lines, self.txt, self._wraps
        tokenize = self._tokenize
        Line = _Line

        tokens = tokenize(txt[wraps[l]:])
        dest.y = sum(line.image.get_height() + spacing for line in lines[:l])
        wraps = wraps[:l + 1]
        k = wraps[-1]
        linebuff = []
        L = [l] # a list of updated lines
        for token in tokens:
            if token == '\n':
                k += 1 # increment k (so the \n will be on this line)
                wraps.append(k)
                # a space is the visual representation of the \n character
                linebuff.append(' ')
                _linebuff = []

            elif font.size(''.join(linebuff + [token]))[0] < rect_w:
                k += len(token)
                linebuff.append(token)
                continue

            else:
                wraps.append(k) # k is the position of the previous space token
                k += len(token)
                _linebuff = [token]
                lines.insert(l + 1, Line(Surface((0, 0)), Rect(0, 0, 0, 0)))

            line = font.render(''.join(linebuff), 0, color, bkg)
            line = Line(line, Rect(dest.topleft, line.get_size()))
            lines[l].clear(image, bkg_img)
            lines[l] = line

            dest.y += line.image.get_height() + spacing
            linebuff = _linebuff
            l += 1
            L.append(l)

        line = font.render(''.join(linebuff), 0, color, bkg)
        line = Line(line, Rect(dest.topleft, line.get_size()))
        lines[l].clear(image, bkg_img)
        lines[l] = line

        for line in [lines[l] for l in L]: image.blit(line.image, line.rect)

        self._wraps = wraps
