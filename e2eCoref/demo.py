from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from six.moves import input
import tensorflow as tf
from . import coref_model as cm
from . import util

import nltk
nltk.download("punkt")
from nltk.tokenize import sent_tokenize, word_tokenize

import json
from helpers import export2xml

def create_example(text):
  raw_sentences = sent_tokenize(text)
  sentences = [word_tokenize(s) for s in raw_sentences]
  speakers = [["" for _ in sentence] for sentence in sentences]
  return {
    "doc_key": "nw",
    "clusters": [],
    "sentences": sentences,
    "speakers": speakers,
  }

def print_predictions(example):
  words = util.flatten(example["sentences"])
  for cluster in example["predicted_clusters"]:
    print(u"Predicted cluster: {}".format([" ".join(words[m[0]:m[1]+1]) for m in cluster]))

def make_predictions(text, model):
  example = create_example(text)
  tensorized_example = model.tensorize_example(example, is_training=False)
  feed_dict = {i:t for i,t in zip(model.input_tensors, tensorized_example)}
  _, _, _, mention_starts, mention_ends, antecedents, antecedent_scores, head_scores = session.run(model.predictions + [model.head_scores], feed_dict=feed_dict)

  predicted_antecedents = model.get_predicted_antecedents(antecedents, antecedent_scores)

  example["predicted_clusters"], _ = model.get_predicted_clusters(mention_starts, mention_ends, predicted_antecedents)
  example["top_spans"] = zip((int(i) for i in mention_starts), (int(i) for i in mention_ends))
  example["head_scores"] = head_scores.tolist()
  return example

# next 3 methods added
def get_predictions_list(example):
  cluster_list = []
  for cluster in example["predicted_clusters"]:
    clust_l = []
    for t in cluster:
      tup_list = list(t)
      clust_l.append(tup_list)
    cluster_list.append(clust_l)

  return cluster_list

def make_and_get_predictions_list(text):
  config = util.initialize_from_env()
  model = cm.CorefModel(config)
  with tf.Session() as session:
    model.restore(session)
    return get_predictions_list(make_predictions(text, model))


def make_and_write_predictions_to_file(text, destination: str):
  pred_list = make_and_get_predictions_list(text)
  json.dump(pred_list, open('pred_clusters.json', 'w'))
  export2xml('pred_clusters.json', destination)

if __name__ == "__main__":
  config = util.initialize_from_env()
  model = cm.CorefModel(config)
  with tf.Session() as session:
    model.restore(session)
    while True:
      text = input("Document text: ")
      print_predictions(make_predictions(text, model))
