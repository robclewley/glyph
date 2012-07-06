# Copyright (c) 2011, Chandler Armstrong (omni dot armstrong at gmail dot com)
# see LICENSE.txt for details




from __future__ import division
import re
from collections import defaultdict, deque
import os

from pygame import font
from pygame.event import Event
from pygame.font import Font
from pygame.rect import Rect
from pygame.sprite import Sprite
from pygame import Surface
from pygame.transform import scale
from pygame.locals import *

from .editor import Editor




######################################################################
# inits
font.init()




######################################################################
# constants
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
FONT = Font(None, 8)
SPECIALS = ['/', '{', '}']
WHITESPACE = {'n' : '\n'}




######################################################################
# globals
Macros = {}




######################################################################
# private functions
def _iswhitespace(char):
    # determine if char is whitespace
    # accepts a char, if char is not a string then it is always
    # considered whitespace
    # returns true if char is whitespace, else returns false
    whitespace = re.compile('\s+') # re to detect whitespace
    if not char: return True
    if isinstance(char, str) or isinstance(char, unicode):
        assert len(char) == 1
        if whitespace.search(char): return True
        return False
    return False



def _scale_token(token, (width, height)):
    # scale token to width and height
    # accepts token object and a (width, height) argument
    # returns a new token object scaled to width and height
    Token = _Token

    links = token.links
    token_iswhitespace, token_str = token.iswhitespace, token.str
    surfs = [scale(token, (width, height))]

    ratio_w = width / token.get_width()
    ratio_h = height / token.get_height()

    # given token height, modify link rect y
    shift_x = 0
    for rect in [rect for v in links.values() for rect in v]:
        rect_w = rect.w
        rect.w *= ratio_w
        rect.h *= ratio_h
        rect.x += shift_x
        rect.y += (height - rect.h)    
        shift_x = rect.w - rect_w

    return Token((width, height), links, surfs, token_iswhitespace, token_str)



def _token_builder(interpreted_txt):
    # build a token from interpreted text
    # accepts an interpreted text list
    # returns a token object
    iswhitespace = _iswhitespace
    Token = _Token

    links = defaultdict(list)

    token_iswhitespace = True

    surfs, x, y = [], 0, 0
    for (envs, chars) in interpreted_txt:
        bkg, color, font = envs['bkg'], envs['color'], envs['font']
        strbuff, surfbuff = [], []
        for char in chars:
            if not iswhitespace(char): token_iswhitespace = False

            if char == '\n':
              char = Surface((0, font.get_linesize()))

            if isinstance(char, unicode):
                if iswhitespace(char): char = ' '
                strbuff.append(char)
            elif isinstance(char, str):
                if iswhitespace(char): char = ' '
                strbuff.append(char)            
            else:
                if strbuff:
                  surfbuff.append(font.render(''.join(strbuff), 1, color, bkg))
                surfbuff.append(char)
                strbuff = []
        
        if strbuff:
          surfbuff.append(font.render(''.join(strbuff), 1, color, bkg))

        if surfbuff:
            # calculate link rects
            link = envs['link']
            surfbuff_w = sum(surf.get_width() for surf in surfbuff)
            surfbuff_h = max(surf.get_height() for surf in surfbuff)
            links[link].append(Rect(x, 0, surfbuff_w, surfbuff_h))
            x += surfbuff_w
            # extend surfbuff to surfs and reset surfbuff
            surfs.extend(surfbuff)
            surfbuff = []

    # get token width and height
    width = sum(surf.get_width() for surf in surfs)
    height = max(surf.get_height() for surf in surfs)

    # given token height, modify link rect y
    for rect in [rect for v in links.values() for rect in v]:
        rect.y += (height - rect.h)
    token_str = ''.join(unicode(char) for (envs, chars) in interpreted_txt
                        for char in chars)

    return Token((width, height), links, surfs, token_iswhitespace, token_str)




######################################################################
# private classes
class _Token(Surface):
    # token object
    # links is a dictionary of link id strings keyed to the link rect on the
    #   token
    # iswhitespace is a boolean indicating if the token is whitespace
    # str is a string representing the token content


    def __init__(self, (width, height), links, surfs, iswhitespace, token_str):
        # construct a token object
        # (width, height) is the width and height of the token
        # links is a dictionary of link id strings keyed to the link rect on the
        #   token
        # surfs is a list of surfaces comprising the token
        # iswhitespace is a boolean indicating if the token is whitespace
        # token_str is a string representing the token
        self.links = links
        self.iswhitespace = iswhitespace
        self.str = token_str

        # construct Surface superclass
        Surface.__init__(self, (width, height))

        # blit each token onto self
        x = 0
        for surf in surfs:
            w, h = surf.get_size()
            y = height - h
            self.blit(surf, (x, y))
            x += w


    def __str__(self):
        return self.str



