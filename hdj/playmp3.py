import os
import random


class ShufflePlayer():
	def __init__(self):
		pass
		
	def _recFindAllSongs(self, strSongPath):
		print("INF: _recFindAllSongs in '%s'" % strSongPath )
		listFiles = os.listdir(strSongPath)
		cpt = 0
		for f in listFiles:
			afn = strSongPath + f
			if os.path.isdir(afn):
				self._recFindAllSongs(afn+os.sep)
				continue
			if not ".mp3" in f.lower():
				continue
			self.allSongs.append(afn)
			cpt += 1
			
		print("INF: _recFindAllSongs in '%s' found %d song(s)" % (strSongPath,cpt) )
			
		
	def findAllSongs(self, strSongPath):
		self.strSongPath = strSongPath
		self.allSongs = []
		print("INF: findAllSongs in '%s'" % strSongPath )
		self._recFindAllSongs(strSongPath)

		print("INF: findAllSongs: found %d song(s)" % len(self.allSongs))
			
			
	def playShuffle(self):
		shuffled = self.allSongs[:]
		random.shuffle(shuffled)
		for afn in shuffled:
			print("INF: playing '%s'" % afn)
			strCommand = 'omxplayer "%s"' % afn
			os.system(strCommand)
		
			
			
# class ShufflePlayer - end

shufflePlayer = ShufflePlayer()


if __name__ == "__main__":
	shufflePlayer.findAllSongs("/home/pi/hdj_musique_classique_et_film/")	
	while 1:
		shufflePlayer.playShuffle()