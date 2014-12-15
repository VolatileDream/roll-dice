import plyplus

# using C99 math grammar
dice_grammar = plyplus.Grammar("""

@start : expr ;

mul_op : '\*' | '/' ;
add_op : '\+' | '-' ;

mul_expr : (mul_expr mul_op)? atom ;
add_expr : (add_expr add_op)? mul_expr ;
expr : add_expr ;

atom : number | dice | '\(' expr '\)' | function ;

number : '[\d]+' ;
dice : number ? 'd' number ;

function : function_name '\(' expr '\)' ;
function_name : '[a-zA-Z][a-zA-Z_]+' ;

WS: '[ \t\n]+' (%ignore) (%newline) ;

""")


def augment_to_list(t):
	if type(t) is not type([]):
		t = [t]
	return t

def lapply(func, maybe_list_1, maybe_list_2=None):
	maybe_list_1 = augment_to_list(maybe_list_1)
	if maybe_list_2:
		maybe_list_2 = augment_to_list(maybe_list_2)
		#print("lapply:", maybe_list_1, maybe_list_2)
		return list( map(func, [ (x,y) for x in maybe_list_1 for y in maybe_list_2] ) )
	else:
		return list( map(func, [ x for x in maybe_list_1 ] ) )

import random
import functools

class ExprParser(plyplus.STransformer):

	__default__ = lambda self, exp : exp.tail[0]

	def _bin_op(self, exp):
		#print("bin op:", exp.tail)
		if len(exp.tail) == 1:
			return exp.tail[0]

		arg1, op, arg2 = exp.tail

		if op == "+":
			return lapply( lambda x : x[0] + x[1], arg1, arg2 )
		elif op == "-":
			return lapply( lambda x : x[0] - x[1], arg1, arg2 )
		elif op == "*":
			return lapply( lambda x : x[0] * x[1], arg1, arg2 )
		elif op == "/":
			return lapply( lambda x : x[0] // x[1], arg1, arg2 )

		raise Error("no matching operation")

	add_expr = _bin_op
	mul_expr = _bin_op

	number = lambda self, exp : int(exp.tail[0])

	def dice(self, exp):
		if len(exp.tail) == 2:
			dice_count, die_roll = exp.tail
		else:
			dice_count, die_roll = 1, exp.tail[0]
		return [ self.rand.randint(1, die_roll) for i in range(0,dice_count) ]

	def function(self, exp):
		name, value = exp.tail

		if type(value) != type([]):
			value = [value]

		if name in self.functions:
			func, init = self.functions[name]
			value = functools.reduce( func, value, init )

			if type(value) != type([]):
				value = [ value ]

			return value

		raise SyntaxError("No function by name: " + name)

	def __init__(self, funcs):
		self.rand = random.Random()
		self.functions = funcs


def get_line(prompt):
	try:
		return input(prompt)
	except EOFError:
		return None

import functions

def do_roll():
	l = dice_grammar
	t = ExprParser( functions.get_dice_functions() )

	output = None

	while True:
		line = (yield output)

		output = None

		if line is None:
			return

		if not line:
			continue

		try:
			output = t.transform( l.parse( line ) )
		except plyplus.plyplus.ParseError as e:
			output = e
		except SyntaxError as e :
			output = e



if __name__ == "__main__":

	rolls = do_roll()
	rolls.send(None)

	while True:
		output = None

		try:
			output = rolls.send(get_line("> "))
		except StopIteration:
			break

		if type(output) == type([]):
			print(output[0], end='')
			for num in output[1:]:
				print(" " + str(num), end='')
			print()
		elif output:
			print(output)


