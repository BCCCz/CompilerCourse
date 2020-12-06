from mylexer import Lexer
from mylexer import TokenType
from mylexer import Token
from expnode import ExpNode
import math
import sys


#语法分析器
tokenIter = None
tokenNow = None
showProcess = False


def setDefaultValue(show):
	global showProcess
	showProcess = show


# 从词法分析器的tokens获得token
def FetchToken():
	global tokenNow
	try:
		tokenNow = next(tokenIter)
		return tokenNow
	except StopIteration:
		sys.exit()

def MatchToken(tokenType, show=False):
	if show:
		tokenNow.show()
	if tokenNow.tokenType==tokenType:
		FetchToken()
		return True
	else:
		print("Excepted ", tokenType, "received ", tokenNow.tokenType)
		print("error!")
		return False
		exit(-1)

##########################################
# 表达式
# ########################################

# 二叉树节点
# + - * / ** T CONST_ID FUNC
# '('  ')' 匹配过程中扔掉
# 叶子节点： T CONST_ID
# 非叶子节点： 非终结符

# 加法运算 
# 左结合
# 新的 + - 为根节点
# Example： 1+2-3
#     -
#    / \
#   +   3
#  / \
# 1   2

def Expression(level):
	left = Term(level+1)
	root = None
	while tokenNow.tokenType==TokenType.PLUS or tokenNow.tokenType==TokenType.MINUS:
		root = ExpNode(tokenNow)
		MatchToken(tokenNow.tokenType)
		right = Term(level+1)
		root.addson(left)
		root.addson(right)
		left = root
		# left.dfs()
	print(left.dfs())
	return left

# 乘法运算 
# 左结合
# 新的 * / 为根节点
# Example： 1*2*3
#     *
#    / \
#   *   3
#  / \
# 1   2
def Term(level):
	left = Factor(level)
	root = None
	while tokenNow.tokenType==TokenType.MUL or tokenNow.tokenType==TokenType.DIV:
		root = ExpNode(tokenNow)
		MatchToken(tokenNow.tokenType)
		right = Factor(level+1)
		root.addson(left)
		root.addson(right)
		left = root

	return left

def Factor(level):
	if tokenNow.tokenType==TokenType.PLUS or tokenNow.tokenType==TokenType.MINUS:
		root = ExpNode(tokenNow)
		MatchToken(tokenNow.tokenType);
		son = Factor(level+1)	
		root.addson(son)
		return root
	else:
		return Component(level+1)		

# 乘方运算 右结合
def Component(level):
	left = Atom(level)
	if tokenNow.tokenType==TokenType.POWER:
		root = ExpNode(tokenNow)
		MatchToken(tokenNow.tokenType)
		right = Component(level+1)

		root.addson(left)
		root.addson(right)
		return root
	else:
		return left

# 函数节点 FUNC <- CONST_ID | T
# 叶子节点 CONST_ID | T
def Atom(level):
	#Msg(level, "Atom", 0)
	if tokenNow.tokenType==TokenType.CONST_ID or tokenNow.tokenType==TokenType.T:
		root = ExpNode(tokenNow)
		MatchToken(tokenNow.tokenType)
		#Msg(level, "Atom")
		return root

	elif tokenNow.tokenType==TokenType.FUNC:
		root = ExpNode(tokenNow)
		MatchToken(tokenNow.tokenType)
		MatchToken(TokenType.L_BRACKET)
		son = Expression(level+1)
		MatchToken(TokenType.R_BRACKET)
		root.addson(son)
		#Msg(level, "Atom")
		return root

	elif tokenNow.tokenType==TokenType.L_BRACKET:
		MatchToken(TokenType.L_BRACKET)
		root = Expression(level+1)
		MatchToken(TokenType.R_BRACKET)
		#Msg(level, "Atom")
		return root
	else:
		print("Atom Error!")



def OriginStatement(level):
	#Msg(level, "OriginStatement", 0)
	MatchToken(TokenType.ORIGIN)
	MatchToken(TokenType.IS)
	MatchToken(TokenType.L_BRACKET)
	Origin_x = Expression(level+1)
	MatchToken(TokenType.COMMA)
	Origin_y = Expression(level+1)
	MatchToken(TokenType.R_BRACKET)

	return ["OriginStatement", Origin_x, Origin_y]

def	ScaleStatement(level):
	MatchToken(TokenType.SCALE)
	MatchToken(TokenType.IS)
	MatchToken(TokenType.L_BRACKET)
	Scale_x = Expression(level+1)
	MatchToken(TokenType.COMMA)
	Scale_y = Expression(level+1)
	MatchToken(TokenType.R_BRACKET)

	return ["ScaleStatement", Scale_x, Scale_y]

def	RotStatement(level):
	MatchToken(TokenType.ROT)
	MatchToken(TokenType.IS)
	Rot_angle = Expression(level+1)

	return ["RotStatement", Rot_angle]

def getColor():
	if tokenNow.tokenType==TokenType.COLOR:
		if tokenNow.lexeme=='RED':
			color = 'r'
		elif tokenNow.lexeme=='GREEN':
			color = 'g'
		elif tokenNow.lexeme=='BLUE':
			color = 'b'
		elif tokenNow.lexeme=='YELLOW':
			color = 'y'
		elif tokenNow.lexeme=='BLACK':
			color = 'k'
		MatchToken(TokenType.COLOR)
		return color
		# else: 
		# 	print("GetColor Error")	
	else:
		print("GetColor Error")

def	ForStatement(level):
	#Msg(level, "ForStatement", 0)
	MatchToken(TokenType.FOR)
	MatchToken(TokenType.T)
	MatchToken(TokenType.FROM)
	T_start = Expression(level+1)
	MatchToken(TokenType.TO)
	T_end = Expression(level+1)
	MatchToken(TokenType.STEP)
	T_step = Expression(level+1)

	
	MatchToken(TokenType.DRAW)
	MatchToken(TokenType.L_BRACKET)
	Point_x = Expression(level+1)
	# print(Point_x.dfs())
	MatchToken(TokenType.COMMA)
	Point_y = Expression(level+1)
	MatchToken(TokenType.R_BRACKET)

	# 自定义颜色
	Draw_color = None
	if tokenNow.tokenType==TokenType.OF:
		MatchToken(TokenType.OF)
		Draw_color = getColor() 

	return ["ForStatement", T_start, T_end, T_step, Point_x, Point_y, Draw_color]

# Statement -> OriginStatement | ScaleStatement | RotStatement | ForStatement
def Statement(level):
	statement = None
	if tokenNow.tokenType==TokenType.ORIGIN:
		statement = OriginStatement(level+1)
	elif tokenNow.tokenType==TokenType.SCALE:
		statement = ScaleStatement(level+1)
	elif tokenNow.tokenType==TokenType.ROT:
		statement = RotStatement(level+1)
	elif tokenNow.tokenType==TokenType.FOR:
		statement = ForStatement(level+1)
	else:
		print("Statement Error!")
		exit(-1)

	return statement


def Program(level=0):
	statements = []
	while tokenNow.tokenType!=TokenType.NONTOKEN:
		tmpstatement = Statement(level+1)
		matched = MatchToken(TokenType.SEMICO)
		if matched:
			statements.append(tmpstatement)
		else:
			print("Program Error")
			exit(-1)
	return statements

def Parser(string, show=False):
	global tokenIter			# 必须要 global

	# 调用词法分析器 得到记号表
	tokenList = Lexer(string)
	tokenIter = iter(tokenList)

	setDefaultValue(show)
	FetchToken()
	return Program()
