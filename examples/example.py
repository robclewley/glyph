import pygame
import os
from os import chdir
from os.path import dirname
from glyph import Editor, Glyph, Macros
from pygame import display
from pygame import draw
from pygame import event
from pygame.font import Font
from pygame import image
from pygame import mouse
from pygame import transform
from pygame.locals import *
pygame.init()



# path constants
DIRNAME = os.path.join(dirname(__file__), "resources",)
P_REG = os.path.join(DIRNAME, "font", "silkscreen.ttf")
P_BOLD = os.path.join(DIRNAME, "font", "silkscreen_bold.ttf")


# screen constants
SCREEN_SIZE = (800, 600)
SCREEN = display.set_mode(SCREEN_SIZE)


# colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# image constants
BKGSCREEN = image.load(os.path.join(DIRNAME, "img", "bkgscreen.tga"))
BKGSCREEN = transform.scale(BKGSCREEN, SCREEN_SIZE)
BKGSCREEN = BKGSCREEN.convert()
EDITOR_BKGSCREEN = BKGSCREEN.copy()

BLUPOT = image.load(os.path.join(DIRNAME, "img", "blu_pot.tga"))
BLUPOT = BLUPOT.convert()

REDPOT = image.load(os.path.join(DIRNAME, "img", "red_pot.tga"))
REDPOT = transform.scale(REDPOT, (16, 16))
REDPOT = REDPOT.convert()


#glyph constants
FONT = Font(os.path.join(DIRNAME, "font", "silkscreen.ttf"), 8)
DEFAULT = {
    'bkg'       : (11, 11, 11),
    'color'     : (201, 192, 187),
    'font'      : FONT,
    'spacing'   : 0, #FONT.get_linesize(),
    }


#functions
def center(surf, rect):
# centers rectangles on a specified axis on a surface
    surfrect = surf.get_rect()
    rect.x = ((surfrect.w / 2) - (rect.w / 2))
    rect.y = ((surfrect.h / 2) - (rect.h / 2))


#prepare rects and surfaces
CLIP = Rect(0, 0, 560, 420)
center(BKGSCREEN, CLIP)

EDITOR_CLIP = Rect(0, 0, 400, 300)
EDITOR_INFO_CLIP = Rect(0, 0, 400, 50)
center(BKGSCREEN, EDITOR_CLIP)
center(BKGSCREEN, EDITOR_INFO_CLIP)
EDITOR_INFO_CLIP.y -= 190

BKGSCREEN.set_clip(CLIP)
BKGSCREEN.fill((1, 1, 1))
EDITOR_BKGSCREEN.set_clip(EDITOR_INFO_CLIP)
EDITOR_BKGSCREEN.fill((1, 1, 1))
EDITOR_BKGSCREEN.set_clip(EDITOR_CLIP)
EDITOR_BKGSCREEN.fill((1, 1, 1))

CLIP.w -= 10
CLIP.h -= 10
center(BKGSCREEN, CLIP)
EDITOR_CLIP.w -= 10
EDITOR_CLIP.h -= 10
center(EDITOR_BKGSCREEN, EDITOR_CLIP)
EDITOR_INFO_CLIP.w -= 10
EDITOR_INFO_CLIP.h -= 10
center(EDITOR_BKGSCREEN, EDITOR_INFO_CLIP)
EDITOR_INFO_CLIP.y -= 190


# prepare cursors
#the default cursor
DEFAULT_CURSOR = mouse.get_cursor()


#the hand cursor
_HAND_CURSOR = (
"     XX         ",
"    X..X        ",
"    X..X        ",
"    X..X        ",
"    X..XXXXX    ",
"    X..X..X.XX  ",
" XX X..X..X.X.X ",
"X..XX.........X ",
"X...X.........X ",
" X.....X.X.X..X ",
"  X....X.X.X..X ",
"  X....X.X.X.X  ",
"   X...X.X.X.X  ",
"    X.......X   ",
"     X....X.X   ",
"     XXXXX XX   ")
_HCURS, _HMASK = pygame.cursors.compile(_HAND_CURSOR, ".", "X")
HAND_CURSOR = ((16, 16), (5, 1), _HCURS, _HMASK)


