
import re

file_path = r'd:\Palak\Idea-to-deploy\apps\api\engine\ui_renderer.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# This is a very crude check for f-string single braces
# We'll look for f""" or f''' and then scan the content until the end of the string

matches = re.finditer(r'f("""|\'\'\')', content)
for match in matches:
    quote = match.group(1)
    start = match.end()
    end = content.find(quote, start)
    if end == -1:
        print(f"Unclosed f-string starting at {match.start()}")
        continue
    
    f_content = content[start:end]
    
    # Inside f_content:
    # {{ and }} are literal braces
    # { starts an expression, } ends it
    
    i = 0
    in_expr = False
    expr_stack = []
    
    while i < len(f_content):
        if f_content[i:i+2] == '{{':
            i += 2
            continue
        if f_content[i:i+2] == '}}':
            i += 2
            continue
        if f_content[i] == '{':
            in_expr = True
            expr_stack.append(i)
        elif f_content[i] == '}':
            if not expr_stack:
                # This is a single } that is not part of an expression!
                # But wait, it could be the end of the LAST expression.
                print(f"Found single '}}' at character {start + i} (approx line {content.count('\\n', 0, start + i) + 1})")
            else:
                expr_stack.pop()
                if not expr_stack:
                    in_expr = False
        i += 1
    
    if expr_stack:
        for pos in expr_stack:
            print(f"Found unclosed '{{' at character {start + pos} (approx line {content.count('\\n', 0, start + pos) + 1})")
