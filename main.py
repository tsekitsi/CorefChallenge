import logging
import warnings
from allennlp.predictors.predictor import Predictor

## Just to ignore warning messages:
logging.getLogger("allennlp").setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore")

predictor = Predictor.from_path("https://s3-us-west-2.amazonaws.com/allennlp/models/coref-model-2018.02.05.tar.gz")
results = predictor.predict(
    document="My sister and I met her friends, and then she left with them and left me alone."
)

def clustersToString(pred_results):
    top_spans = pred_results.get('top_spans')
    doc = pred_results.get('document')
    clusters = pred_results.get('clusters')
    # top_spans from list of lists to list of strings:
    top_spans_dict = {}
    for span in top_spans:
        span_as_str = str(span)
        a = span[0]  # span is a tuple, so extract its components
        b = span[-1]
        temp = ''
        for i in range(a, b + 1):
            temp = temp + doc[i] + ' '
        temp = temp[0:-1]
        top_spans_dict[span_as_str] = temp

    # clusters from list of lists of lists to dict of lists of strings:
    clusters_dict = {}
    i = 0
    for cluster in clusters:
        temp = list()
        for span in cluster:
            temp.append(top_spans_dict.get(str(span)))
        clusters_dict[i] = temp
        i += 1

    return clusters_dict

print("Clusters: " + str(clustersToString(results)))