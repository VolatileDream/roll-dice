
_function_table = {}

def get_dice_functions():
	return dict(_function_table)

def dice(initial_value=0):

	def decorate_function(func):

		_function_table[ func.__name__ ] = (func, initial_value)

		return func

	return decorate_function


@dice(0)
def sum(acc, value):
	return acc + value


@dice(None)
def min(acc, value):
	if acc and acc < value:
		return acc
	else:
		return value

@dice(None)
def max(acc, value):
	if acc and acc > value:
		return acc
	else:
		return value

