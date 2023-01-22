# Example from bandit
# https://github.com/PyCQA/bandit/blob/main/examples/eval.py
import os  # noqa

print(eval("1+1"))
print(eval("os.getcwd()"))
print(eval("os.chmod('%s', 0o777)" % 'test.txt'))

exec("do evil")
