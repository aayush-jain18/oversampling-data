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

    # Highlight: In case need to get a elbow graph to determine
    #  the number of clusters
    wcss = []
    for i in range(1, 11):
        kmeans = KMeans(n_clusters=i, init='k-means++', random_state=42)
        kmeans.fit(X)
        wcss.append(kmeans.inertia_)
    logging.info(f'Elbow curve for cluster: {wcss}')
    # plt.plot(range(1, 11), wcss)
    # plt.title('The Elbow Method')
    # plt.xlabel('Number of clusters')
    # plt.ylabel('WCSS')
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

    # FIXME: hierarchical-clustering is crashing the laptop :(
    # # Dendrograms to identify the number of clusters to make
    # plt.figure(figsize=(10, 7))
    # plt.title("Dendrogram")
    # dend = shc.dendrogram(shc.linkage(data, method='ward'))
    # plt.savefig(output_dendo)
    # cluster = AgglomerativeClustering(n_clusters=5,
    #                                    affinity='euclidean',
    #                                    linkage='ward')
    # cluster.fit_predict(X)
    # dendrogram(
    #     H_cluster,
    #     truncate_mode='lastp',  # show only the last p merged clusters
    #     p=5,  # show only the last p merged clusters
    #     leaf_rotation=90.,
    #     leaf_font_size=12.,
    #     show_contracted=True,  # to get a distribution impression
    #     in truncated branches
    # )
    #
    # plt.figure(figsize=(10, 7))
    # plt.title("Data Clusters")
    # plt.scatter(data[:, 1], data[:, 0], c=cluster.labels_, cmap='rainbow')
    # plt.savefig(output_cluster)