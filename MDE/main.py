from textx import metamodel_from_file
from jinja2 import Template, Environment
from interpreter import interpret
import random

def rounded(value, precision=2):
    return round(value, precision)

# Load the grammar and metamodel
mm = metamodel_from_file('arithmetics.tx')

# Generate random numbers and create input DSL code
a, b, c, d, e, f, g, h = [random.randint(1, 10) for _ in range(8)]
input_dsl = f'{a} PLUS {b}\n{c} MINUS {d}\n{e} MUL {f}\n{g} DIV {h}\nMEAN({a},{c},{e})'

# Parse the input DSL code
model = mm.model_from_str(input_dsl)

# Interpret the model and print results
print("\nInterpreting the model:\n")
interpret(model)

# Generate and print Python code
from template import template
print("\nGenerated Python code:")
env = Environment()
env.filters['rounded'] = rounded
t = env.from_string(template)
code = t.render(statements=model.statements)
print(code)
