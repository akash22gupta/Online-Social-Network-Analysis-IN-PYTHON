# coding: utf-8

"""
CS579: Assignment 2

In this assignment, you will build a text classifier to determine whether a
movie review is expressing positive or negative sentiment. The data come from
the website IMDB.com.

You'll write code to preprocess the data in different ways (creating different
features), then compare the cross-validation accuracy of each approach. Then,
you'll compute accuracy on a test set and do some analysis of the errors.

The main method takes about 40 seconds for me to run on my laptop. Places to
check for inefficiency include the vectorize function and the
eval_all_combinations function.

Complete the 14 methods below, indicated by TODO.

As usual, completing one method at a time, and debugging with doctests, should
help.
"""

# No imports allowed besides these.
from collections import Counter, defaultdict
from itertools import chain, combinations
import glob
import matplotlib.pyplot as plt
import numpy as np
import os
import re
from scipy.sparse import csr_matrix
from sklearn.cross_validation import KFold
from sklearn.linear_model import LogisticRegression
import string
import tarfile
import urllib.request


def download_data():
    """ Download and unzip data.
    DONE ALREADY.
    """
    url = 'https://www.dropbox.com/s/xk4glpk61q3qrg2/imdb.tgz?dl=1'
    urllib.request.urlretrieve(url, 'imdb.tgz')
    tar = tarfile.open("imdb.tgz")
    tar.extractall()
    tar.close()


def read_data(path):
    """
    Walks all subdirectories of this path and reads all
    the text files and labels.
    DONE ALREADY.

    Params:
      path....path to files
    Returns:
      docs.....list of strings, one per document
      labels...list of ints, 1=positive, 0=negative label.
               Inferred from file path (i.e., if it contains
               'pos', it is 1, else 0)
    """
    fnames = sorted([f for f in glob.glob(os.path.join(path, 'pos', '*.txt'))])
    data = [(1, open(f).readlines()[0]) for f in sorted(fnames)]
    fnames = sorted([f for f in glob.glob(os.path.join(path, 'neg', '*.txt'))])
    data += [(0, open(f).readlines()[0]) for f in sorted(fnames)]
    data = sorted(data, key=lambda x: x[1])
    return np.array([d[1] for d in data]), np.array([d[0] for d in data])


def tokenize(doc, keep_internal_punct=False):
    """
    Tokenize a string.
    The string should be converted to lowercase.
    If keep_internal_punct is False, then return only the alphanumerics (letters, numbers and underscore).
    If keep_internal_punct is True, then also retain punctuation that
    is inside of a word. E.g., in the example below, the token "isn't"
    is maintained when keep_internal_punct=True; otherwise, it is
    split into "isn" and "t" tokens.

    Params:
      doc....a string.
      keep_internal_punct...see above
    Returns:
      a numpy array containing the resulting tokens.

    >>> tokenize(" Hi there! Isn't this fun?", keep_internal_punct=False)
    array(['hi', 'there', 'isn', 't', 'this', 'fun'],
          dtype='<U5')
    >>> tokenize("Hi there! Isn't this fun? ", keep_internal_punct=True)
    array(['hi', 'there', "isn't", 'this', 'fun'],
          dtype='<U5')
    """
    ###TODO
    doc = doc.lower()
    if(keep_internal_punct):
        tokens = re.findall(r"[[\w_][^\s]*[\w_]|[\w_]", doc)

    else:
        tokens = re.sub('\W+', ' ', doc).split()

    return np.array(tokens)
    pass


def token_features(tokens, feats):
    """
    Add features for each token. The feature name
    is pre-pended with the string "token=".
    Note that the feats dict is modified in place,
    so there is no return value.

    Params:
      tokens...array of token strings from a document.
      feats....dict from feature name to frequency
    Returns:
      nothing; feats is modified in place.

    >>> feats = defaultdict(lambda: 0)
    >>> token_features(['hi', 'there', 'hi'], feats)
    >>> sorted(feats.items())
    [('token=hi', 2), ('token=there', 1)]
    """
    ###TODO
    count = Counter(tokens)
    for token in count:
        feats["token=" + token] = count[token]



