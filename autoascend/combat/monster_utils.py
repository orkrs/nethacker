import os

# heuristic monster types lists
from .. import jf_config

ONLY_RANGED_SLOW_MONSTERS = ['floating eye', 'blue jelly', 'brown mold', 'gas spore', 'acid blob']
if jf_config.HAZARD_FIXES:
    ONLY_RANGED_SLOW_MONSTERS += ['spotted jelly', 'ochre jelly', 'gelatinous cube']
if jf_config.LATE_FIXES:
    ONLY_RANGED_SLOW_MONSTERS += ['yellow mold', 'green mold', 'red mold']
EXPLODING_MONSTERS = ['yellow light', 'gas spore', 'flaming sphere', 'freezing sphere', 'shocking sphere']
INSECTS = ['giant ant', 'killer bee', 'soldier ant', 'fire ant', 'giant beetle', 'queen bee']
WEAK_MONSTERS = ['lichen', 'newt', 'shrieker', 'grid bug']
WEIRD_MONSTERS = ['leprechaun', 'nymph']

# H6a: the Dlvl 1 killers that the classifier missed (see REFLECTION.md section 5v).
# ACCEPTED - on by default. 30-seed A/B: mean29 0.099083 -> 0.111075, d1 deaths
# 11 -> 9, count_down 12 -> 9, median 0.07454 -> 0.11705. Set VK_DANGER=0 to
# restore the old classifier (that is the inert control used by that A/B).
_VK_DANGER = os.environ.get('VK_DANGER', '1') == '1'

# H6d: scale the melee-retreat HP threshold by current max HP. Off by default so
# 9315154 (H6a as accepted) stays reproducible; VK_HP_FRAC=1 enables it.
_VK_HP_FRAC = os.environ.get('VK_HP_FRAC', '0') == '1'

_FAST_BASE = ['bat', 'dog', 'cat', 'kitten', 'pony', 'horse', 'bee', 'fox',
              'snake', 'moccasin', 'viper', 'spider', 'ant']
_FAST_EXTRA = ['jackal', 'wolf', 'hyena', 'dingo', 'coyote', 'iguana',
               'kobold', 'lizard', 'creeper']

_POISON_EXACT = ['garter snake', 'water moccasin', 'pit viper', 'snake', 'giant spider']
_HARD_EXACT = ['hobgoblin', 'hill orc', 'orc zombie', 'Woodland-elf', 'tengu']

# matched as substrings; the 'corpse' guard keeps inert bodies out of the
# dangerous set so the bot still walks over corpses to collect them.
_BEAST_EXTRA = ['kobold', 'jackal', 'coyote', 'hyena', 'wolf', 'dingo',
                'iguana', 'lizard', 'creeper', 'imp']


def _mname(monster):
    return monster[3].mname


def is_monster_faster(agent, monster):
    mname = _mname(monster)
    if not _VK_DANGER:
        names = _FAST_BASE
    elif 'corpse' in mname:
        # inert bodies must not raise the retreat threshold, otherwise the bot
        # stops walking over corpses to collect the XP they are worth
        names = _FAST_BASE
    else:
        names = _FAST_BASE + _FAST_EXTRA
    return any(n in mname for n in names)


def imminent_death_on_melee(agent, monster):
    # hypothesis: fast attackers such as foxes and giant bats can get another
    # hit before an escape succeeds, so treat them like other high-risk melee
    # threats while HP is still recoverable.
    #
    # H6d: the absolute thresholds below assume a fresh 18 HP valkyrie. Traces
    # show the killers sit at 20-67 HP (seed 8 died at 20/67), so an absolute
    # "HP <= 16" either never fires or fires while the fight is still winnable
    # (seed 25: 17/17 at first contact, retreat at turn 802, death at 6600).
    # VK_HP_FRAC=1 scales the thresholds by current max HP instead.
    hp = agent.blstats.hitpoints
    if _VK_HP_FRAC:
        ceiling = max(1, agent.blstats.max_hitpoints)
        risky = 16 * ceiling / 18.0
        safe = 10 * ceiling / 18.0
    else:
        risky = 16
        safe = 10
    if is_dangerous_monster(monster) or is_monster_faster(agent, monster):
        return hp <= risky
    return hp <= safe


def is_dangerous_monster(monster):
    mname = _mname(monster)
    is_pet = 'dog' in mname or 'cat' in mname or 'kitten' in mname or 'pony' in mname \
             or 'horse' in mname
    if _VK_DANGER:
        # substring matching: "large kobold", "kobold lord" and "rotted hill orc
        # corpse" must not slip through an exact-equality list. The corpse veto
        # keeps ordinary bodies out of the dangerous set (they are XP, not a
        # threat) while "rotted" ones stay flagged - their contact poison killed
        # seed 22 on Dlvl 1.
        corpse = 'corpse' in mname
        is_poisonous = any(n in mname for n in _POISON_EXACT) or 'rotted' in mname
        is_hard_hitter = (any(n in mname for n in _HARD_EXACT) or 'kobold' in mname) and not corpse
        is_beast = (not corpse) and any(n in mname for n in _BEAST_EXTRA)
    else:
        is_poisonous = mname in _POISON_EXACT
        is_hard_hitter = mname in _HARD_EXACT
        is_beast = False
    return is_pet or mname in INSECTS or mname == 'leocrotta' or is_poisonous or is_hard_hitter or is_beast


def consider_melee_only_ranged_if_hp_full(agent, monster):
    return monster[3].mname in ('brown mold', 'blue jelly') and agent.blstats.hitpoints == agent.blstats.max_hitpoints
