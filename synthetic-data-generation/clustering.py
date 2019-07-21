"""
The KMeans algorithm clusters data by trying to separate samples
in n groups of equal variance, minimizing a criterion known as the
inertia or within-cluster sum-of-squares.
"""
import logging

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
# from scipy.cluster.hierarchy import dendrogram, linkage
# from sklearn.cluster import AgglomerativeClustering


# TODO: Add Logging to the module
def kmeans_cluster(df,
                   independent_columns,
                   output_cluster,
                   n_clusters=5, random_state=1234,
                   ):
    """
    This method draws a scatter plot of cluster for categorical data
    of input DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame for kmeans cluster scatter plot
    output_cluster : str
        File path to store image of scatter plot
    n_clusters : int
        The number of clusters to form as well as the
        number of centroids to generate
    random_state : int, RandomState instance or None (default 1234)
        Determines random number generation for centroid initialization.
        Use an int to make the randomness deterministic.
    independent_columns : list/tuples
        array-like, sparse matrix
    """
    # FIXME: parametrize this input
    logging.info(f'using {independent_columns} columns to transform cluster.')
    X = df[independent_columns].values
    logging.info(f'{n_clusters} number of clusters to form as well as the '
                 'number of centroids to generate ')
    kmeans = KMeans(n_clusters, init='k-means++', random_state=random_state)
    y_kmeans = kmeans.fit_predict(X)
    # Visualising the clusters
    plt.scatter(X[:, 0], X[:, 1],
                c=y_kmeans, s=15,
                cmap='viridis')
    plt.scatter(kmeans.cluster_centers_[:, 0],
                kmeans.cluster_centers_[:, 1],
                s=17, label='Centroids')
    plt.title('Data Clusters')
    plt.legend()
    plt.savefig(output_cluster)
    plt.close()

    df['cluster'] = pd.DataFrame(y_kmeans)
    kmeans_mean_cluster = pd.DataFrame(df.groupby('cluster').mean())
    logging.info(f'Cluster info:\n{kmeans_mean_cluster}')
