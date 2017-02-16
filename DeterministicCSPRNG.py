import hashlib, os, numbers

class DeterministicCSPRNG:
	"""A deterministic cryptographically-secure pseudorandom number generator.
	
	Given a seed, it can generate an unlimited amount of random data.
	The same seed will always give the same data, if the same random
	number ranges are requested each time. If the hash function is in
	fact secure and the attacker is unable to guess the seed, then
	there should be no way to predict new random output, even if
	a lot of random data has already been output.
	"""
	seed = ""
	
	_current = ""
	_used = 0
	
	def __init__(self, seed=None):
		"""Constructs a DeterministicCSPRNG.
		
		If seed is None, then os.urandom is used to securely seed it
		randomly. Read DeterministicCSPRNG.seed if you need to know the
		seed; note that it will probably contain control characters.
		
		If seed is a string, then it is used as the seed. Only if
		the given seed is particularly long, it is hashed first
		in order to ensure consistent RNG performance.
		"""
		if seed is None:
			self.seed = os.urandom(32)
		else:
			if not isinstance(seed, str):
				raise TypeError('seed must be a byte string')
			
			if len(seed) > 87: #Would use a third SHA-2 block
				h = hashlib.sha256()
				h.update(seed)
				seed = h.digest()
				
			self.seed = seed
	def _nextbit(self):
		if self._used+1 > len(self._current)*8:
			h = hashlib.sha256()
			h.update(self._current+self.seed)
			self._current = h.digest()
			self._used = 0
		ba = bytearray(self._current)
		bit = ba[self._used // 8] & (1 << 7-(self._used % 8))
		if bit > 0:
			bit = 1
		
		self._used += 1
		return bit
	def randrange(self, start, stop):
		"""Get a number uniformly at random from the set range(start, stop)."""
		
		if not (isinstance(start, numbers.Integral) and isinstance(stop, numbers.Integral)):
			raise TypeError('stop and start must be integral type')
	
		count = stop-start-1
		if count < 0:
			raise ValueError('stop must be greater than start')
		
		# get bits required
		bits = 0
		c = count
		while c > 0:
			bits += 1
			c = c >> 1
			
		out = 0
		# build the random number
		while True:
			for i in range(bits):
				out = out << 1
				if self._nextbit() == 1:
					out += 1
			if out <= count:
				break
			# too big, try again
			out = 0
		return start + out
