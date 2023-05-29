from markov.model import MarkovModel
from chinese_postman.model import ChinesePostmanModel

from constants import (MARKOV_DATA_SIZE,
                       MARKOV_DATA_PATH,
                       MARKOV_TO_GENERATE,
                       MARKOV_TO_GENERATE_PATH,
                       CHINESE_POSTMAN_DATA_SIZE,
                       CHINESE_POSTMAN_DATA_PATH,
                       CHINESE_POSTMAN_TO_GENERATE,
                       CHINESE_POSTMAN_TO_GENERATE_PATH)


markov_model = MarkovModel(MARKOV_DATA_PATH,
                           MARKOV_DATA_SIZE)

for i in range(MARKOV_TO_GENERATE):
    markov_model.GenerateSong(f'{MARKOV_TO_GENERATE_PATH}/markov_sample_{i}.midi')


chinese_postman_model = ChinesePostmanModel(CHINESE_POSTMAN_DATA_PATH,
                                            CHINESE_POSTMAN_DATA_SIZE)

for i in range(CHINESE_POSTMAN_TO_GENERATE):
    chinese_postman_model.GenerateSong(f'{CHINESE_POSTMAN_DATA_PATH}/{i}.midi',
                                       f'{CHINESE_POSTMAN_TO_GENERATE_PATH}/chinese_postman_sample_{i}.midi')
