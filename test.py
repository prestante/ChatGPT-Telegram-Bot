import re

answer = r"!Content /for/ *Alex|ander_Galkovsky** was _cleared_!"
pattern = r'([/<>()!{}|*_])'
escapedAnswer = re.sub(pattern, r'\\\1', answer)
print(escapedAnswer)