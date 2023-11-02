def interpret(model):
    for statement in model.statements:
        if hasattr(statement, 'left'):
            if statement.__class__.__name__ == 'Add':
                print(f"{statement.left} PLUS {statement.right} -> {statement.left + statement.right}")
            elif statement.__class__.__name__ == 'Sub':
                print(f"{statement.left} MINUS {statement.right} -> {statement.left - statement.right}")
            elif statement.__class__.__name__ == 'Mul':
                print(f"{statement.left} MUL {statement.right} -> {statement.left * statement.right}")
            elif statement.__class__.__name__ == 'Div':
                result = round(statement.left / statement.right, 2)
                print(f"{statement.left} DIV {statement.right} -> {result}")
        else:
            mean_value = round(sum(statement.values) / len(statement.values), 2)
            values_str = ', '.join(map(str, statement.values))
            print(f"MEAN({values_str}) -> ({' + '.join(map(str, statement.values))})/{len(statement.values)} -> {mean_value}")
