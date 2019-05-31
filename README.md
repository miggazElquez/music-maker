make_music
=========


This package is useful for create douns and music.

It contain three module : `make_sound`, `make_music` and `clavier`.


make_sound
----------

This module provide all functions needed for create a sound. All the functions return the sound in the form of a np.array of float.
If you want to use the sound, you must to convert it, using `make_sound.array_from_nparray`,
or if you have an iterable, `make_sound.array_from_nparrays`

To listen the sound, you can use `pygame.mixer.Sound(array).play()`, if you use pygame.

You can also use `make_sound.to_wav()`, for writing the sound to a file


make_music
----------

This module allow you to write your music in a little language.

### Settings

In this language, you can set the tempo writing `:t=60:`.
You can also set the key signature in two ways : 

If you want to set 5 sharp, just write between the colons `[5#]`, or `[3b]` if you want three flat.
You can also choose which note you want to modifiy, `[a+b-]` will set the A sharp, and the B flat.

### Note

You separe each time by a dot.
Then, you write your notes between.
you write the name of the note ('A','B',...).
If you write it in uppercase, you will have the upper octave, and if you write it in lowercase, you will have the lower octave.
You can put an accidental sharp simply by writing `#` just before the note, but you can't put an accidental flat.
If you have set the key signature, you can write  `!` as a natural.  
/!\\ You must write your accidental in each note of the time !

If you write two notes, they will take the same time.
You can put `-` to continue the last note. If you have a part of the time with a lot of notes, you can use [] for separe it:
instead of `.A-B-CD.`, you can write `.AB[CD].`

### Utilisation

You just have to create a instance of `make_music.MusicParser` with the string in argument. You can then do `my_music.play()` (using pygame)
or `my_music.write_music(path)`. If you doesn't specify the framerate, it will use the default framerate of pygame.

You can find example of music in `data/musique.txt`

clavier
----

This module allow you to play in your keyboard like on a piano.

There is two octaves on the keyboard. If you press shift, you are increase all the note by an octave.
If you want to move the octaves permanently, you can use the arrows.

I'm didn't test if this module work on a qwerty keyboard (I use an azerty)