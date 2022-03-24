import os
import sys
import argparse
from utils import *

if __name__ == "_main__":
    parser = argparse.ArgumentParser(description='Classification and embeddings for the graphs.')
    parser.add_argument('name', metavar='name_inst', type=str, 
                    help='Name of the water installation.')
    parser.add_argument('--c', metavar='classifier', type=str, help='Classification method')
    parser.add_argument('--e', metavar='epochs', type=int, help='Epochs for training the embeddings')
    parser.add_argument('--emb', metavar='embedding', type=str, help='Embedding method')
    parser.add_argument('--d', metavar='dimensions', type=int, help='Dimension size for embedding')
    parser.add_argument('--k', metavar='kvalue', type=float, help='k-Value for RanGraph2Vec')

    args = parser.parse_args()

    name = args.name
    classifier = args.classifier if  args.classifier else "SVM"
    epochs = args.epochs if  args.epochs else 100
    embedding = args.embedding if  args.embedding else "g2v"
    dimensions = args.dimensions if  args.dimensions else 256
    k = args.kvalue if args.kvalue and <= 1.0 else 0.75

    data, target = load_pickle(name)
    embeddings = get_embeddings(data, dimensions=dimensions, method=embedding, epochs=epochs)

    indexes = np.random.permutation(len(data))
    embeddings, target = np.array(embeddings), np.array(target)
    embeddings, target = embeddings[indexes], target[indexes]

    X_train, X_test, y_train, y_test = train_test_split(embeddings, target, test_size=0.1, shuffle=False)
    clf, _ =  classification(X_train, y_train, method=classifier)
    predicted =  clf.predict(X_test)
    acc, f1, auc = get_scores(predicted, y_test)
    print(f"\tAcc: {acc}\n\tF1 : {f1}\n\tAUC: {auc}\n\tBest: {best_scores}")

"""
–c 	    Classifier 	                SVM, RF, DT, GNN 	            SVM
–e 	    Epochs 	                    Any integer 	                100
–emb 	Embedding Method 	        g2v, rg2v, sf 	                g2v
–d 	    Embedding Dimension 	    Any integer 	                256
–k 	    k-value for RanGraph2Vec 	Decimal number from range 0-1 	0.75
"""