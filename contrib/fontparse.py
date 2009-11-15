#!/usr/bin/env python

# EDM magic font script
# Michael Davidsaver <mdavidsaver@bnl.gov>
# 20091113
#
# $ cat << EOF > fonts.list
# 3 0 0
# helvetica-medium-r-12.0
# helvetica-medium-r-18.0
# EOF
# $ xlsfonts -fn '-*-*-*-*-*-*-*-*-75-75-*-*-*-*' | ./fontparse.py >> fonts.list
#

import sys,re
from collections import defaultdict

inp=sys.stdin
outp=sys.stdout

xfontpat='-([^-]*)'
xfont=re.compile(xfontpat)

#print >>sys.stderr, 'Matching',xfontpat

fset = defaultdict(list)

# read and store by family

melem=0
for line in inp.readlines():

	#remove '\n'
	line=line[:-1]

	spec = xfont.findall(line)

	if len(spec)<14:
#		print >>sys.stderr, 'invalid spec?',line
		continue

	fset[spec[1]].append(spec)
	melem=max(melem, len(spec))

#	print >>sys.stderr, spec

print >>sys.stderr, 'Found',len(fset.keys()),'Families'
for family in fset.keys():

	print >>sys.stderr, '\nfamily',family,'has',len(fset[family]),'fonts'
	
	# These aren't practically usable
	if len(fset[family]) < 32:
		print >>sys.stderr, "Too small, skipping..."
		del fset[family]


# digest and group be field

for family in fset.keys():

	fspecs = map(lambda x:set(),range(melem))

	for fn in fset[family]:
#		print fn
		for i in range(len(fn)):
#			print i,fn[i],fspecs[i]
			fspecs[i].add(fn[i])

	fspecs=map(list,fspecs)

	# X11 font spec
	#   fields
	# 0 - foundry
	# 1 - family (ie times or helvetica)
	# 2 - weight (bold)
	# 3 - slant (r = normal,i , o)
	# 4 - setwidth (normal, condensed)
	# 5 - addedstyle (usually empty '')
	# 6 - pixelsize (usually all '*')
	# 7 - point size
	# 8 - resx  (75 or 100)
	# 9 - resy
	#10 - space (m = mono, p = propor, c = cell)
	#11 - average width
	#12 - registry
	#13 - encoding

	# -*-*-*-*-*-*-*-*-75-75-*-*-*-*

	fspecs[0]=['*']

	# ensure that the ordering is correct
	slant=[]
	for s in 'rio':
		if s in fspecs[3]:
			slant.append(s)
	fspecs[3]=slant

	#fspecs[5]=['']
	fspecs[6]=['*']
	fspecs[11]=['*']
	fspecs[12]=['*']
	fspecs[13]=['*']

	# EDM likes only 75 dpi fonts

	fspecs[8]=['75']
	fspecs[9]=['75']

	# sort numeric fields and remove 0's

	for i in [7]:
		d=fspecs[i]

		val=map(int,d)
		val.sort()
		val=filter(lambda x:x!=0,val)
		d=map(str,val)

		fspecs[i]=d

	#print fspecs


	# Create the spec line
	# -*-*-*-*-*-...
	ln=''
	for field in fspecs:

		ln=ln+'-'

		if len(field)==0:
			# empty fields '--'
			pass
		elif len(field)==1:
			# single fields '-val-'
			ln=ln+str(field[0])
		else:
			# group fields '-(a,b,c)-'
			s=reduce(lambda a,b:a+b, map(lambda x:x+',',field),'')
			s=s[:-1] # drop last ','
			ln=ln+'(%s)' % s

#	print ln

	outp.write('%s=%s\n'%(family,ln))
