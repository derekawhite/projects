# python -m pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org anytree

from anytree import Node, RenderTree

udo = Node("Udo")
marc = Node("Marc", parent=udo)
lian = Node("Lian", parent=marc)
dan = Node("Dan", parent=udo)
jet = Node("Jet", parent=dan)
jan = Node("Jan", parent=dan)
joe = Node("Joe", parent=dan)

print(udo)
Node('/Udo')
print(joe)
Node('/Udo/Dan/Joe')

for pre, fill, node in RenderTree(udo):
    print("%s%s" % (pre, node.name))

print()

for pre, fill, node in RenderTree(udo):
    print(f"{node.name}")


for node in udo:
    print(f"{node.name}")



print()

print(dan.children)
print(udo.children)


x = [1,2,3,4,5,6]
y = " + ".join(str(q) for q in x)
print (y)