class _Line(Surface):
    # Line class


    def __init__(self, line, surf_w, justify):
        # renders a line (list of tokens)
        # accepts a line (list of tokens), width of line, and justification
        # returns Surface object with the tokens justified upon it given the
        #   justify argument
        self.line = line
        self.links = defaultdict(list)

        links = self.links
        scale_token = _scale_token

        # get the line width, line height, whitespace used in the line, and
        # freespace remaining in the line
        line_w = sum(token.get_width() for token in line)
        line_h = max(token.get_height() for token in line)
        total_whitespace = sum(token.get_width() for token in line
                               if token.iswhitespace)
        freespace = surf_w - line_w # the freespace available in the surface

        # initialize surface
        Surface.__init__(self, (surf_w, line_h))
        self.set_colorkey(BLACK)

        # set x
        if justify == 'right': x = freespace
        elif justify == 'center': x = freespace / 2
        else: x = 0

        # if justified: modify whitespace widths
        if justify == 'justified':
            # the amount to stretch whitespace
            stretch = 1.0 + (freespace / total_whitespace)

            sub_w = 0
            for i, token in enumerate(line):
                if token.iswhitespace:
                    # replace token with a scaled token
                    token_w = token.get_width() * stretch
                    scale_w = int(token_w)
                    sub_w += token_w % scale_w
                    while sub_w > 1:
                        sub_w -= 1
                        scale_w += 1
                    line[i] = scale_token(token, (scale_w, token.get_height()))

        for token in line:
            w, h = token.get_size()
            y = (line_h - h) # token y
            self.blit(token, (x, y))

            for link in token.links:
                for rect in token.links[link]:
                    # move rect to token's position in line and append to links
                    links[link].append(rect.move(x, y))

            x += w # update x with object width


    def __str__(self):
        return ''.join(str(token) for token in self.line)



######################################################################
# public classes
class GlyphGroup(dict):
    """a dictionary that assumes Glyphs as values.  adds methods to get links
    from all Glyphs in the group"""

    def get_collisions(pos):
        for k, v in self:
            link =  v.get_collisions(pos)
            if link: return k, link
        return None



