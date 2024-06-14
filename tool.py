with open("output.txt", "r", encoding='utf-8') as f:
	a = f.read()

#print(a)


b= r"""data-testid="sds-"""
c = a.index(b)

print(a[c:c+100])