def token_pair_features(tokens, feats, k=3):
    """
    Compute features indicating that two words occur near
    each other within a window of size k.

    For example [a, b, c, d] with k=3 will consider the
    windows: [a,b,c], [b,c,d]. In the first window,
    a_b, a_c, and b_c appear; in the second window,
    b_c, c_d, and b_d appear. This example is in the
    doctest below.
    Note that the order of the tokens in the feature name
    matches the order in which they appear in the document.
    (e.g., a__b, not b__a)

    Params:
      tokens....array of token strings from a document.
      feats.....a dict from feature to value
      k.........the window size (3 by default)
    Returns:
      nothing; feats is modified in place.

    >>> feats = defaultdict(lambda: 0)
    >>> token_pair_features(np.array(['a', 'b', 'c', 'd']), feats)
    >>> sorted(feats.items())
    [('token_pair=a__b', 1), ('token_pair=a__c', 1), ('token_pair=b__c', 2), ('token_pair=b__d', 1), ('token_pair=c__d', 1)]
    """
    ###TODO
    token_pair =[]
    temp_list = []
    length = len(tokens)
    i=0
    while i<=length-1 and i+(k-1)<=length-1:
        j=i
        l=j+(k-1)
        while j<=l:
            temp_list.append(tokens[j])
            if(len(temp_list)==k):
                temp = list(combinations(temp_list,2))
                for pair in temp:
                    token_pair.append(pair[0]+"__"+pair[1])
            j+=1
        temp_list = []
        i+=1

    count = Counter(token_pair)
    for token in count:
        feats["token_pair=" + token] = count[token]



neg_words = set(['bad', 'hate', 'horrible', 'worst', 'boring'])
pos_words = set(['awesome', 'amazing', 'best', 'good', 'great', 'love', 'wonderful'])

def lexicon_features(tokens, feats):
    """
    Add features indicating how many time a token appears that matches either
    the neg_words or pos_words (defined above). The matching should ignore
    case.

    Params:
      tokens...array of token strings from a document.
      feats....dict from feature name to frequency
    Returns:
      nothing; feats is modified in place.

    In this example, 'LOVE' and 'great' match the pos_words,
    and 'boring' matches the neg_words list.
    >>> feats = defaultdict(lambda: 0)
    >>> lexicon_features(np.array(['i', 'LOVE', 'this', 'great', 'boring', 'movie']), feats)
    >>> sorted(feats.items())
    [('neg_words', 1), ('pos_words', 2)]
    """
    ###TODO
    for token in tokens:
        if(token.lower() in neg_words):
            feats['neg_words']+= 1
        elif(token.lower() in pos_words):
            feats['pos_words']+= 1
    if(feats['neg_words'] == 0):
        feats['neg_words'] = 0
    if(feats['pos_words'] == 0):
        feats['pos_words'] = 0
    pass



def featurize(tokens, feature_fns):
    """
    Compute all features for a list of tokens from
    a single document.

    Params:
      tokens........array of token strings from a document.
      feature_fns...a list of functions, one per feature
    Returns:
      list of (feature, value) tuples, SORTED alphabetically
      by the feature name.

    >>> feats = featurize(np.array(['i', 'LOVE', 'this', 'great', 'movie']), [token_features, lexicon_features])
    >>> feats
    [('neg_words', 0), ('pos_words', 2), ('token=LOVE', 1), ('token=great', 1), ('token=i', 1), ('token=movie', 1), ('token=this', 1)]
    """
    ###TODO
    feats = defaultdict(lambda:0)
    for function in feature_fns:
        function(tokens,feats)
    return sorted(feats.items())
    pass


