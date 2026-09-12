from src.utils.hash_utils import initialize, MASK64, rotr_64
from src.utils.hash_mixer import mix_a, mix_b, mix_c, mix_d, mix_e, build_mixer
from typing import Callable

RECOMMEND_MIX_A = [mix_a, mix_b]
RECOMMEND_MIX_B = [mix_c, mix_d, mix_e]
RECOMMEND_MIX_C = [mix_a,mix_b, mix_c, mix_d, mix_e]
HashFunction = Callable[[bytes], int]

def mix(hash:int, data:int)->int:
    h = (hash ^ data) & MASK64
    return build_mixer(RECOMMEND_MIX_B)(h)
def finalize(h:int)->int:
    h ^= rotr_64(h, 22)
    return h
def hashfunc(b:bytes)->int:
    full_length = len(b)
    h = initialize()
    for i in range(0, full_length, 8):
        chunk = int.from_bytes(b[i:i + 8], "little")
        h = mix(h, chunk)
    h = mix(h, full_length & MASK64)
    return finalize(h)