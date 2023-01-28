from mido import Message, MidiFile, MidiTrack

from reformatting import midi2dict, dict2midi, dict2seq, seq2dict, edges2graph
from chord import Chord, get_distance

from solve import solve

for input_index in range(1, 8):
    input = MidiFile(f'original{input_index}.mid')
    d = midi2dict(input)
    seq = dict2seq(d, skip_pauses=True)

    dict2midi(seq2dict(seq), filename=f'harmony{input_index}.mid')

    hash2el = dict()
    el2hash = dict()
    amount = 1
    for i in range(len(seq)):
        if seq[i].get_hash() not in hash2el:
            hash2el[seq[i].get_hash()] = amount
            el2hash[amount] = seq[i]
            amount += 1

    edges = set()
    simple_edges = list()
    for i in range(len(seq)):
        tail = hash2el[seq[i].get_hash()]
        head = hash2el[seq[(i + 1) % len(seq)].get_hash()]
        if (head != tail):
            edge = (tail, head, get_distance(seq[i], seq[(i + 1) % len(seq)]))
            edges.add(edge)

            simple_edge = (tail, head)
            simple_edges.append(simple_edge)

    print(len(simple_edges))
    route = solve(edges)
    print(len(route))

    new_seq = [el2hash[el] for el in route]
    dict2midi(seq2dict(new_seq),
              filename=f'recreated-harmony{input_index}.mid')
    print('----------------------------------------------------------------')
