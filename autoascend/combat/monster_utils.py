# heuristic monster types lists
ONLY_RANGED_SLOW_MONSTERS = ['floating eye', 'blue jelly', 'brown mold', 'gas spore', 'acid blob']
EXPLODING_MONSTERS = ['yellow light', 'gas spore', 'flaming sphere', 'freezing sphere', 'shocking sphere']
INSECTS = ['giant ant', 'killer bee', 'soldier ant', 'fire ant', 'giant beetle', 'queen bee']
WEAK_MONSTERS = ['lichen', 'newt', 'shrieker', 'grid bug']
WEIRD_MONSTERS = ['leprechaun', 'nymph']


def is_monster_faster(agent, monster):
    _, y, x, mon, _ = monster
    # TOOD: implement properly
    return 'bat' in mon.mname or 'dog' in mon.mname or 'cat' in mon.mname \
           or 'kitten' in mon.mname or 'pony' in mon.mname or 'horse' in mon.mname \
           or 'bee' in mon.mname or 'fox' in mon.mname


def imminent_death_on_melee(agent, monster):
    # hypothesis: fast attackers such as foxes and giant bats can get another
    # hit before an escape succeeds, so treat them like other high-risk melee
    # threats while HP is still recoverable.
    if is_dangerous_monster(monster) or is_monster_faster(agent, monster):
        return agent.blstats.hitpoints <= 16
    return agent.blstats.hitpoints <= 10


def is_dangerous_monster(monster):
    _, y, x, mon, _ = monster
    is_pet = 'dog' in mon.mname or 'cat' in mon.mname or 'kitten' in mon.mname or 'pony' in mon.mname \
             or 'horse' in mon.mname
    is_poisonous = mon.mname in ['garter snake', 'water moccasin', 'pit viper', 'snake', 'giant spider']
    is_hard_hitter = mon.mname in ['hobgoblin', 'hill orc', 'orc zombie', 'Woodland-elf', 'tengu']
    return is_pet or mon.mname in INSECTS or mon.mname == 'leocrotta' or is_poisonous or is_hard_hitter


def consider_melee_only_ranged_if_hp_full(agent, monster):
    return monster[3].mname in ('brown mold', 'blue jelly') and agent.blstats.hitpoints == agent.blstats.max_hitpoints
