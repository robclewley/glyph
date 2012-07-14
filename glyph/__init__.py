"""
glyph is a library for manipulating text and printing it to a pygame window.

so what?  there are about a million pygame libraries to do that already.

glyph is different for a few reasons:
1) glyph provides a within string literal mini-language for text manipulation.  you can use the mini-language to indicate what you want exactly where you want it, all right within the string literal.

2) glyph provides typesetting like functionality: positioning text, wrapping text, justifying text, scrolling text, switching font, text color, background color, even inserting images into text

3) glyph provides 'linked' text: text that returns a value whenever the mouse is hovering over it.  this can be used to route the user around your program, or provide tooltips.

one simple object, the Glyph object, provides all this functionality. how? because Glyph interprets a mini-language, provided in string literals, that indicates how the Glyph object should treat text.


GLYPH MINI-LANGUAGE

syntax--
glyph syntax is modeled loosely after the LaTeX environment syntax.  appropriately, we will call text manipulation in glyph an 'environment'.  a left curly bracket, /{, indicates the beginning of an environment.  the first word following the left curly bracket declares the environment type.  after the environment type there should be a space, and then a comma seperated ilst of arguments, if there are any arguments.  a semi-colon denotes the end of the environment type declaration and argument list.  the rest of the text of this environment, until the environment ends or another is began, will be printed to the pygame window according to the instructions given by the environment type declaration and arguments.  an environment is terminated with the right curly bracket.

here are some example environments:

  glyph can {font font/silkscreen_bold.ttf, 8; bold} text for you.

  it can also {color 255, 0, 0; color} text for you.

  it can even {font font/silkscreen_bold.ttf, 8; nest these {color 255, 0, 0; features} for you}.


macros--
the glyph syntax is a little unwieldy, and is making it difficult to read the actual text.  to compensate for this, glyph provides macros.  macros are used to abbreviate the declarations and argument lists of environments.  setting macros can make the text and mini-language much easier to read and work with.  to initialize a macro, add a key-value pair to the glyph.Macro dictionary.  the key of the pair will be the abbreviation used to call the macro, and the value will be a tuple containing the environment declaration and arguments.

here are som example macros:

  glyph.Macro['b'] = ('font', Font(silkscreen_bold, 8))

  glyph.Macro['red'] = ('color', (255, 0, 0))

with the macro initialized, the abbreviation can be used in place of the full environment declaration and argument list:

  glyph can {b; bold} text for you.

  it can also {red; color} text for you.

  it can even {b; nest these {red; features} for you}.

macros are the recommended method of utilizing glyph's functionality.  they not only make it easier to type and read the glyph input syntax, but they also allow the client code to load resources, rather than leaving glyph attempting to find and load resources; a task that it is not designed to do and not very good at.


environments--
environments are the constructs used to manipulate how text is printed to the screen.  a Glyph object is instantiated with some default settings for font, size, color, and other parameters.  all text sent to this object will be printed to the screen according to these defaults.  if text needs to be manipulated in some way to be different from the defaults, an environment must be used.  all text inside the environment will be printed to the screen according to the instructions given by the environment declaration and argument list.

these are the environment types offered in this version of glyph:

  font file, size
    file is the path to the directory containing the font file
    size will be the size of the font

  color R, G, B
    R, G, B are the red, green, blue values, respectively.

  bkg R, G, B
    R, G, B are the red, green, blue values, respectively.

  link linkname
    linkname is the name of the link, and will serve as the key for all the rects associated with the link

NOTE: pathnames should use the slash ('//') character as separators.  glyph will convert separators to the system appropriate form.

environments allow users to manipulate most of the aspects of pygame's font library, without otherwise having to write any python code.


functions--
functions can insert images from a file or other sorts of surfaces right inside the text rendered by the font library.  functions are tools that allow special characters, images, and other surfaces to be inserted into text.  these are items that pygame's font library does not normally support, so glyph provides some special accomodations for them.  functions are denoted with the slash character: '//'.  glyph uses the slash '//' instead of the typical backslash '\\' to aovid conflicts with python or system commands.  following the slash is the function's name, then a pair of curly brackets enclosing a comma seperated argument list.  not all functions take arguments, in which event the curly brackets are empty.  there is an exception to this: inserting whitespace characters or glyph's special characters as text are also, in essence, a sort of function; for special and whitespace characters, the curly brackets should be ommitted.

the following are the functions supported by the glyph minilanguage

  special characters in the glyph minilanguage must be preceeded by a slash.  similarly, special characters like newlines are indicated with the slash in glyph
    //
    /{
    /n

  /space{spacesize}
    spacesize is the size of the space in pixels.  this will insert blank space within the text.  the space will be colored to match the current environment

  /img{loc}
    loc is the loation of the image file.  any image format supported by pygame's image library can be loaded.
    FUTURE: a rescale argument that will be used to rescale the image to the given dimensions.

just as with environments, functions may be called from entries in the glyph.Macro dictionary.  insert the macro name, and then the item that the function would normally return.  for example:

  red_pot = image.load("red_pot.tga")
  red_pot = red_pot.convert()
  glyph.Macro['red_pot'] = red_pot

then call the macro using the macro name as the function name with no arguments:

  to restore health, use a red potion /red_pot{}.


EXAMPLE

see the example folder, provided with the source distribution, for an example script.  Running the example will cover the same topics introduced above, but will show the results of the examples.
"""




from .glyph import Glyph, GlyphGroup, Macros
from .editor import Editor, EditorGroup
