import array
import math
import itertools
import pygame
import numpy as np
import pylab


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

NOTE = genere_frequence_note()


def genere_frequence_note_bis():
	coef = 2**(1/12)
	name = ['c','c#','d','d#','e','f','f#','g','g#','a','a#','b']
	frequence = LA
	base_gamme = {}
	for i,j in enumerate(name[name.index('a'):]):
		base_gamme[j] = frequence * (coef)**i
	for i,j in enumerate(reversed(name[:name.index('a')]),1):
		base_gamme[j] = frequence / (coef)**i
	ord_base_gamme = {note:base_gamme[note] for note in name}
	
	notes = {
		num: {i: j*2**(num-3) for i,j in ord_base_gamme.items()}	#la gamme décalé d'une ou plusieurs octaves
		for num in range(7)
	}
	
	return notes



def array_from_nparray(np_array):
	"""
	Transforme un array numpy de float en array de type 'h'
	Permet de passer du son tel qu'on le calcule au son tel qu'on doit l'encoder"""
	return array.array('h',map(int,np_array))


def array_from_nparrays(iterables):
	"""Comme 'array_from_nparray',mais permet de passer un iterables de np_array"""
	return array.array('h',map(int,itertools.chain.from_iterable(iterables)))


def resize_amplitude(son,amplitude=1):
	"""
	multiplie toutes les amplitudes par un même coefficient,
	de tel sorte à ce qu'on ai l'amplitude max de la valeur souhaitée
	"""
	max_amplitude = (2**15-1)
	max_dans_le_son = max(map(abs,(f(son)for f in (min,max))))
	coef = (max_amplitude / max_dans_le_son)*amplitude
	nouv_son = son*coef
	return nouv_son



def make_square_sound(frequence,duree):
	"""
	Génère une onde quadratique de la forme :
	___     ___
	   |   |   |
	   ----    ----
	Return un array de type 'h'


	Attention : cette fonction n'est absolument pas compatible avec le reste du module.
	"""
	frequence_mixer = pygame.mixer.get_init()[0]
	amplitude = (2**15-1)//10
	periode = frequence_mixer // frequence
	print(periode)
	son = array.array('h')
	nbr_de_valeur = int(frequence_mixer * duree)
	while len(son)/2<nbr_de_valeur:
		for i in range(periode): #Faut //2, puis 2 * son.append, du coup voila
			son.append(amplitude)
		for i in range(periode):    
			son.append(-amplitude)
	return son

def make_silence(duree,framerate=None):
	if framerate is None:
		framerate = pygame.mixer.get_init()[0]
	return np.zeros(int(framerate*duree*2))


def make_sinus_sound(frequence,duree,relatif=1,framerate=None):
	"""
	Génère une onde sinusoidale, on peut choisir son amplitude relative au maximum.
	"""
	if framerate is None:
		framerate = pygame.mixer.get_init()[0]
	#size = pygame.mixer.get_init()[1]
	amplitude = 2**15-1
	periode = framerate / frequence
	#print(periode)
	coef = (math.pi*2) / periode
	n = nbr_de_valeur = int(framerate * duree)
	son = np.array([np.arange(n),np.arange(n)]).reshape((n*2,),order='F')	#0,0,1,1,...,44,44,45,45,...
	son = son*coef
	son = np.sin(son)
	son *= amplitude * relatif

	return son


def combine_sound(sons):
	"""
	Créé un nouveau son à partir de touts les sons passés en paramètres,
	en les recombinant en un son de duréé égale au son le plus long
	"""
	sons = iter(sons)
	final_son = next(sons)
	i = 1
	for son in sons:
		final_son += sons
		i += 1
	final_son /= i
	return final_son





def make_complex_sound(frequence,duree,amplitude_relative,framerate=None):
	"""on passe la liste des amplitudes relative"""
	sounds = (make_sinus_sound(frequence*i, duree, j, framerate)for i,j in enumerate(amplitude_relative, start=1) if j)
	return combine_sound(sounds)


def show_courbe(son):
	x = list(range(len(son)))
	pylab.plot(x,son)
	pylab.show()




def main():
	pygame.init()
	pygame.display.set_mode(((1,1)))
	print("Entrez 0 et 0 pour crash le programme et l'interrompre (oui c'et sale XD)")
	while 1:
		frequence = int(input("fréquence : "))
		duree = float(input("durée (en s) : "))
		son = make_square_sound(frequence,duree)
		pygame.mixer.Sound(son).play()

	pygame.quit()

if __name__ == "__main__":
	main()

