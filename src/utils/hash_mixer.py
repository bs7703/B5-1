from src.utils.hash_utils import rotl_64, rotr_64, MASK64
from typing import Callable, List
mix_policy = Callable[[int], int]

def build_mixer(policy:List[mix_policy])->mix_policy:
    def mixer(h: int) -> int:
        for fn in policy:
            h = fn(h)
        return h
    return mixer

# ---------------------------------------------------------
# A: rotate + multiply
# 기본적인 bit-position 이동 + carry diffusion
# absorb(h ^ data)는 외부에서 이미 수행되었다고 가정
# ---------------------------------------------------------

def mix_a(h: int) -> int:
    C1 = 0x9E3779B185EBCA87  # odd

    h = rotl_64(h, 27)
    h = (h * C1) & MASK64
    h ^= h >> 31

    return h & MASK64


# ---------------------------------------------------------
# B: add + rotate + multiply
# XOR 중심의 A와 다르게 ADD의 carry propagation을 이용
# ---------------------------------------------------------

def mix_b(h: int) -> int:
    C1 = 0xC2B2AE3D27D4EB4F  # odd
    C2 = 0x165667B19E3779F9  # odd

    h = (h + C1) & MASK64
    h = rotr_64(h, 23)
    h = (h * C2) & MASK64
    h ^= h >> 29

    return h & MASK64


# ---------------------------------------------------------
# C: high <-> low diffusion
# 곱셈보다 bit 영역 사이의 dependency를 만드는 데 초점
# ---------------------------------------------------------

def mix_c(h: int) -> int:
    h ^= h >> 33
    h ^= (h << 17) & MASK64
    h ^= h >> 21
    h = rotl_64(h, 11)

    return h & MASK64


# ---------------------------------------------------------
# D: split-path mixing
# 하나의 state에서 별도 파생값 d를 만든 뒤 다시 결합
# dependency path를 하나 더 만드는 구조
# ---------------------------------------------------------

def mix_d(h: int) -> int:
    C1 = 0xD6E8FEB86659FD93  # odd
    C2 = 0xA5A35625AA5A3563  # odd

    d = (h * C1) & MASK64
    d = rotl_64(d, 37)
    d ^= d >> 23

    h ^= d
    h = (h + rotr_64(d, 17)) & MASK64
    h = (h * C2) & MASK64

    return h & MASK64


# ---------------------------------------------------------
# E: state cleanup / finalizer-like mix
# 새로운 정보를 넣기보다는 현재 state의 잔여 bias 제거
# ---------------------------------------------------------

def mix_e(h: int) -> int:
    C1 = 0x94D049BB133111EB  # odd
    C2 = 0xBF58476D1CE4E5B9  # odd
    h ^= h >> 30
    h = (h * C1) & MASK64
    h ^= h >> 27
    h = (h * C2) & MASK64
    h ^= h >> 31
    return h & MASK64