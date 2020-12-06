from mylexer import Lexer
from myparser import Parser
from mypainter import Painter
import os

textBox = None
str = 'FOR T FROM 0 TO 2*PI STEP PI/50 DRAW (cos(T),sin(T));'
Lexer(str, show=True)
Parser(str, show=True)
Painter(str)