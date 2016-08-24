import sys

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn import metrics, cross_validation
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from Dataset import Dataset
from Utils.preprocessing import preproc_text as tp
from Utils.tokenization import Tokenize
from Utils.validation import CrossValidation

dataset_path = sys.argv[1]

""" read from json """
dataset = Dataset(dataset=dataset_path)

""" Initialise default tokenizer """
tok = Tokenize.TweetTokenizer()

"""
    Split data into train, test and validation
     ----------------------------------------------------------
    |               70% TRAIN            |      30% TEST       |
     ----------------------------------------------------------
"""
PERCENT_TRAIN = 0.7
PERCENT_TEST = 0.3

raw_train_data, train_targets = dataset.getData(n=len(dataset) * PERCENT_TRAIN,
                                                cut_long_tail=False)
raw_train_data_nlt, train_targets_nlt = dataset.getData(n=len(dataset) * PERCENT_TRAIN,
                                                        cut_long_tail=True)

raw_test_data, test_targets = dataset.getData(offset=len(dataset) * PERCENT_TRAIN,
                                              n=len(dataset) * PERCENT_TEST,
                                              cut_long_tail=False)
raw_test_data_nlt, test_targets_nlt = dataset.getData(offset=len(dataset) * PERCENT_TRAIN,
                                                      n=len(dataset) * PERCENT_TEST,
                                                      cut_long_tail=True)

print('SAMPLES = {}, TRAIN = {} ({:.2%}), TEST = {} ({:.2%}) (EXCEPT FOR CV CASES)'.format(len(dataset),
                                                                                           len(raw_train_data),
                                                                                           PERCENT_TRAIN,
                                                                                           len(raw_test_data),
                                                                                           PERCENT_TEST))


def e1():
    """
    E1 - Binary BagOfWords
    Full text gets tokenized and transformed into a binary term-document-matrix.
    Dataset with long tail
    """
    print('========== e1: BINARY BOW WITH LONG TAIL BEGIN ==========')
    preproc_text = tp.TextProcessor(blind_urls=False, remove_urls=False, remove_user_mentions=False,
                                    remove_hashtags=False,
                                    transform_lowercase=False, expand_urls=False)
    print('** preproc config:', preproc_text, '**')
    print('Training classifier...', end='', flush=True)
    pipeline = Pipeline(
        [('vect', CountVectorizer(preprocessor=preproc_text, tokenizer=tok, lowercase=False, binary=True)),
         ('clf', MultinomialNB()),
         ])
    pipeline.fit(raw_train_data, train_targets)
    print('done.')
    print('Predicting test data...', end='', flush=True)
    predicted = pipeline.predict(raw_test_data)

    print('done.')

    precision_micro = precision_score(test_targets, predicted, average='micro')
    precision_macro = precision_score(test_targets, predicted, average='macro')
    precision_weighted = precision_score(test_targets, predicted, average='weighted')
    recall_micro = recall_score(test_targets, predicted, average='micro')
    recall_macro = recall_score(test_targets, predicted, average='macro')
    recall_weighted = recall_score(test_targets, predicted, average='weighted')
    f1_micro = f1_score(test_targets, predicted, average='micro')
    f1_macro = f1_score(test_targets, predicted, average='macro')
    f1_weighted = f1_score(test_targets, predicted, average='weighted')
    accuracy = accuracy_score(test_targets, predicted)
    print('--- PrintingScorer ---')
    print("Precision:\tmicro={}\tmacro={}\tweighted={}".format(precision_micro, precision_macro, precision_weighted))
    print("Recall:\t\tmicro={}\tmacro={}\tweighted={}".format(recall_micro, recall_macro, recall_weighted))
    print("F-Measure:\tmicro={}\tmacro={}\tweighted={}".format(f1_micro, f1_macro, f1_weighted))
    print("Accuracy:\t{}".format(accuracy))

    print('--- FULL CLASSIFICATION REPORT WITH ALL CLASSES ---')
    labels = list(set(test_targets))  # take only labels that have support
    target_names = [dataset.getTargetName(x) for x in labels]
    print(metrics.classification_report(test_targets, predicted, labels=labels, target_names=target_names, digits=4))
    print('--- CLASSIFICATION REPORT FOR LONG-TAIL CLASSES ---')
    labels_longtail = list(set(test_targets).difference(set(test_targets_nlt)))  # take only labels that have support
    target_names_longtail = [dataset.getTargetName(x) for x in labels]
    print(metrics.classification_report(test_targets, predicted, labels=labels_longtail,
                                        target_names=target_names_longtail, digits=4))

    print('========== e1: BINARY BOW END ==========')