def vectorize(tokens_list, feature_fns, min_freq, vocab=None):
    """
    Given the tokens for a set of documents, create a sparse
    feature matrix, where each row represents a document, and
    each column represents a feature.

    Params:
      tokens_list...a list of lists; each sublist is an
                    array of token strings from a document.
      feature_fns...a list of functions, one per feature
      min_freq......Remove features that do not appear in
                    at least min_freq different documents.
    Returns:
      - a csr_matrix: See https://goo.gl/f5TiF1 for documentation.
      This is a sparse matrix (zero values are not stored).
      - vocab: a dict from feature name to column index. NOTE
      that the columns are sorted alphabetically (so, the feature
      "token=great" is column 0 and "token=horrible" is column 1
      because "great" < "horrible" alphabetically),

    >>> docs = ["Isn't this movie great?", "Horrible, horrible movie"]
    >>> tokens_list = [tokenize(d) for d in docs]
    >>> feature_fns = [token_features]
    >>> X, vocab = vectorize(tokens_list, feature_fns, min_freq=1)
    >>> type(X)
    <class 'scipy.sparse.csr.csr_matrix'>
    >>> X.toarray()
    array([[1, 0, 1, 1, 1, 1],
           [0, 2, 0, 1, 0, 0]], dtype=int64)
    >>> sorted(vocab.items(), key=lambda x: x[1])
    [('token=great', 0), ('token=horrible', 1), ('token=isn', 2), ('token=movie', 3), ('token=t', 4), ('token=this', 5)]
    """
    ###TODO
    feats=[]
    row=[]
    column=[]
    key=[]
    token_total=defaultdict(dict)
    main_vocab={}
    token_count = defaultdict(list)
    if vocab == None:
        mapping=defaultdict(dict)
        i=0
        for document in tokens_list:
            #print (i)
            feat_urize = dict(featurize(document, feature_fns))
            #print(feat_urize)
            token_total.update(feat_urize)
            mapping[i] = feat_urize
            feat_urize = dict.fromkeys(feat_urize,i)
            for k,v in feat_urize.items():
                token_count[k].append(v)
            i+=1
            #print(token_count)
        for k,v in sorted(token_count.items()):
            if len(v) >= min_freq:
                main_vocab[k] = v
            #print(sorted(main_vocab))

        value = 0
        for k in sorted(main_vocab):
            main_vocab[k] = value
            value+=1
        #print(sorted(main_vocab.items()))
        #print(feat_urize)
        #print(sorted(token_total.items()))
        #print(sorted(token_count.items()))

        for k in sorted(main_vocab):
            for v in sorted(token_count[k]):
                if k in mapping[v]:
                    row.append(v)
                    column.append(main_vocab[k])
                    key.append(mapping[v][k])
        x = csr_matrix((key,(row,column)), shape=(len(tokens_list), len(main_vocab)))
        return x,main_vocab
    else:
        j=0
        for document in tokens_list:
            feat_urize = dict(featurize(document, feature_fns))
            for feature in feat_urize:
                if feature in vocab:
                    row.append(j)
                    column.append(vocab[feature])
                    key.append(feat_urize[feature])
            j+=1
        x = csr_matrix((key,(row,column)), shape=(len(tokens_list), len(vocab)))
        return x,vocab

    pass

def accuracy_score(truth, predicted):
    """ Compute accuracy of predictions.
    DONE ALREADY
    Params:
      truth.......array of true labels (0 or 1)
      predicted...array of predicted labels (0 or 1)
    """
    return len(np.where(truth==predicted)[0]) / len(truth)


def cross_validation_accuracy(clf, X, labels, k):
    """
    Compute the average testing accuracy over k folds of cross-validation. You
    can use sklearn's KFold class here (no random seed, and no shuffling
    needed).

    Params:
      clf......A LogisticRegression classifier.
      X........A csr_matrix of features.
      labels...The true labels for each instance in X
      k........The number of cross-validation folds.

    Returns:
      The average testing accuracy of the classifier
      over each fold of cross-validation.
    """
    ###TODO

    kf = KFold(len(labels), k)
    accuracies = []

    for train_idx, test_idx in kf:
        clf.fit(X[train_idx], labels[train_idx])
        accuracies.append(accuracy_score(labels[test_idx],clf.predict(X[test_idx])))

    return np.mean(accuracies)
    pass


