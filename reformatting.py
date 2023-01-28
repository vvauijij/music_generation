import matplotlib.pyplot as plt
import networkx as nx
from mido import Message, MidiFile, MidiTrack
from collections import defaultdict

from constants import TONE_OFFSET, TONE_SPECTOR, CHORD_LENGTH, PAUSE_LENGTH
from chord import Chord, get_distance


def midi2dict(midi: MidiFile) -> dict:
    d = defaultdict(Chord)
    for track in midi.tracks:
        cut_time = 0
        for msg in track:
            cut_time += msg.time
            if msg.type == 'note_on':
                d[cut_time].add_note(note=msg.note, is_on=True)
            elif msg.type == 'note_off':
                d[cut_time].add_note(note=msg.note, is_on=False)
    return d


def dict2midi(d: dict, filename: str):
    midi = MidiFile()
    track = MidiTrack()
    pr_time = 0
    for cur_time in sorted(d.keys()):
        for i in range(TONE_SPECTOR):
            if d[cur_time].notes[i] > 0:
                track.append(
                    Message('note_on', note=TONE_OFFSET + i, velocity=100, time=cur_time - pr_time))
                pr_time = cur_time
            elif d[cur_time].notes[i] < 0:
                track.append(
                    Message('note_off', note=TONE_OFFSET + i, velocity=64, time=cur_time - pr_time))
                pr_time = cur_time
    midi.tracks.append(track)
    midi.save(filename)


def dict2seq(d: dict, skip_pauses=False) -> list['Chord']:
    seq = []
    last_chord = Chord()
    for cur_time in sorted(d.keys()):
        if not skip_pauses:
            seq.append(d[cur_time] + last_chord)
        else:
            if d[cur_time] + last_chord != Chord():
                seq.append(d[cur_time] + last_chord)

        last_chord += d[cur_time]
    return seq


def seq2dict(seq: list['Chord']) -> dict:
    d = defaultdict(Chord)
    cur_time = 0
    for chord in seq:
        d[cur_time] = chord
        cur_time += CHORD_LENGTH
        d[cur_time] = -chord
        cur_time += PAUSE_LENGTH
    return d


def edges2graph(edges):
    G = nx.Graph()
    G.add_edges_from(edges)
    nx.draw_networkx(G)
    plt.show()
