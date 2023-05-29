from typing import Dict, List, TextIO
import mido as md
import markovify

from clusterization.utils import Midi2Chords, ClusterizeChords, Chords2Midi, GetClusterParams
from markov.markov_constants import (STATE_SIZE,
                                     SENTENCE_SIZE,
                                     MIN_WORDS)


class MarkovModel:
    def __init__(self,
                 data_path: str,
                 data_size: int):

        volumes, durations = GetClusterParams(data_path, data_size)
        self._volumes = volumes
        self._durations = durations
        self._model = self._create_model(data_path, data_size)

    def _create_model(self,
                      data_path: int,
                      data_size: int):

        with open('markov/text_model.txt', 'w') as text_model:
            for i in range(data_size):
                chords = Midi2Chords(md.MidiFile(f'{data_path}/{i}.midi'))
                clusterized_chords = ClusterizeChords(
                    chords, self._volumes, self._durations)
                self._write_chords(clusterized_chords, text_model)

        with open('markov/text_model.txt', 'r') as text_model:
            return markovify.Text(text_model, state_size=STATE_SIZE, retain_original=False)

    def _write_chords(self,
                      clusterized_chords: List[List[int]],
                      text_model: TextIO):

        for i, chord in enumerate(clusterized_chords):
            to_write = ':'.join(map(str, chord))
            if i and i % SENTENCE_SIZE == 0:
                to_write += '. '
            else:
                to_write += ' '
            text_model.write(to_write)

    def _parse_text_song(self,
                         text_song: str):

        clusterized_chords = [list(map(int, el.split(':')))
                              for el in text_song[:-1].split()]
        return clusterized_chords

    def GenerateSong(self,
                     output_path: str,
                     min_words=MIN_WORDS):

        text_song = ''
        while text_song.count('.') != 1:
            text_song = self._model.make_sentence(min_words=min_words)
        clusterized_chords = self._parse_text_song(text_song)
        Chords2Midi(clusterized_chords, output_path,
                    from_clusterized_chords=True)
