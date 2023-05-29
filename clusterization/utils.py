from typing import Dict, List
from collections import defaultdict

import numpy as np
import mido as md

from clusterization.clusterization_constants import (TONE_SPECTOR,
                                                     TONE_OFFSET,
                                                     OCTAVE_USED,
                                                     CLUSTER_SPECTOR,
                                                     DURATION_SCALE,
                                                     TICKS_PER_BEAT)


def Midi2Chords(midi: md.MidiFile):
    extended_chords_matrix = []

    notes = {}
    for track in midi.tracks:
        current_time = 0
        for message in track:
            current_time += message.time
            if message.type == 'note_on' or message.type == 'note_off':
                if not current_time in notes:
                    notes[current_time] = [None for _ in range(TONE_SPECTOR)]
                notes[current_time][message.note] = message.velocity if message.type == 'note_on' else 0

    if len(notes):
        chords = sorted(notes.items())
        current_chord = [note if note else 0 for note in chords[0][1]]
        current_time_delta = chords[0][0]
        current_chord.append(current_time_delta)

        for i in range(1, len(chords)):
            extended_chords_matrix.append(current_chord.copy())
            for j in range(TONE_SPECTOR):
                if chords[i][1][j] is not None:
                    current_chord[j] = chords[i][1][j]

            current_chord[TONE_SPECTOR] = chords[i][0] - chords[i - 1][0]

    return extended_chords_matrix


def GetNotePosition(note: int):
    note -= TONE_OFFSET
    if note < 0:
        return note % (CLUSTER_SPECTOR // OCTAVE_USED)
    elif note >= CLUSTER_SPECTOR:
        return CLUSTER_SPECTOR - (CLUSTER_SPECTOR // OCTAVE_USED) + note % (CLUSTER_SPECTOR // OCTAVE_USED)

    return note


def ClusterizeChords(chords: List[List[int]],
                     volumes: Dict[int, int],
                     durations: Dict[int, int]):

    clusterized_chords = [
        [0 for _ in range(CLUSTER_SPECTOR + 1)] for _ in range(len(chords))]

    for i in range(len(chords)):
        for j in range(TONE_SPECTOR):
            if chords[i][j]:
                new_note = GetNotePosition(j)
                if clusterized_chords[i][new_note]:
                    continue
                else:
                    clusterized_chords[i][new_note] = volumes[new_note]
        clusterized_chords[i][CLUSTER_SPECTOR] = durations[chords[i][TONE_SPECTOR]]

    return clusterized_chords


def Chords2Midi(chords: List[List[int]],
                output_path: str,
                ticks_per_beat=TICKS_PER_BEAT,
                from_clusterized_chords=False):

    midi = md.MidiFile()
    track = md.MidiTrack()

    spector = CLUSTER_SPECTOR if from_clusterized_chords else TONE_SPECTOR
    spector_offset = TONE_OFFSET if from_clusterized_chords else 0
    for i in range(len(chords)):
        current_time_delta = chords[i][spector]
        for j in range(spector):
            if i == 0 or chords[i - 1][j] != chords[i][j]:
                track.append(md.Message('note_on', note=spector_offset + j,
                             velocity=chords[i][j], time=current_time_delta))
                current_time_delta = 0
            elif chords[i][j] == 0:
                track.append(md.Message(
                    'note_on', note=spector_offset + j, velocity=0, time=current_time_delta))
                current_time_delta = 0

    midi.tracks.append(track)
    midi.ticks_per_beat = ticks_per_beat
    midi.save(output_path)


def ClusterizeMidi(input_path: str,
                   ouput_path: str,
                   volumes: Dict[int, int],
                   durations: Dict[int, int],
                   ticks_per_beat=TICKS_PER_BEAT):

    midi = md.MidiFile(input_path)
    extended_chords_matrix = Midi2Chords(midi)
    clusterized_chords = ClusterizeChords(
        extended_chords_matrix, volumes, durations)
    Chords2Midi(clusterized_chords, ouput_path, ticks_per_beat, True)


def GetClusterDurations(durations: Dict[int, int]):
    sorted_durations = sorted(
        durations.items(), key=lambda item: item[1], reverse=True)
    cluster_durations = defaultdict(int)
    for duration, duration_repeats in sorted_durations:
        offset_limit = int(DURATION_SCALE / duration_repeats)
        for offset in range(-offset_limit, offset_limit):
            if duration + offset in cluster_durations:
                cluster_durations[duration] = duration + offset
                break
        if duration not in cluster_durations:
            cluster_durations[duration] = duration
    return cluster_durations


def GetClusterVolumes(volumes: Dict[int, List]):
    return {note: int(np.mean(volumes[note])) for note in volumes}


def GetClusterParams(data_path: str, data_size: int):
    volumes = defaultdict(list)
    durations = defaultdict(int)
    for i in range(data_size):
        extended_chords_matrix = Midi2Chords(
            md.MidiFile(f'{data_path}/{i}.midi'))
        for chord in extended_chords_matrix:
            for j in range(TONE_SPECTOR):
                if chord[j]:
                    volumes[GetNotePosition(j)].append(chord[j])
            durations[chord[TONE_SPECTOR]] += 1

    cluster_durations = GetClusterDurations(durations)
    cluster_volumes = GetClusterVolumes(volumes)
    return cluster_volumes, cluster_durations