#prepare the pages of text
PAGES = {
    '0' : """welcome to the glyph demo
/n
click {link startdemo; {green; here}} to learn about glyph and the glyph mini-language
/n
click {link editor; {green; here}} to see and use the editor
/n
press ESCAPE anytime to exit this demo
""",


    'editor' : """the editor allows users to input text.  the black box below is the editor surface.  click on it to give the editor focus.  once the editor has focus, keyboard input goes to it, and will be blitted to the screen.  all keyboard input is saved as string literals.  press the escape key to exit.
""",


    'startdemo' : """glyph is a library for manipulating text and printing it to a pygame window.
/n
so what?  there are about a million pygame libraries to do that already.
/n
glyph is different for a few reasons:
1) glyph provides a within string literal mini-language for text manipulation.  you can use the mini-language to indicate what you want exactly where you want it, all right within the string literal.
/n
2) glyph provides typesetting like functionality: positioning text, wrapping text, justifying text, scrolling text, switching font, text color, background color, even inserting images into text
/n
3) glyph provides 'linked' text: text that returns a value whenever the mouse is hovering over it.  this can be used to route the user around your program, or provide tooltips.
/n
one simple object, the Glyph object, provides all this functionality.  how?  because the mini-language indicates how the Glyph object should treat text.
/n
so what is this wonderous mini-language?  click {link syntax; {green; here}} to learn more
""",


    'syntax' : """glyph syntax is modeled loosely after the LaTeX environment syntax.  appropriately, we will call text manipulation in glyph an 'environment'.  a left curly bracket, /{, indicates the beginning of an environment.  the first word following the left curly bracket declares the environment type.  after the environment type there should be a space, and then a comma seperated ilst of arguments, if there are any arguments.  a semi-colon denotes the end of the environment type declaration and argument list.  the rest of the text of this environment, until the environment ends or another is began, will be printed to the pygame window according to the instructions given by the environment type declaration and arguments.  an environment is terminated with the right curly bracket.
/n
here are some example environments and what they would produce:
/n
/space{10}glyph can /{font font//silkscreen_bold.ttf, 8; bold/} text for you.
/space{10}glyph can {font font/silkscreen_bold.ttf, 8; bold} text for you.
/n
/space{10}it can also /{color 255, 0, 0; color/} text for you.
/space{10}it can also {color 255, 0, 0; color} text for you.
/n
/space{10}it can even /{font font//silkscreen_bold.ttf, 8; nest these /{color 255, 0, 0; features/} for you/}.
/space{10}it can even {font font/silkscreen_bold.ttf, 8; nest these {color 255, 0, 0; features} for you}.
/n
this syntax is a little unwieldy, and is making it difficult to read the actual text.  to compensate for this, glyph provides macros.  click {link macros; {green; here}} to learn more about macros
""",


    'macros' : """macros are used to abbreviate the declarations and argument lists of environments.  setting macros can make the text and mini-language much easier to read and work with.  to initialize a macro, add a key-value pair to the glyph.Macro dictionary.  the key of the pair will be the abbreviation used to call the macro, and the value will be a tuple containing the environment declaration and arguments.
/n
here are some example macros:
/n
/space{10}glyph.Macro['b'] = ('font', Font(silkscreen_bold, 8))
/n
/space{10}glyph.Macro['red'] = ('color', (255, 0, 0))
/n
with the macro initialized, the abbreviation can be used in place of the full environment declaration and argument list:
/n
/space{10}glyph can /{b; bold/} text for you.
/space{10}glyph can {b; bold} text for you.
/n
/space{10}it can also /{red; color/} text for you.
/space{10}it can also {red; color} text for you.
/n
/space{10}it can even /{b; nest these /{red; features/} for you/}.
/space{10}it can even {b; nest these {red; features} for you}.
/n
macros are the recommended method of utilizing glyph's functionality.  they not only make it easier to type and read the glyph input syntax, but they also allow the client code to load resources, rather than leaving glyph attempting to find and load resources; a task that it is not designed to do and not very good at.
/n
by now you may be wondering what are the different environment declarations, and how to use them.  click {link environments; {green; here}} to learn more.
""",


    'environments' : """environments are the constructs used to manipulate how text is printed to the screen.  a Glyph object is instantiated with some default settings for font, size, color, and other parameters.  all text sent to this object will be printed to the screen according to these defaults.  if text needs to be manipulated in some way to be different from the defaults, an environment must be used.  all text inside the environment will be printed to the screen according to the instructions given by the environment declaration and argument list.
/n
these are the environment types offered in this version of glyph:
/n
/space{10}font file, size
/space{20}file is the path to the directory containing the font file
/space{20}size will be the size of the font
/n
/space{10}color R, G, B
/space{20}R, G, B are the red, green, blue values, respectively.
/n
/space{10}bkg R, G, B
/space{20}R, G, B are the red, green, blue values, respectively.
/n
/space{10}link linkname
/space{20}linkname is the name of the link, and will serve as the key for all the rects associated with the
/space{20}link
/n
NOTE: pathnames should use the slash ('//') character as separators.  glyph will convert separators to the system appropriate form.
/n
environments allow users to manipulate most of the aspects of pygame's font library, without otherwise having to write any python code.  glyph offers yet one more tool that extends the functionality of the pygame library: functions.  functions can insert images from a file or other sorts of surfaces right inside the text rendered by the font library.  to learn more about functions, click {link functions; {green; here}}.
""",


    'functions' : """functions are tools that allow special characters, images, and other surfaces to be inserted into text.  these are items that pygame's font library does not normally support, so glyph provides some special accomodations for them.  functions are denoted with the slash character: '//'.  glyph uses the slash '//' instead of the typical backslash '\\' to aovid conflicts with python or system commands.  following the slash is the function's name, then a pair of curly brackets enclosing a comma seperated argument list.  not all functions take arguments, in which event the curly brackets are empty.  there is an exception to this: inserting whitespace characters or glyph's special characters as text are also, in essence, a sort of function; for special and whitespace characters, the curly brackets should be ommitted.
/n
the following are the functions supported by the glyph minilanguage
/n
/space{10}special characters in the glyph minilanguage must be preceeded by a slash.  similarly, special
/space{10}characters like newlines are indicated with the slash in glyph
/space{20}////
/space{20}///{
/space{20}//n
/n
/space{10}//space/{spacesize/}
/space{20}spacesize is the size of the space in pixels.  this will insert blank space within the text.  the space
/space{20}will be colored to match the current environment
/n
/space{10}//img/{loc/}
/space{20}loc is the loation of the image file.  any image format supported by pygame's image library can be
/space{20}loaded.
/space{20}FUTURE: a rescale argument that will be used to rescale the image to the given dimensions.
/n
just as with environments, functions may be called from entries in the glyph.Macro dictionary.  insert the macro name, and then the item that the function would normally return.  for example:
/n
/space{10}red_pot = image.load("red_pot.tga")
/space{10}red_pot = red_pot.convert()
/space{10}glyph.Macro['red_pot'] = red_pot
/n
then call the macro using the macro name as the function name with no arguments:
/n
/space{10}to restore health, use a red potion //red_pot/{/}.
/n
the line should produce something like this:
/n
/space{10}to restore health, use a red potion /red_pot{}.
/n
one final feature glyph offers is fillable text.  To learn how to add fillable text to glyph objects, click {link fillable_text; {green; here}}.
""",

    'fillable_text' : """fillable text are editor objects inserted within the text of a glyph object.  fillable text can be used to permit users to enter data into a typeset glyph documents, and the data can be accessed from the glyph.editors attribute.  try entering some data into the fillable texts below:
/n
First Name: {editor first_name, 100; Omni}
/n
Last Name: {editor last_name, 100; Armstrong}
/n
hobbies: {editor hobbies, 200; programming, biking, gaming}
/n
fillable texts are technically environments (despite that they are not text attrtibutes but surfaces, which would generally be a function).  fillable texts are inserted with the following syntax:
/space{10}/{editor name, width; default_text/}
/space{10}'name' will the key where the editor may be accessed from glyph.editors.
/space{10}w is the the width of the fillable text.  height will be set from the surrounding line height.
/space{10}the font, color and background color of the editor are set from the default values of the glyph
/space{20}object.
/n
that's everything, and this is the end of the glyph demo.  thanks for trying it out.  glyph aims to be pygame's premier text processing library, if you have any questions, comments, concerns, or suggestions, please add them as a comment to glyph's pygame page.
"""}