def e2():
    """
    E2 - Binary BagOfWords without long-tail
    Full text gets tokenized and transformed into a binary term-document-matrix.
    Dataset without long tail
    """
    print('========== e2: BINARY BOW WITHOUT LONG-TAIL BEGIN ==========')
    preproc_text = tp.TextProcessor(blind_urls=False, remove_urls=False, remove_user_mentions=False,
                                    remove_hashtags=False,
                                    transform_lowercase=False, expand_urls=False)
    print('** preproc config:', preproc_text, '**')

    """ Initialise PrintScorer for cross-validation"""
    scorer = CrossValidation.PrintingScorer()

    print('Cross Validation with 90% long-tail-cutoff...', end='', flush=True)
    pipeline = Pipeline(
        [('vect', CountVectorizer(preprocessor=preproc_text, tokenizer=tok, lowercase=False, binary=True)),
         ('clf', MultinomialNB()),
         ])
    cross_validation.cross_val_score(pipeline, raw_train_data_nlt, train_targets_nlt, cv=5, n_jobs=5, scoring=scorer)
    print('done.')

    dataset_50percent = Dataset(dataset_path, long_tail_cutoff=0.5)
    print('Cross Validation with 50% long-tail-cutoff...', end='', flush=True)
    raw_data_nlt_50, targets_nlt_50 = dataset_50percent.getData(cut_long_tail=True)
    cross_validation.cross_val_score(pipeline, raw_data_nlt_50, targets_nlt_50, cv=5, n_jobs=5, scoring=scorer)
    print('done.')
    print('--- CLASSIFICATION REPORT FOR LONG-TAIL-CUTOFF 50% CLASSES ---')
    predicted = cross_validation.cross_val_predict(pipeline, raw_data_nlt_50, targets_nlt_50, cv=5, n_jobs=5)
    labels = list(set(targets_nlt_50))  # take only labels that have support
    target_names = [dataset.getTargetName(x) for x in labels]
    print(metrics.classification_report(targets_nlt_50, predicted, labels=labels,
                                        target_names=target_names, digits=4))
    print('========== e2: BINARY BOW WITHOUT LONG-TAIL END ==========')


def e3():
    """
        E3 - TF/IDF BagOfWords without long-tail
        Full text gets tokenized and transformed into a tf/idf weighted term-document-matrix.
        Dataset without long tail
        """
    print('========== e3: TF/IDF BOW WITHOUT LONG-TAIL (0.9 CutOff) BEGIN ==========')
    preproc_text = tp.TextProcessor(blind_urls=False, remove_urls=False, remove_user_mentions=False,
                                    remove_hashtags=False,
                                    transform_lowercase=False, expand_urls=False)
    print('** preproc config:', preproc_text, '**')

    """ Initialise PrintScorer for cross-validation"""
    scorer = CrossValidation.PrintingScorer()

    print('Cross Validation...', end='', flush=True)
    pipeline = Pipeline(
        [('vect', TfidfVectorizer(preprocessor=preproc_text, tokenizer=tok, lowercase=False, use_idf=True, )),
         ('clf', MultinomialNB()),
         ])
    cross_validation.cross_val_score(pipeline, raw_train_data_nlt, train_targets_nlt, cv=5, n_jobs=5, scoring=scorer)
    print('done.')
    print('========== e3: TF/IDF BOW WITHOUT LONG-TAIL END ==========')


def e4():
    """
        E4 - TF/IDF BagOfWords without long-tail
        Made additional changes in preproc, see printed config
        Full text gets tokenized and transformed into a tf/idf weighted term-document-matrix.
        Dataset without long tail
        """
    print('========== e4: TF/IDF BOW WITHOUT LONG-TAIL CLEANED TWEET 1 BEGIN ==========')
    preproc_text = tp.TextProcessor(blind_urls=False, remove_urls=True, remove_user_mentions=True,
                                    remove_hashtags=True,
                                    transform_lowercase=True, expand_urls=False)
    print('** preproc config:', preproc_text, '**')
    print('Training classifier...', end='', flush=True)
    pipeline = Pipeline(
        [('vect', TfidfVectorizer(preprocessor=preproc_text, tokenizer=tok, lowercase=False)),
         ('clf', MultinomialNB()),
         ])
    pipeline.fit(raw_train_data_nlt, train_targets_nlt)
    print('done.')
    print('Predicting test data...', end='', flush=True)
    predicted = pipeline.predict(raw_test_data_nlt)
    print('done.')
    print('--- FULL CLASSIFICATION REPORT ---')
    labels = list(set(test_targets_nlt))  # take only labels that have support
    target_names = [dataset.getTargetName(x) for x in labels]
    print(metrics.classification_report(test_targets_nlt, predicted, labels=labels, target_names=target_names,
                                        digits=4))
    print('========== e4: TF/IDF BOW WITHOUT LONG-TAIL CLEANED TWEET 1 END ==========')


def e5():
    """
        E5 - Character N-Grams
        Made additional changes in preproc, see printed config
        Full text gets tokenized and transformed into a tf/idf weighted term-document-matrix.
        Dataset without long tail
        """
    print('========== e5: CHARACTER N GRAMS (1,3) WITHOUT LONG-TAIL EXPANDED URLS ==========')
    preproc_text = tp.TextProcessor(blind_urls=False, remove_urls=False, remove_user_mentions=True,
                                    remove_hashtags=False,
                                    transform_lowercase=True, expand_urls=True)
    print('** preproc config:', preproc_text, '**')
    print('Training classifier...', end='', flush=True)
    pipeline = Pipeline(
        [('vect', CountVectorizer(preprocessor=preproc_text, analyzer='char', ngram_range=(1, 3))),
         ('clf', MultinomialNB()),
         ])
    pipeline.fit(raw_train_data_nlt, train_targets_nlt)
    print('done.')
    print('Predicting test data...', end='', flush=True)
    predicted = pipeline.predict(raw_test_data_nlt)
    print('done.')
    print('--- FULL CLASSIFICATION REPORT ---')
    labels = list(set(test_targets_nlt))  # take only labels that have support
    target_names = [dataset.getTargetName(x) for x in labels]
    print(metrics.classification_report(test_targets_nlt, predicted, labels=labels, target_names=target_names,
                                        digits=4))

    print('========== e5: CHARACTER N GRAMS (1,3) WITHOUT LONG-TAIL EXPANDED URLS END ==========')


"""Run experiments"""
e1()
# e2()
# e3()
# e4()
# e5()