def eval_all_combinations(docs, labels, punct_vals,
                          feature_fns, min_freqs):
    """
    Enumerate all possible classifier settings and compute the
    cross validation accuracy for each setting. We will use this
    to determine which setting has the best accuracy.

    For each setting, construct a LogisticRegression classifier
    and compute its cross-validation accuracy for that setting.

    In addition to looping over possible assignments to
    keep_internal_punct and min_freqs, we will enumerate all
    possible combinations of feature functions. So, if
    feature_fns = [token_features, token_pair_features, lexicon_features],
    then we will consider all 7 combinations of features (see Log.txt
    for more examples).

    Params:
      docs..........The list of original training documents.
      labels........The true labels for each training document (0 or 1)
      punct_vals....List of possible assignments to
                    keep_internal_punct (e.g., [True, False])
      feature_fns...List of possible feature functions to use
      min_freqs.....List of possible min_freq values to use
                    (e.g., [2,5,10])

    Returns:
      A list of dicts, one per combination. Each dict has
      four keys:
      'punct': True or False, the setting of keep_internal_punct
      'features': The list of functions used to compute features.
      'min_freq': The setting of the min_freq parameter.
      'accuracy': The average cross_validation accuracy for this setting, using 5 folds.

      This list should be SORTED in descending order of accuracy.

      This function will take a bit longer to run (~20s for me).
    """
    ###TODO
    all_feature_combinations=[]
    final_list = []
    for i in range(1, len(feature_fns)+1):
        combination_list = [list(combination) for combination in combinations(feature_fns,i)]
        all_feature_combinations.extend(combination_list)
    for true_false in punct_vals:
        tokens_list = [tokenize(document, true_false) for document in docs]
        for feature in all_feature_combinations:
            for min_freq in min_freqs:
                X, vocab = vectorize(tokens_list, feature, min_freq)
                #print("Sparse Matrix Shape:", X.shape)
                accuracy = cross_validation_accuracy(LogisticRegression(), X, labels, 5)
                final_list.append({'features': feature, 'punct': true_false, 'accuracy': accuracy, 'min_freq': min_freq})

    return sorted(final_list, key = lambda x: (-x['accuracy'], -x['min_freq']))
    pass


def plot_sorted_accuracies(results):
    """
    Plot all accuracies from the result of eval_all_combinations
    in ascending order of accuracy.
    Save to "accuracies.png".
    """
    ###TODO
    accuracy =[]
    for i in results:
        accuracy.append(i['accuracy'])
    accuracy = sorted(accuracy)
    x = np.arange((len(accuracy)))
    y = accuracy
    plt.plot(x,y)
    plt.xlabel("setting")
    plt.ylabel("accuracy")
    plt.savefig("accuracies.png")
    pass



def mean_accuracy_per_setting(results):
    """
    To determine how important each model setting is to overall accuracy,
    we'll compute the mean accuracy of all combinations with a particular
    setting. For example, compute the mean accuracy of all runs with
    min_freq=2.

    Params:
      results...The output of eval_all_combinations
    Returns:
      A list of (accuracy, setting) tuples, SORTED in
      descending order of accuracy.
    """
    ###TODO
    setting_acc = []
    temp =defaultdict(lambda: (0.0, 0))
    for result in results:
        temp["min_freq="+str(result["min_freq"])] = (temp["min_freq="+str(result["min_freq"])][0]+result["accuracy"],temp["min_freq="+str(result["min_freq"])][1]+1)
        func_key = " "
        for func in result["features"]:
            func_key+=" "+func.__name__
        temp["features="+func_key.strip()] = (temp["features="+func_key.strip()][0]+result["accuracy"],temp["features="+func_key.strip()][1]+1)
        temp["punct="+ str(result["punct"])] = (temp["punct="+ str(result["punct"])][0] + result["accuracy"], temp["punct="+ str(result["punct"])][1] + 1)

    for k in temp.keys():
        setting_acc.append(((temp[k][0]/temp[k][1]),k))

    set_acu= defaultdict(lambda: 0.)
    set_freq= defaultdict(lambda: 0)
    for result in results:
        set_acu["punct" + "="+ str(result["punct"])] += result["accuracy"]
        set_freq["punct" + "="+ str(result["punct"])] += 1
        function_name = "features="
        for function in result["features"]:
            function_name +=" "+function.__name__
        set_acu[function_name] += result["accuracy"]
        set_freq[function_name] += 1
        set_acu["min_freq" + "=" + str(result["min_freq"])] += result["accuracy"]
        set_freq["min_freq" + "=" + str(result["min_freq"])] += 1
    for k in set_acu:
        set_acu[k] = set_acu[k] / set_freq[k]

    return[(v,k) for k,v in sorted(set_acu.items(), key = lambda x: -x[1])]



