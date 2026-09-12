SEED = 0x1234567812345678
MIX = 0x1244768657955422
MASK64 = (1 << 64) - 1

def initialize()->int:
    return SEED
def rotr_64(t:int, v:int)->int:
    v %= 64
    t &= MASK64
    return ((t >> v) | (t << (64 - v))) & MASK64
def rotl_64(t:int, v:int)->int:
    v %= 64
    t &= MASK64
    return ((t << v) | (t >> (64 - v))) & MASK64
