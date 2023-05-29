from typing import List, Set, Tuple
import numpy as np
import mido as md

from collections import defaultdict

from clusterization.utils import Midi2Chords, ClusterizeChords, Chords2Midi, GetClusterParams
from chinese_postman.graph import eularian, network


class ChinesePostmanModel:
    def __init__(self, data_path: str, data_size: int):
        volumes, durations = GetClusterParams(data_path, data_size)
        self._volumes = volumes
        self._durations = durations

    def _solve(self, edges: Set[Tuple[int]]):
        original_graph = network.Graph(edges)
        if not original_graph.is_eularian:
            graph = eularian.make_eularian(original_graph)
        else:
            graph = original_graph

        route = eularian.eularian_path(graph, start=1)
        return route

    def _recreate_chords(self, chords: List[List[int]]):
        chord2index = defaultdict(int)
        index2chord = defaultdict(list)
        for i in range(len(chords)):
            chord = tuple(chords[i][:-1])
            if chord not in chord2index:
                chord2index[chord] = len(chord2index) + 1
                index2chord[len(index2chord) + 1] = chords[i]

        edges = set()
        for i in range(len(chords)):
            from_chord = tuple(chords[i][:-1])
            to_chord = tuple(chords[(i + 1) % len(chords)][:-1])
            if from_chord != to_chord:
                diff_chord = tuple(to_chord[j] - from_chord[j]
                                   for j in range(len(to_chord)))
                distance = np.linalg.norm(np.array(diff_chord))
                edge = (chord2index[from_chord],
                        chord2index[to_chord],
                        distance)
                edges.add(edge)

        route = self._solve(edges)
        return [index2chord[index] for index in route]

    def GenerateSong(self, input_path: str, output_path: str):
        midi = md.MidiFile(input_path)
        chords = Midi2Chords(midi)
        clusterized_chords = ClusterizeChords(
            chords, self._volumes, self._durations)
        recreated_chords = self._recreate_chords(clusterized_chords)
        Chords2Midi(recreated_chords, output_path,
                    ticks_per_beat=midi.ticks_per_beat, from_clusterized_chords=True)
