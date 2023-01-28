from math import sqrt

from constants import TONE_SPECTOR


class Chord:
    def __init__(self):
        self.notes = [0] * TONE_SPECTOR

    def __add__(self, other) -> 'Chord':
        res = Chord()
        for i in range(TONE_SPECTOR):
            res.notes[i] = self.notes[i] + other.notes[i]
        return res

    def __iadd__(self, other) -> 'Chord':
        for i in range(TONE_SPECTOR):
            self.notes[i] += other.notes[i]
        return self

    def __neg__(self) -> 'Chord':
        res = Chord()
        for i in range(TONE_SPECTOR):
            res.notes[i] = -self.notes[i]
        return res

    def __eq__(self, other):
        for i in range(TONE_SPECTOR):
            if self.notes[i] != other.notes[i]:
                return False
        return True

    def __str__(self) -> str:
        return str(self.notes)

    def __repr__(self) -> str:
        return str(self.notes)

    def add_note(self, note: int, is_on: bool) -> None:
        if is_on:
            self.notes[note % TONE_SPECTOR] += 1
        else:
            self.notes[note % TONE_SPECTOR] -= 1

    def get_hash(self) -> int:
        pow = 1
        res = 0
        for i in range(TONE_SPECTOR):
            res += self.notes[i] * pow
            pow *= TONE_SPECTOR
        return res


def get_distance(a: Chord, b: Chord) -> float:
    res = 0
    for i in range(TONE_SPECTOR):
        res += (a.notes[i] - b.notes[i]) ** 2
    return sqrt(res)
