import datetime

def now():
	t = datetime.datetime.now()
	return [t.month,t.day,t.hour,t.minute]

def dprint(t):
	if(t[2]<12):
		s = "am"
	else:
		if(t[2] > 12):
			t[2]-=12
		s = "pm"
	if(t[1] == now()[1]):
		ss = "today"
	else:
		ss = "yesterday"
	return ("{} @ {:02}:{:02}{}".format(ss,t[2],t[3],s))

def past24(t1,t2):
	if(t2[0]==t1[0] and t2[1]!=t1[1]):
		if(t2[2] > t1[2] or (t2[2]==t1[2] and t2[3]>t1[3])):
			return True
	elif(t2[0]>t1[0]):
		return True

	return False 
