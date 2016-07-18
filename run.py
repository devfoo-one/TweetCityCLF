import sys

from sklearn.feature_extraction.text import CountVectorizer

from Dataset import Dataset
from Utils.preprocessing import preproc_text as tp
from Utils.tokenization import tweet_tokenizer

dataset_path = sys.argv[1]

"""read from json"""
dataset = Dataset(dataset=dataset_path)
tok = tweet_tokenizer.Tokenizer()
raw_train_data, train_targets = dataset.getData(n=len(dataset) * 0.8, cut_long_tail=True)  # get 80% of data for training
raw_test_data_e1, test_targets_e1 = dataset.getData(offset=len(dataset) * 0.8, n=len(dataset) * 0.1, cut_long_tail=True)  # get another 10% for testing

print('---------- e1: BOW BASELINE ----------')

e1_preproc_text = tp.TextProcessor(blind_urls=False, remove_urls=False, remove_user_mentions=False, remove_hashtags=False,
                                   transform_lowercase=False, expand_urls=False)
print('** preproc config:', e1_preproc_text, '**')

test_data_e1 = [e1_preproc_text.digest(tweet) for tweet in raw_test_data_e1]
cv_e1 = CountVectorizer(preprocessor=e1_preproc_text, tokenizer=tok, lowercase=False, binary=True)
tdm_e1 = cv_e1.fit_transform(raw_train_data)  # create term-document matrix

for i, tweet in enumerate(raw_train_data):
    print('"', tweet['text'], '" got transformed into...', sep='')
    for featureID, count in enumerate(
            tdm_e1.getrow(i).toarray()[0]):  # .toarray()[0] to transform sparse matrix into list
        if count != 0:
            print(cv_e1.get_feature_names()[featureID], '(', count, '), ', sep='', end='')
    print('\n-----')

# clf_e1 = Pipeline([('vect', CountVectorizer()),
#                    ('clf', MultinomialNB()),
#                    ])
# clf_e1.fit(train_data_e1, train_targets_e1)
# predicted = clf_e1.predict(test_data_e1)
"""---------- e1: END ----------"""

# for tweet, target, predict in zip(train_data_e1, train_targets_e1, predicted):
#     print(dataset.getTargetName(target), dataset.getTargetName(predict))
# print(np.mean(predicted == test_targets_e1))

# train_data = [x['text'] for x in dataset.data[:1000]]
# train_targets = dataset.targets[:1000]
# test_data = [x['text'] for x in  dataset.data[1001:1100]]
# test_targets = dataset.targets[1001:1100]
# from sklearn.naive_bayes import MultinomialNB
# from sklearn.pipeline import Pipeline
# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.feature_extraction.text import TfidfTransformer
#
# text_clf = Pipeline([('vect', CountVectorizer()),
#                      ('tfidf', TfidfTransformer()),
#                      ('clf', MultinomialNB()),
# ])
#
# import numpy as np
# text_clf.fit(train_data, train_targets)
# predicted = text_clf.predict(test_data)
# print(np.mean(predicted == test_targets))
