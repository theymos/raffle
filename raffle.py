import re, fractions, sys
from DeterministicCSPRNG import *

print "You should have already:"
print " - Publicly announced the block number from which you will get your hash, and at the time of this announcement, this block number should have been in the future."
print " - Publicly announced the \"raffle ID\" that will be used (ASCII characters only)"
print " - Waited at least 6 blocks after the announced block number"
print "If this is the case, then you can continue."
print ""

blockNum = raw_input("Block number: ").strip()
if not re.match("^[0-9]+$", blockNum):
	print "Invalid block number"
	sys.exit(1)
blockNum = int(blockNum)

blockHash = raw_input("Hash of block #"+str(blockNum)+": ").strip()
if not re.match("^[0-9a-fA-F]{64}$", blockHash):
	print "That is not a Bitcoin block hash"
	sys.exit(1)

print "Choose a raffle ID like \"mysite.com raffle #104\". The point of this is to ensure that if multiple people run raffles on the same block number, they do not get the same numbers. Use ASCII characters only"
raffleID = raw_input("Raffle ID: ").strip()
if not all(ord(c) < 127 for c in raffleID):
	print "Invalid raffle ID, use ASCII characters only"
	sys.exit(1)

print "You will now add the raffle participants"
print "If you make an error, there will be an opportunity to make edits at the end"
participants = []

def addPart(part):
	while True:
		name = raw_input("Name of participant #"+str(len(part)+1)+" (leave blank to stop): ").strip()
		if name == "":
			break
		tickets = raw_input("Number of raffle tickets (decimal amounts are OK): ").strip()
		if not re.match("^([0-9]+|[0-9]+\.[0-9]*|\.[0-9]+)$", tickets):
			print "Invalid raffle count"
			continue
		try:
			tickets = fractions.Fraction(tickets)
		except:
			print "Invalid raffle count"
			continue
		part.append([name, tickets, 0])

addPart(participants)

def printPart(part):
	print 'ID', 'Tickets', 'Name'
	for i in range(len(part)):
		print i+1, str(float(part[i][1])), part[i][0]
		
def delPart(part):
	id = raw_input("ID of participant to delete (leave blank to cancel): ").strip()
	if id == "":
		return
	if not re.match("^[0-9]+$", id) or int(id) < 1 or int(id) >= len(part)+1:
		print "Invalid ID"
		return
	del part[int(id)-1]
def repositionPart(part):
	id = raw_input("ID of participant to move (leave blank to cancel): ").strip()
	if id == "":
		return
	if not re.match("^[0-9]+$", id) or int(id) < 1 or int(id) >= len(part)+1:
		print "Invalid ID"
		return
	newID = raw_input("New ID of that participant: ").strip()
	if not re.match("^[0-9]+$", newID) or int(newID) < 1 or int(newID) >= len(part)+1:
		print "Invalid ID"
		return
	old = part[int(id)-1]
	del part[int(id)-1]
	part.insert(int(newID)-1, old)

while True:
	print "Menu:"
	print " l - list participants"
	print " a - add participants"
	print " d - delete participant"
	print " r - reposition participant"
	print " c - continue"
	cmd = raw_input("Command: ").strip()
	if not re.match("^[ladrc]$", cmd):
		print 'Invalid command'
		continue
	if cmd == "l":
		printPart(participants)
	elif cmd == "a":
		addPart(participants)
	elif cmd == "d":
		delPart(participants)
	elif cmd == "r":
		repositionPart(participants)
	elif cmd == "c":
		break

def lcm(a, b):
	if a == 0 and b == 0:
		return 0
	return abs(a*b)/fractions.gcd(a,b)

if len(participants) == 0:
	print "No participants"
	sys.exit(1)


total = fractions.Fraction()
for p in participants:
	total += p[1]
den = 1
for p in participants:
	p[2] = p[1]/total
	den = lcm(den, p[2].denominator)

prev = 0
print "Ticket numbers (inclusive):"
for p in participants:
	tickets = p[2].numerator * (den / p[2].denominator)
	p[2] = prev + tickets
	print str(prev+1)+" - "+str(p[2])+':', p[0]
	prev = p[2]

print "RESULTS"
print "Block number: " + str(blockNum)
print "Block hash: " + blockHash
print "Raffle ID: " + raffleID
drng = DeterministicCSPRNG(blockHash+raffleID)
rand = drng.randrange(1, den+1)
print ''
print "WINNING TICKET: " + str(rand)
winner = ''
prev = 0
for p in participants:
	if rand >= prev+1 and rand <= p[2]:
		winner = p[0]
		break
	prev = p[2]
print "WINNER: ", winner