def fit_best_classifier(docs, labels, best_result):
    """
    Using the best setting from eval_all_combinations,
    re-vectorize all the training data and fit a
    LogisticRegression classifier to all training data.
    (i.e., no cross-validation done here)

    Params:
      docs..........List of training document strings.
      labels........The true labels for each training document (0 or 1)
      best_result...Element of eval_all_combinations
                    with highest accuracy
    Returns:
      clf.....A LogisticRegression classifier fit to all
            training data.
      vocab...The dict from feature name to column index.
    """
    ###TODO
    token_list=[]
    punct = best_result["punct"]
    min_freq = best_result["min_freq"]
    feature = best_result["features"]
    clf = LogisticRegression()
    for document in docs:
        token_list.append(tokenize(document,punct))

    X,vocab = vectorize(token_list,feature,min_freq)
    clf.fit(X, labels)

    return clf,vocab


    pass


def top_coefs(clf, label, n, vocab):
    """
    Find the n features with the highest coefficients in
    this classifier for this label.
    See the .coef_ attribute of LogisticRegression.

    Params:
      clf.....LogisticRegression classifier
      label...1 or 0; if 1, return the top coefficients
              for the positive class; else for negative.
      n.......The number of coefficients to return.
      vocab...Dict from feature name to column index.
    Returns:
      List of (feature_name, coefficient) tuples, SORTED
      in descending order of the coefficient for the
      given class label.
    """
    topids1 = []
    top_coef1 = []
    coef1 = clf.coef_[0]
    if label == 1:
        topids1 = np.argsort(coef1)[::-1][:n]
        top_coef1 = coef1[topids1]  #coefficient
    else:
        topids1 = np.argsort(coef1)[:n]
        top_coef1 = coef1[topids1] * -1

    top_coef_terms1 = np.array(sorted(vocab.items(), key=lambda x: x[1]))[topids1]


    coef = clf.coef_[0]
    #top_index = []
    top_coef = []
    list_coef = []
    if label == 1:
        top_index = np.argsort(coef)[::-1][:n]
        #print(top_index)
    else:
        #print(top_index)
        top_index = np.argsort(coef)[::1][:n]

    for i in top_index:
        for j in vocab.items():
            if j[1]==i:
                top_coef_word = j[0]
        top_coef = coef[i]
        list_coef.append((top_coef_word ,abs(top_coef)))

    return list_coef



def parse_test_data(best_result, vocab):
    """
    Using the vocabulary fit to the training data, read
    and vectorize the testing data. Note that vocab should
    be passed to the vectorize function to ensure the feature
    mapping is consistent from training to testing.

    Note: use read_data function defined above to read the
    test data.

    Params:
      best_result...Element of eval_all_combinations
                    with highest accuracy
      vocab.........dict from feature name to column index,
                    built from the training data.
    Returns:
      test_docs.....List of strings, one per testing document,
                    containing the raw.
      test_labels...List of ints, one per testing document,
                    1 for positive, 0 for negative.
      X_test........A csr_matrix representing the features
                    in the test data. Each row is a document,
                    each column is a feature.
    """
    ###TODO
    test_docs, test_labels = read_data(os.path.join('data','test'))
    punct = best_result["punct"]
    min_freq = best_result["min_freq"]
    feature = best_result["features"]
    tokens_list=[]

    for document in test_docs:
        tokens_list.append(tokenize(document,punct))

    X_test , vocab_new = vectorize(tokens_list, feature, min_freq, vocab)

    return test_docs, test_labels, X_test
    pass


