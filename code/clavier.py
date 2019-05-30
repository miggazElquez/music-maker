import array

import make_sound as sound


LA = 440


def genere_frequence_note():
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