class Main():
#   Example usage of Glyph

    def __init__(self):
        self.glyph = Glyph(CLIP, ncols=2, **DEFAULT)

        Macros['b'] = ('font', Font(P_BOLD, 8))
        Macros['big'] = ('font', Font(P_REG, 16))
        Macros['BIG'] = ('font', Font(P_BOLD, 16))
        Macros['red'] = ('color', RED)
        Macros['green'] = ('color', GREEN)
        Macros['bkg_blu'] = ('bkg', BLUE)
        Macros['red_pot'] = REDPOT

        self.editor = Editor(EDITOR_CLIP, **DEFAULT)
        self.editor_info = Glyph(EDITOR_INFO_CLIP, **DEFAULT)


    def start(self):
        chdir(DIRNAME)
        glyph = self.glyph
        start_editor = self.start_editor
        editor = None
        editors = glyph.editors
        glyph_rect = glyph.rect
        glyph.input(PAGES['0'], justify = 'justified')
        glyph.update()
        SCREEN.blit(BKGSCREEN, (0, 0))
        SCREEN.blit(glyph.image, glyph_rect)
        while 1:
            link = glyph.get_collisions(mouse.get_pos())
            if link: mouse.set_cursor(*HAND_CURSOR)
            else: mouse.set_cursor(*DEFAULT_CURSOR)
            for ev in event.get():
                if ev.type == MOUSEBUTTONDOWN:
                    if link:
                        if link == 'editor': start_editor()
                        elif link in editors:
                            if editor: editor.redraw() #clear the cursor
                            editor = editors[link]
                        else:
                            glyph.clear(SCREEN, BKGSCREEN)
                            glyph.input(PAGES[link], justify = 'justified')
                            glyph.update()
                            for _editor in glyph.editors.values():
                                draw.rect(glyph.image, GREEN,
                                          _editor.rect.inflate(2, 2), 1)

                if ev.type == KEYDOWN:
                    if ev.key == K_ESCAPE: exit()
                    elif editor: editor.input(ev)

            if editor: #if it has editors, glyph must be updated each loop
                cursor = editor.get_cursor()
                editor.image.fill((255, 205, 0), cursor)
                glyph.update()

            SCREEN.blit(glyph.image, glyph_rect)
            display.update()


    def start_editor(self):
        glyph = self.editor_info
        glyph_rect = glyph.rect
        glyph.input(PAGES['editor'])
        glyph.update()
        editor = self.editor
        editor_rect = editor.rect
        SCREEN.blit(EDITOR_BKGSCREEN, (0, 0))
        SCREEN.blit(glyph.image, glyph_rect)
        SCREEN.blit(editor.image, editor_rect)
        editor_focus = False
        while 1:
            mouse_pos = mouse.get_pos()
            link = glyph.get_collisions(mouse_pos)
            if link: mouse.set_cursor(*HAND_CURSOR)
            else: mouse.set_cursor(*DEFAULT_CURSOR)
            for ev in event.get():
                if ev.type == MOUSEBUTTONDOWN:
                    if link: pass

                    if editor.rect.collidepoint(mouse_pos): editor_focus = True

                    else: editor_focus = False

                if ev.type == KEYDOWN:
                    if ev.key == K_ESCAPE: exit()
                    if editor_focus == True: editor.input(ev)

            cursor = editor.get_cursor()
            editor.image.fill((255, 205, 0), cursor)

            SCREEN.blit(editor.image, editor_rect)
            display.update()




if __name__ == '__main__':
    main = Main()
    main.start()