def print_top_misclassified(test_docs, test_labels, X_test, clf, n):
    """
    Print the n testing documents that are misclassified by the
    largest margin. By using the .predict_proba function of
    LogisticRegression <https://goo.gl/4WXbYA>, we can get the
    predicted probabilities of each class for each instance.
    We will first identify all incorrectly classified documents,
    then sort them in descending order of the predicted probability
    for the incorrect class.
    E.g., if document i is misclassified as positive, we will
    consider the probability of the positive class when sorting.

    Params:
      test_docs.....List of strings, one per test document
      test_labels...Array of true testing labels
      X_test........csr_matrix for test data
      clf...........LogisticRegression classifier fit on all training
                    data.
      n.............The number of documents to print.

    Returns:
      Nothing; see Log.txt for example printed output.
    """
    ###TODO

    labels_predict = clf.predict(X_test)
    labels_different = np.where(labels_predict != test_labels)[0]  #different prediction indice

    predict_prob = clf.predict_proba(X_test)
    pred_wrong = predict_prob[labels_different]
    ids = np.argsort(np.amax(pred_wrong, axis = 1))[::-1][:n]   #first maximum n indice
    value=clf.predict(X_test)
    list_of_incorrect=[]
    predict_matrix= clf.predict_proba(X_test)
    for i in range(len(predict_matrix)):
                   incorrect_dict={}
                   if value[i]!=test_labels[i]:
                    incorrect_dict.update({'docs':test_docs[i]})
                    incorrect_dict.update({'label':test_labels[i]})
                    incorrect_dict.update({'predicted':value[i]})
                    list_of_incorrect.append(incorrect_dict)
    #final_list=sorted(list_of_incorrect, key=lambda k: -k['proba'])
    count=0


    predict = clf.predict(X_test)
    predict_prob = clf.predict_proba(X_test)

    w_p =[]

    for i in range(len(test_docs)):
        if(predict[i] != test_labels[i]):
            w_p.append((predict_prob[i][predict[i]],i,predict[i],test_labels[i]))

    predictions = sorted(w_p, key=lambda x:-x[0])
    for i in predictions[:n]:
        print("\n" + "truth=" + str(i[3]) + " predicted=" + str(i[2]) + " proba=" + str(float("{0:.6f}".format(i[0]))))
        print(test_docs[i[1]])

    pass


def main():
    """
    Put it all together.
    ALREADY DONE.
    """
    feature_fns = [token_features, token_pair_features, lexicon_features]
    # Download and read data.
    download_data()
    docs, labels = read_data(os.path.join('data', 'train'))
    # Evaluate accuracy of many combinations
    # of tokenization/featurization.
    results = eval_all_combinations(docs, labels,
                                    [True, False],
                                    feature_fns,
                                    [2,5,10])
    # Print information about these results.
    best_result = results[0]
    worst_result = results[-1]
    print('best cross-validation result:\n%s' % str(best_result))
    print('worst cross-validation result:\n%s' % str(worst_result))
    plot_sorted_accuracies(results)
    print('\nMean Accuracies per Setting:')
    print('\n'.join(['%s: %.5f' % (s,v) for v,s in mean_accuracy_per_setting(results)]))
    # Fit best classifier.
    clf, vocab = fit_best_classifier(docs, labels, results[0])
    # Print top coefficients per class.
    print('\nTOP COEFFICIENTS PER CLASS:')
    print('negative words:')
    print('\n'.join(['%s: %.5f' % (t,v) for t,v in top_coefs(clf, 0, 5, vocab)]))
    print('\npositive words:')
    print('\n'.join(['%s: %.5f' % (t,v) for t,v in top_coefs(clf, 1, 5, vocab)]))
    # Parse test data
    test_docs, test_labels, X_test = parse_test_data(best_result, vocab)

    # Evaluate on test set.
    predictions = clf.predict(X_test)
    print('testing accuracy=%f' %
          accuracy_score(test_labels, predictions))
    print('\nTOP MISCLASSIFIED TEST DOCUMENTS:')
    print_top_misclassified(test_docs, test_labels, X_test, clf, 5)


if __name__ == '__main__':
    main()
