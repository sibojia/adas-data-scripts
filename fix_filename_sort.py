import sys
def fcmp(a,b):
	if len(a) != len(b):
		return len(a)-len(b)
	else:
		if a>b:
			return 1
		elif a==b:
			return 0
		else:
			return -1
fin=open(sys.argv[1]).readlines()
fout=open(sys.argv[1],'w')
fin.sort(fcmp)
fout.write(''.join(fin))
fout.close()
