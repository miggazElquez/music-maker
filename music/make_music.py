import re
import array
import itertools
import wave

import pygame

from . import make_sound as sound


LA = 440

def genere_frequence_note():
	frequence_base = frequence = LA
	name = ['a','a#','b','c','c#','d','d#','e','f','f#','g','g#']
	coef = 2**(1/12)
	note = {}
	for i in name:
		note[i.upper()] = frequence
		frequence*=coef
	frequence = frequence_base
	for i in name[::-1]:
		frequence/=coef
		note[i] = frequence

	note_bon_sens = {nom:note[nom] for nom in itertools.chain(name,map(str.upper,name))}
	return note_bon_sens

NOTES = genere_frequence_note()
DIESES = ['f','c','g','d','a','e','b']
BEMOLS = DIESES[::-1]


def separe_block(source):
	"""Separe le texte source en différents blocs (un bloc = un bloc de paramètre (':XXX:') ou un bloc temps ('.AAA.'))"""
	liste = []
	cursor = 0
	while True:
		if cursor>=len(source)-1:
			break
		if source[cursor] == ':':
			cursor_2 = cursor + 1
			while source[cursor_2]!=':':
				cursor_2+=1
			param = source[cursor:cursor_2+1]
			liste.append(param)
			cursor = cursor_2+1
		elif source[cursor] == '.':
			if source[cursor+1]==":":
				cursor+=1
			else:
				cursor_2=cursor+1
				while source[cursor_2]!='.':
					cursor_2+=1
				temps = source[cursor:cursor_2+1]
				liste.append(temps)
				cursor=cursor_2
	return liste


def join(blocks):
	"""A partir d'une liste de bolck, recrée un fichier source"""
	final = ""
	for block in blocks:
		if final and final[-1] == "." and block[0] == ".":
			final+=block[1:]
		else:
			final+=block
	return final




def remove_inside_square_bracket(string):
	"""Permet de traduire '.A[BCD]E.' en '.A--BCDE--.', compréhensible par le parser principal"""
	blocks = separe_block(string)
	nouv = []
	for block in blocks:
		if block[0]=="." and "[" in block:
			if not "]" in block:
				raise ValueError(f"There is a '[' but no ']' in the block {block}")
			else:
				inside_block = block[block.index('[')+1:block.index(']')]
				nbr_de_notes = len(inside_block) - inside_block.count('#')
				nouv_block = '.'
				cursor = 1
				while cursor+1 < len(block):
					if block[cursor] not in '[]':
						if cursor+1 < len(block) and block[cursor+1] == "#":
							nouv_block += block[cursor:cursor+2]
							cursor+=2
						else:
							nouv_block += block[cursor]
							cursor+=1
						nouv_block += '-'* (nbr_de_notes-1)
					else:
						while block[cursor] != ']':
							cursor+=1
						cursor+=1
						nouv_block+=inside_block
				nouv_block+='.'
				nouv.append(nouv_block)
		else:
			nouv.append(block)
	return join(nouv)


def make_armure(string):
	"""
	On renseigne l'armure de cette façon : 
	:[a+b-]: pour mettre le la # et le si b
	on peut aussi mettre [5#] ou [4b] pour avoir une armure avec les 5 premier dièses, ou les 4 premiers bémols
	"""
	blocks = separe_block(string)
	chgt = {}
	nouv = []
	for block in blocks:
		if block[0] == ":":
			if '[' in block:
				inside_block = block[block.index('[')+1:block.index(']')]
				if inside_block[0] in map(str,range(1,10)):
					assert len(inside_block) == 2
					alter = DIESES if inside_block[1] == '#' else BEMOLS
					sign = '+' if inside_block[1] == '#' else '-'
					chgt = {note:sign for note in alter[:int(inside_block[0])]}
				else:
					chgt =  dict(zip(inside_block[::2],inside_block[1::2]))	#"a+b-" -> {'a':'+', 'b':'-'}
				deb = block.index('[')
				fin = block.index(']')
				nouv.append(block[:deb] + block[fin+1:])
			else:
				nouv.append(block)

		elif block[0] == '.':
			nouv_block = ''
			for indice,note in enumerate(block):
				if note.lower() in chgt:
					if block[indice+1] not in '#!':
						name = list(NOTES)
						if chgt[note.lower()] == '+':
							nouv_block +=  name[name.index(note)+1]
						else:
							nouv_block += name[name.index(note)-1]
					else:
						nouv_block += note
				elif note != '!':	#On l'a pris en compte, mais on le réécrit pas
					nouv_block += note
			nouv.append(nouv_block)

	return join(nouv)








