import re

with open("backend/app/static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Extract script block content
match = re.search(r'<script type="text/babel">(.*?)</script>', html, re.DOTALL)
if not match:
    print("No babel script block found!")
    exit(1)

script = match.group(1)

# Simple bracket matching tool
stack = []
lines = script.split('\n')
for idx, line in enumerate(lines, 1):
    for char_idx, char in enumerate(line, 1):
        if char in ['{', '[', '(']:
            stack.append((char, idx, char_idx, line))
        elif char in ['}', ']', ')']:
            if not stack:
                print(f"Extra closing bracket '{char}' at line {idx}:{char_idx} -> {line.strip()}")
                continue
            last_open, o_line, o_char, o_text = stack.pop()
            if (char == '}' and last_open != '{') or \
               (char == ']' and last_open != '[') or \
               (char == ')' and last_open != '('):
                print(f"Mismatched bracket at line {idx}:{char_idx} (Found '{char}', expected match for '{last_open}' from line {o_line})")
                print(f"  Open line:  {o_text.strip()}")
                print(f"  Close line: {line.strip()}")

if stack:
    print(f"Unclosed brackets left: {len(stack)}")
    for item in stack[:5]:
        print(f"  Unclosed '{item[0]}' at line {item[1]}: {item[3].strip()}")
else:
    print("All basic brackets match!")
