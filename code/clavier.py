import array

import pygame
import keyboard

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


CODE_TO_NOTE = {

	16: ('c',1),	#A
	17: ('d',1),	#Z
	18: ('e',1),	#E
	19: ('f',1),	#R
	20: ('g',1),	#T
	21: ('a',1),	#Y
	22: ('b',1),	#U
	23:	('c',2),	#I
	24: ('d',2),	#O
	25: ('e',2),	#P

	3: ('c#',1),	#2
	4: ('d#',1),	#3
#	5: NOTHING (pas de mi dièse)
	6: ('f#',1),	#5
	7: ('g#',1),	#6
	8: ('a#',1),	#7
#	9: NOTHING (pas de si dièse)
	10: ('c#',2),	#9
	11: ('d#',2),	#0

	44:	('c',0),	#W
	45: ('d',0),	#X
	46:	('e',0),	#C
	47: ('f',0),	#V
	48: ('g',0),	#B
	49: ('a',0),	#N
	50: ('b',0),	#?
	51: ('c',1),	#;

	31: ('c#',0),	#S
	32: ('d#',0),	#D
#	33: NOTHING (pas de mi dièse)
	34: ('f#',0),	#G
	35: ('g#',0),	#H
	36: ('a#',0),	#J
#	37: NOTHING (pas de si dièse)
	38: ('c#',1),	#L

}

NOTES = genere_frequence_note()

SHIFT = (54, 42)
UP = 72
DOWN = 80


def record_to_frequence(record):
	base_gamme = 3
	total = []
	t_0 = record[0].time

	note_en_cours = {}
	key_pressed = {*()}
	shift_is_pressed = False

	for event in record:
		scan_code = event.scan_code

		if scan_code in SHIFT:
			shift_is_pressed = (event.event_type == 'down')

		elif scan_code == UP:
			base_gamme += 1
		elif scan_code == DOWN:
			base_gamme -= 1

		elif scan_code in CODE_TO_NOTE:

			if event.event_type == 'down':
				if scan_code not in key_pressed:
					key_pressed.add(scan_code)
					infos = CODE_TO_NOTE[scan_code]
					note_en_cours[scan_code] = (NOTES[infos[1] + base_gamme + shift_is_pressed][infos[0]], event.time - t_0)
			else:

				key_pressed.remove(scan_code)
				infos = note_en_cours[scan_code]
				temps = (infos[1],event.time - t_0)
				total.append((infos[0],temps))

	return total



def play_record(record,framerate=None):
	if framerate is None:
		framerate = pygame.mixer.get_init()[0]
	frequence = record_to_frequence(record)
	son = sound.array_from_nparray(sound.make_sound(frequence,framerate))
	pygame.mixer.Sound(son).play()

def play(framerate=None):
	t = keyboard.record()
	play_record(t,framerate)