MACROS = [	#l'ordre est important !!! Par exemple, si il y a des '!', 'remove_inside_square_brackets' ne fonctionnera pas
	remove_inside_square_bracket,
	make_armure,
]

def do_macros(string):
	"""Transforme le fichier source en un texte capable d'être lu par le parser principal"""
	for f in MACROS:
		string = f(string)
	return string



class MusicParser:
	"""Classe chargée de convertir le fichier source en son utilisable"""
	def __init__(self,string,framerate=None):
		self.contenu = do_macros(string)
		self.tempo = 60
		self.notes = []
		self.last_note = ('',0)	#pk j'ai fait ça ?
		self.timbre = (1,)
		self._parse()
		self.notes_par_frequence = list(self._par_frequence())
		if not framerate:
			infos = pygame.mixer.get_init()
			if infos is None:
				raise ValueError("You didn't give the value of framerate, and pygame isn't initialized, so we can't guess the value")
			else:
				framerate = infos[0]
		self.framerate = framerate


	def _parse(self):
		for i in separe_block(self.contenu):
			if i.startswith('.'):
				self._parse_temps(i)
			elif i.startswith(':'):
				self._parse_param(i)
			else:
				raise ValueError(f"Block {i} non reconnu")
		self.notes.append(self.last_note)



	def _parse_param(self,param):
		tempo = re.search(r"t=[\d\.]+",param)
		if tempo:
			self.tempo = float(tempo.group()[2:])

	def _parse_temps(self,temps):
		nbr_de_notes = len(temps)-2-temps.count("#") #-2 : les points de début et de fin
		duree_d_une_note = (60/self.tempo)/nbr_de_notes
		cursor = 1
		while True:
			if cursor==len(temps)-1:
				break
			if temps[cursor]=="-":
				self.last_note = self.last_note[0], self.last_note[1] + duree_d_une_note
				cursor+=1
			else:
				self.notes.append(self.last_note)
				if temps[cursor+1]=="#":
					self.last_note = temps[cursor:cursor+2],duree_d_une_note
					cursor+=2
				else:
					self.last_note = temps[cursor], duree_d_une_note
					cursor+=1


	def _par_frequence(self):
		return ((NOTES[i],j)if i!=" " else (0,j) for i,j in self.notes[1:])

	def valeur_son(self):
		valeurs = (
			sound.make_complex_sound(i,tps,self.framerate,self.timbre) if i else sound.make_silence(tps,self.framerate)
			for i,tps in self.notes_par_frequence
		)
		son = sound.array_from_nparrays(valeurs)
		return son

	def play(self):
		pygame.mixer.Sound(self.valeur_son()).play()

	def write_to_file(self,path):
		with wave.open(path,'w') as file:
			file.setnchannels(2)
			file.setframerate(self.framerate)
			file.setsampwidth(2)	#oui, ça se changera pas.

			file.writeframes(self.valeur_son())



def play(musique,timbre=(1,)):
	"""Fonction pour jouer le son de manière pratique"""
	a = MusicParser(musique)
	a.timbre = timbre
	a.play()



def write_music(path,musique,timbre=(1,),framerate=44100):
	a = MusicParser(musique,framerate)
	a.timbre = timbre
	a.write_to_file(path)


def init():
	"""A ne pas utiliser si on utilise pygame avec, c'est juste si on veut faire que des sons"""
	pygame.init()
	pygame.display.set_mode((1,1))

def load_musique():
	with open('../musique.txt') as f:
		return f.readlines()

if __name__ == "__main__":
	for musique in load_musique():
		play(musique)
		input("press 'Enter' to listen the next music")
