import functools

import nle.nethack as nh

from .monflag import *


def is_monster(glyph):
    return nh.glyph_is_monster(glyph)


def is_pet(glyph):
    return nh.glyph_is_pet(glyph)


@functools.lru_cache(nh.NUMMONS * 10)
def permonst(glyph):
    if nh.glyph_is_monster(glyph):
        return nh.permonst(nh.glyph_to_mon(glyph))
    elif nh.glyph_is_pet(glyph):
        return nh.permonst(nh.glyph_to_pet(glyph))
    elif nh.glyph_is_body(glyph):
        return nh.permonst(glyph - nh.GLYPH_BODY_OFF)
    else:
        assert 0, glyph


def find(glyph):
    if glyph in ALL_MONS or glyph in MON.ALL_PETS:
        return f'MON.fn({repr(permonst(glyph).mname)})'


@functools.lru_cache(nh.NUMMONS)
def from_name(name):
    mon_id = id_from_name(name)
    if mon_id is None:
        return None
    return nh.GLYPH_MON_OFF + mon_id


@functools.lru_cache(nh.NUMMONS)
def id_from_name(name):
    for i in range(nh.NUMMONS):
        if nh.permonst(i).mname == name:
            return i
    return None


def body_from_name(name):
    mon_id = id_from_name(name)
    if mon_id is None:
        return None
    return mon_id + nh.GLYPH_BODY_OFF


fn = from_name

ALL_MONS = [nh.GLYPH_MON_OFF + i for i in range(nh.NUMMONS)]
ALL_PETS = [nh.GLYPH_PET_OFF + i for i in range(nh.NUMMONS)]
