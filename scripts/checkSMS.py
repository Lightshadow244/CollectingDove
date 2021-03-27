import gammu
import signal

print("1")
sm = gammu.StateMachine()
sm.ReadConfig()
sm.Init()
print("2")

start = True
remain = sm.GetSMSStatus()['SIMUsed']
try:
	#while remain > 0:
		#if start:
		#	sms = sm.GetNextSMS(Start=True, Folder=0)
		#	start = False
		#else:
		#	sms = sm.GetNextSMS(Location=sms[0]['Location'], Folder=0)
		#remain = remain - len(sms)
		sms = sm.GetSMS(Location=2,Folder=0)[0]
		print(sms['Text'])
		print(sms['Text'][sms['Text'].find(":")+2:])
		#for m in sms:
		#	if('Ihre TAN lautet:' not in m['Text']):
		#		print(m['Text'])
		#	else:
		#		print(m['Text'])
		#		print(m['Text'][m['Text'].find(":")+2:])
except gammu.ERR_EMPTY:
	# This error is raised when we've reached last entry
	# It can happen when reported status does not match real counts
	print('Failed to read all messages!')
