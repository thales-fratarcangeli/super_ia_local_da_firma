def check_brackets(text):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for i, c in enumerate(text):
        if c in "([{":
            stack.append((c, i))
        elif c in pairs:
            if not stack or stack[-1][0] != pairs[c]:
                return i
            stack.pop()
    return stack[0][1] if stack else -1
