glyph is a library for manipulating text and printing it to a pygame window.

so what?  there are about a million pygame libraries to do that already.

glyph is different for a few reasons:

1) glyph provides a within string literal mini-language for text manipulation.  you can use the mini-language to indicate what you want exactly where you want it, all right within the string literal.

2) glyph provides typesetting like functionality: positioning text, wrapping text, justifying text, scrolling text, switching font, text color, background color, even inserting images into text

3) glyph provides 'linked' text: text that returns a value whenever the mouse is hovering over it.  this can be used to route the user around your program, or provide tooltips.

one simple object, the Glyph object, provides all this functionality.  how?  because Glyph interprets a mini-language, provided in string literals, that indicates how the Glyph object should treat text.