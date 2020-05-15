# import modules & set up logging
import gensim, logging
import numpy as np
#documentation https://radimrehurek.com/gensim/models/word2vec.html
#from gensim.test.utils import common_texts, get_tmpfile
#from gensim.models import Word2Vec

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


sentences = [['first', 'sentence'], ['second', 'sentence']]
# train word2vec on the two sentences
model = gensim.models.Word2Vec(sentences, min_count=1)

class MySentences(object):
    def __init__(self, dirname):
        self.dirname = dirname

    def __iter__(self):
        for fname in os.listdir(self.dirname):
            for line in open(os.path.join(self.dirname, fname)):
                yield line.split()

sentences = MySentences('./Word2VecSentences') # a memory-friendly iterator
model = gensim.models.Word2Vec(sentences)

model = gensim.models.Word2Vec(iter=1)  # an empty model, no training yet
model.build_vocab(some_sentences)  # can be a non-repeatable, 1-pass generator
model.train(other_sentences)  # can be a non-repeatable, 1-pass generator

model = Word2Vec(sentences, min_count=10, size=200)  # default value is 5 and 100

#install Cython to enable multicore
#model = Word2Vec(sentences, workers=4) # default = 1 worker = no parallelization

#model.accuracy('/tmp/questions-words.txt') #for evaluation of models

#storing of models
#model.save('/tmp/mymodel')
#new_model = gensim.models.Word2Vec.load('/tmp/mymodel')

#model = gensim.models.Word2Vec.load('/tmp/mymodel')
#model.train(more_sentences)

#for similiarity score
#model.most_similar
#model.doesnt_match
#model.similarity

#to get vectors of a words
#model['word']

#also vecotrs in numpy array
#model.syn0

#for prediction
#https://stackoverflow.com/questions/49643974/how-to-do-text-classification-using-word2vec/49647149
