template = """
{%- for statement in statements %}
    {%- if statement.__class__.__name__ == 'Add' %}
print("{{ statement.left }} PLUS {{ statement.right }} -> {{ statement.left + statement.right }}")
    {%- elif statement.__class__.__name__ == 'Sub' %}
print("{{ statement.left }} MINUS {{ statement.right }} -> {{ statement.left - statement.right }}")
    {%- elif statement.__class__.__name__ == 'Mul' %}
print("{{ statement.left }} MUL {{ statement.right }} -> {{ statement.left * statement.right }}")
    {%- elif statement.__class__.__name__ == 'Div' %}
print("{{ statement.left }} DIV {{ statement.right }} -> {{ (statement.left / statement.right)|round(2) }}")
    {%- elif statement.__class__.__name__ == 'Mean' %}
print("MEAN({{ statement.values|join(', ') }}) -> ({{ statement.values|join(' + ') }})/{{ statement.values|length }} -> {{ (statement.values|sum / statement.values|length)|round(2) }}")
    {%- endif %}
{%- endfor %}
"""
