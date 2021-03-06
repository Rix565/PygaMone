from typing import NoReturn, Optional, List, Union
import pygame
import sounds

MUSIC_CHANNEL: Optional[pygame.mixer.Channel] = None
AMBIENT_CHANNEL: Optional[pygame.mixer.Channel] = None
TAUNT_CHANNEL: Optional[pygame.mixer.Channel] = None
TAUNT_CHANNEL2: Optional[pygame.mixer.Channel] = None
TAUNT_CHANNEL3: Optional[pygame.mixer.Channel] = None
TAUNT_CHANNEL4: Optional[pygame.mixer.Channel] = None

TAUNT: List[pygame.mixer.Channel] = []


def init() -> NoReturn:
    global MUSIC_CHANNEL, AMBIENT_CHANNEL, TAUNT_CHANNEL, TAUNT_CHANNEL2, TAUNT_CHANNEL3, TAUNT_CHANNEL4, TAUNT
    MUSIC_CHANNEL = pygame.mixer.Channel(0)
    MUSIC_CHANNEL.set_volume(0.5)
    AMBIENT_CHANNEL = pygame.mixer.Channel(1)
    TAUNT_CHANNEL = pygame.mixer.Channel(2)
    TAUNT_CHANNEL2 = pygame.mixer.Channel(3)
    TAUNT_CHANNEL3 = pygame.mixer.Channel(4)
    TAUNT_CHANNEL4 = pygame.mixer.Channel(4)
    TAUNT = [TAUNT_CHANNEL, TAUNT_CHANNEL2, TAUNT_CHANNEL3, TAUNT_CHANNEL4]


def first_empty_taunt() -> Optional[pygame.mixer.Channel]:
    for i in TAUNT:
        if i.get_sound() is None:
            return i
    return None


def start_in_first_empty_taunt(sound: Union[pygame.mixer.Sound, 'sounds.Sound']):
    i = first_empty_taunt()
    if i:
        i.play(sound if isinstance(sound, pygame.mixer.Sound) else sound.get())
    else:
        TAUNT_CHANNEL.play(sound if isinstance(sound, pygame.mixer.Sound) else sound.get())