class Glyph(object):
    """
    Main glyph class
    image-- the image that text is set to
    rect-- rect for blitting image to viewing surface
    spacing-- line spacing
    links-- dict of (link, [rects]) pairs
    """


    ##################################################################
    # class methods
    def __init__(self, rect, bkg=BLACK, color=WHITE, font=FONT, spacing=0):
        """
        Initialize a glyph object

        rect-- rect object for positioning glyph image on viewing surface
        **kwargs-- dictionary of (env_id, value) pairs
          required kwargs are:
          bkg-- background color
          color-- font color
          font-- font
        """
        # initialize
        self.image = Surface(rect.size)
        self.image.fill(bkg)
        self.image.set_alpha(255)
        self._bkg = bkg
        self.rect = rect
        self.spacing = spacing
        self.links = defaultdict(list)
        # FUTURE ###
        self.editors = {}
        ############
        self._dest = Rect(0, 0, 0, 0) # rect to blit a txt line to image surface
        # list of (env_id, value) pairs for environments;
        # _envs is used as a stack data structure
        self._envs = [('bkg', bkg),
                      ('color', color),
                      ('font', font),
                      ('link', None)] # link id string

        self._buff = deque() # rendered text buffer


    ##################################################################
    # helper methods
    def __read_env(self, _txt_):
        # interprets and returns an environment.  environments set text
        # characteristics such as color or links.
        # accepts the _txt_ iterable at an environment starting point
        # return (environment type, environment) tuple (e.g (font, Font object))

        # re to get env arguments (arguments may be paths and contain \ or /)
        r = re.compile('(\w+)(?:\s+([\w\s\.,=\\\\/]+))?\s*;')
        charbuffer = ''
        # _txt_ is a generator, so iterating consumes the contents for the
        # references to _txt_ in the _interpret function
        for i, char in _txt_:
            charbuffer += char
            s = r.search(charbuffer) # search for environment name arguments
            if s: # if search successful
                env = s.groups() # get environment
                env_ = env[0]
                if env_ in Macros: return Macros[env_]
                # new environment types must be added here

                elif env_ == 'bkg':
                    # return new backgroun color
                    return ('bkg', tuple([int(e) for e in env[1].split(',')]))

                elif env_ == 'color':
                    # return new font color
                    return ('color', tuple([int(e) for e in env[1].split(',')]))

                elif env_ == 'font':
                    # return new font
                    path, size = env[1].split(',') # the font location and size
                    return ('font', Font(os.path.realpath(path), int(size)))

                elif env_ == 'link':
                    # return new link
                    return ('link', env[1].strip())

                # FUTURE ###
                elif env_ == 'editor':
                    #editor is considered an environment because it must be
                    #linked.  any text in an editor environment is input to
                    #that editor, and any nested environments are ignored.
                    name, w = env[1].split(',') 
                    #extract editor kw args
                    kw = dict(self._envs)
                    del kw['link']
                    kw['spacing'] = self.spacing
                    h = kw['font'].get_linesize()
                    editor = Editor(Rect(0, 0, int(w), h), **kw)
                    self.editors[name] = editor 
                    # treat as link env, get_collision will sort 
                    return ('link', name)
                ############

                else:
                    raise ValueError(env[0] + ' is an unrecognized environment')


    # the space func could take a size and return a surface or rect...
    # really only need to shift tokens.  surfs do that without requiring tokens
    # to have rects
    def __read_func(self, _txt_):
        # interprets and returns a function.  functions are special surfaces or
        # objects.
        # accepts the _txt_ iterable at function starting point
        # returns (function type, function results) tuple
        #   (eg. (space, Surface obejct))
        r = re.compile('(\w+){(.*?)}')
        i, char = _txt_.next()

        if char in SPECIALS: return 'special', char
        if char in WHITESPACE: return 'whitespace', WHITESPACE[char]

        charbuff = char
        for i, char in _txt_:
            charbuff += char
            s = r.search(charbuff)
            if s:
                func, args = s.groups()
                if func in Macros: return func, Macros[func]

                if func == 'space': return func, Surface((int(args), 1))
                #"if charbuff = 'img'"?
                if func == 'img': return func, image.load(args).convert()


    ##################################################################
    # private methods
    def _interpret(self, txt):
        # iterprets glyph markup language
        # accepts string literal
        # returns a list of (env, charbuff) pairs,
        #   where env is a dictionary of environment types keyed to values and
        #   charbuff a list of text strings and the surfaces created from
        #   functions
        editors, envs = self.editors, self._envs
        read_env, read_func = self.__read_env, self.__read_func
        iswhitespace = _iswhitespace

        txt = txt.strip()
        # FUTURE ###
        # preamble, txt = read_preamble(txt)
        # if preamble: envs = preamble
        # ##########

        # initialize charbuff, renderbuff, interpreted text, and previous char
        charbuff, interpreted_txt, prevchar = [], [], ''
        _txt_ = enumerate(txt)
        for i, char in _txt_:
            if iswhitespace(char) and iswhitespace(prevchar):
                if char == '\n': charbuff[-1] = char
                continue

            if char == '/': # a function:
                func, char = read_func(_txt_)
                charbuff.append(char)
                prevchar = char

            elif char == '{': # a new environment has started
                # using dict(envs) allows new environments to overwrite default
                # environments, which are in the beginning of the list
                interpreted_txt.append((dict(envs), charbuff))
                charbuff = []
                envs.append(read_env(_txt_))

            elif char == '}': # an environment has ended
                # FUTURE ###
                link = dict(envs)['link']
                if link in editors:
                    editor = editors[link]
                    for char in charbuff:
                        mod = 0
                        if char.isupper(): mod = 3
                        event = Event(KEYDOWN, key=None, mod=mod,
                                      unicode=char.encode('utf8'))
                        editor.input(event)
                    interpreted_txt.append((dict(envs), [editor.image]))
                else: interpreted_txt.append((dict(envs), charbuff))
                #interpreted_txt.append((dict(envs), charbuff))
                charbuff = []
                envs.pop()

            else: # a normal, string, character
                charbuff.append(char)
                prevchar = char
        if charbuff: interpreted_txt.append((dict(envs), charbuff))
        return interpreted_txt


    def _tokenize(self, interpreted_txt):
        # tokenizes text
        # accepts (envs, charbuff)
        # returns a list of tokens
        iswhitespace, token_builder = _iswhitespace, _token_builder

        charbuff, _interpreted_txt, tokenized_txt = [], [], []
        for (envs, chars) in interpreted_txt:
            for char in chars:
                if iswhitespace(char):
                    if charbuff:
                        _interpreted_txt.append((envs, charbuff))
                        charbuff = []

                    if _interpreted_txt:
                        yield token_builder(_interpreted_txt)
                        _interpreted_txt = []

                    yield token_builder([(envs, [char])])

                else: charbuff.append(char)

            if charbuff:
                _interpreted_txt.append((envs, charbuff))
                charbuff = []
        if _interpreted_txt: yield token_builder(_interpreted_txt)


    def _wrap(self, tokenized_txt, justify):
        # wrap interpreted text to page width
        # accepts a list of Token objects tuples
        # returns a list of Line objects, each wrapped to self.rect
        Line = _Line
        rect_w = self.rect.w

        # linesize tracks the current size of the rendered line because moving
        # between environments will mean that there will be multiple surfaces
        # that need to be glued together
        line = [] # initialize line, and linesize
        for token in tokenized_txt:
            token_w = token.get_width()
            if token_w > rect_w:
                raise ValueError("The token '"+token.str+"' is "
                                 +str((token_w - rect_w))
                                 +" pixels too wide to fit in the rect passed.")

            # the token fits, process it and check if the line still fits inside
            # rect area, if not, append line without token, reinitialize line
            # with token
            line.append(token)
            if unicode(token) == '\n':
                # don't justify a line that would not wrap
                if justify == 'justified': _justify = 'left'
                else: _justify = justify

                yield Line(line, rect_w, _justify)
                line = [] # reset line

            elif sum(token.get_width() for token in line) > rect_w:
                token = line.pop()
                # remove single trailing whitespace
                if line[-1].iswhitespace: line = line[:-1]

                yield Line(line, rect_w, justify)
                line = [] # reinitialize _line, line, linesize, and num objects
                # do not append whitespace as the first token of the new line
                if not token.iswhitespace: line.append(token)

        if line:
            # don't justify a line that would not wrap
            if justify == 'justified': _justify = 'left'
            else: _justify = justify

            yield Line(line, rect_w, _justify)


    ##################################################################
    # public methods
    def input(self, txt, justify = None):
        """
        interprets, renders, wraps, and justifies input text

        txt -- raw text written with glyph markup
        justify -- a justify command; default is left justified
          left: left justified
          right: right justified
          justified: justified (both sides even)
          center: center justified

        returns nothing
        """
        buff, interpret, tokenize, wrap = (self._buff, self._interpret,
                                           self._tokenize, self._wrap)
        interpreted_txt = interpret(txt)
        tokens = tokenize(interpreted_txt)
        lines = wrap(tokens, justify)
        buff.extend(lines)


    def update(self):
        """
        updates the surface with the text input to the buffer by the input
        method, then deletes buffer

        accepts nothing

        returns nothing
        """
        buff, dest = self._buff, self._dest
        spacing = self.spacing
        image, rect = self.image, self.rect
        editors, links = self.editors, self.links

        while buff:
            line = buff.popleft()
            line_h = line.get_height()
            if dest.y + line_h > rect.h:
                buff.append(line)
                break
            else:
                image.blit(line, dest)

                for link in line.links:
                    for _rect in line.links[link]:
                        # move rect to token's pos on image and append to links
                        _rect.move_ip(dest.topleft)
                        #links[link].append(_rect.move(dest.topleft))
                        links[link].append(_rect)
                        # FUTURE ###
                        if link in editors: editors[link].rect = _rect
                        ############

                dest.y += line_h + spacing

        # FUTURE ###
        for editor in editors.values(): image.blit(editor.image, editor.rect)


    def clear(self, surface_dest, background):
        """
        draws background over surface_dest using self.rect and resets self._dest

        surface_dest-- the destination surface that self.image has been drawn to
        background-- the background to draw over the areas that self.image was
        drawn to on surface_dest

        returns nothing
        """
        rect = self.rect
        self.image = Surface(rect.size)
        self.image.fill(self._bkg)
        self._dest = Rect(0, 0, 0, 0)
        self.links = defaultdict(list)
        surface_dest.blit(background, rect, rect)


    def get_collisions(self, mpos):
        """
        get collisions between a point and the linked text on the glyph surface

        mpos-- the point to check against the linked text

        if a link collides with mpos
          returns the link collinding with mpos
        if no link collides with mpos
          returns None
        """
        editors, links, rect = self.editors, self.links, self.rect
        for link in links:
            for _rect in links[link]:
                if _rect.move(rect.topleft).collidepoint(mpos): return link



"""
    def scroll(self):
    # scrolls the surface and destination rect to accomodate text in the buffer
    # before updating
    # accepts nothing
    # returns nothing
        dest, image, spacing = self._dest, self.image, self.spacing
        h = sum(line.get_height() + spacing for line in self.buffer)
        dest.move_ip(0, -h)
        image.scroll(0, -h)
        update()
"""
