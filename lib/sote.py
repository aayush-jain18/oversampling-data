"""Class to perform over-sampling using SMOTE."""

# Author: Aayush Jain
# License: MIT

import types
import warnings
from collections import Counter

import numpy as np
from scipy import sparse

from sklearn.base import clone
from sklearn.preprocessing import OneHotEncoder
from sklearn.svm import SVC
from sklearn.utils import check_random_state
from sklearn.utils import safe_indexing
from sklearn.utils import check_array
from sklearn.utils import check_X_y
from sklearn.utils.sparsefuncs_fast import csr_mean_variance_axis0
from sklearn.utils.sparsefuncs_fast import csc_mean_variance_axis0

from imblearn.utils import check_target_type
from imblearn.over_sampling import SMOTE


class SOTENC(SMOTE):
    """Synthetic Minority Over-sampling Technique for Nominal and Continuous
    (SMOTE-NC).
    Unlike :class:`SMOTE`, SMOTE-NC for dataset containing continuous and
    categorical features.
    Read more in the :ref:`User Guide <smote_adasyn>`.
    Parameters
    ----------
    categorical_features : ndarray, shape (n_cat_features,) or (n_features,)
        Specified which features are categorical. Can either be:
        - array of indices specifying the categorical features;
        - mask array of shape (n_features, ) and ``bool`` dtype for which
          ``True`` indicates the categorical features.
    {sampling_strategy}
    {random_state}
    k_neighbors : int or object, optional (default=5)
        If ``int``, number of nearest neighbours to used to construct synthetic
        samples.  If object, an estimator that inherits from
        :class:`sklearn.neighbors.base.KNeighborsMixin` that will be used to
        find the k_neighbors.
    n_jobs : int, optional (default=1)
        The number of threads to open if possible.
    Notes
    -----
    See the original paper [1]_ for more details.
    Supports mutli-class resampling. A one-vs.-rest scheme is used as
    originally proposed in [1]_.
    See
    :ref:`sphx_glr_auto_examples_over-sampling_plot_comparison_over_sampling.py`,
    and :ref:`sphx_glr_auto_examples_over-sampling_plot_smote.py`.
    See also
    --------
    SMOTE : Over-sample using SMOTE.
    SVMSMOTE : Over-sample using SVM-SMOTE variant.
    BorderlineSMOTE : Over-sample using Borderline-SMOTE variant.
    ADASYN : Over-sample using ADASYN.
    References
    ----------
    .. [1] N. V. Chawla, K. W. Bowyer, L. O.Hall, W. P. Kegelmeyer, "SMOTE:
       synthetic minority over-sampling technique," Journal of artificial
       intelligence research, 321-357, 2002.
    Examples
    --------
    >>> from collections import Counter
    >>> from numpy.random import RandomState
    >>> from sklearn.datasets import make_classification
    >>> from imblearn.over_sampling import SMOTENC
    >>> X, y = make_classification(n_classes=2, class_sep=2,
    ... weights=[0.1, 0.9], n_informative=3, n_redundant=1, flip_y=0,
    ... n_features=20, n_clusters_per_class=1, n_samples=1000, random_state=10)
    >>> print('Original dataset shape (%s, %s)' % X.shape)
    Original dataset shape (1000, 20)
    >>> print('Original dataset samples per class {}'.format(Counter(y)))
    Original dataset samples per class Counter({1: 900, 0: 100})
    >>> # simulate the 2 last columns to be categorical features
    >>> X[:, -2:] = RandomState(10).randint(0, 4, size=(1000, 2))
    >>> sm = SMOTENC(random_state=42, categorical_features=[18, 19])
    >>> X_res, y_res = sm.fit_resample(X, y)
    >>> print('Resampled dataset samples per class {}'.format(Counter(y_res)))
    Resampled dataset samples per class Counter({0: 900, 1: 900})
    """

    def __init__(self, categorical_features, sampling_strategy='auto',
                 random_state=None, k_neighbors=5, n_jobs=1):
        super(SOTENC, self).__init__(sampling_strategy=sampling_strategy,
                                     random_state=random_state,
                                     k_neighbors=k_neighbors,
                                     ratio=None)
        self.categorical_features = categorical_features

    @staticmethod
    def _check_X_y(X, y):
        """Overwrite the checking to let pass some string for categorical
        features.
        """
        y, binarize_y = check_target_type(y, indicate_one_vs_all=True)
        X, y = check_X_y(X, y, accept_sparse=['csr', 'csc'], dtype=None)
        return X, y, binarize_y

    def _validate_estimator(self):
        super(SOTENC, self)._validate_estimator()
        categorical_features = np.asarray(self.categorical_features)
        if categorical_features.dtype.name == 'bool':
            self.categorical_features_ = np.flatnonzero(categorical_features)
        else:
            if any([cat not in np.arange(self.n_features_)
                    for cat in categorical_features]):
                raise ValueError(
                    'Some of the categorical indices are out of range. Indices'
                    ' should be between 0 and {}'.format(self.n_features_))
            self.categorical_features_ = categorical_features
        self.continuous_features_ = np.setdiff1d(np.arange(self.n_features_),
                                                 self.categorical_features_)

    def _fit_resample(self, X, y):
        self.n_features_ = X.shape[1]
        self._validate_estimator()

        # compute the median of the standard deviation of the minority class
        target_stats = Counter(y)
        class_minority = min(target_stats, key=target_stats.get)
        X_continuous = X[:, self.continuous_features_]
        X_continuous = check_array(X_continuous, accept_sparse=['csr', 'csc'])
        X_minority = safe_indexing(X_continuous,
                                   np.flatnonzero(y == class_minority))
        if sparse.issparse(X):
            if X.format == 'csr':
                _, var = csr_mean_variance_axis0(X_minority)
            else:
                _, var = csc_mean_variance_axis0(X_minority)
        else:
            var = X_minority.var(axis=0)
        self.median_std_ = np.median(np.sqrt(var))

        X_categorical = X[:, self.categorical_features_]
        if X_continuous.dtype.name != 'object':
            dtype_ohe = X_continuous.dtype
        else:
            dtype_ohe = np.float64
        self.ohe_ = OneHotEncoder(sparse=True, handle_unknown='ignore',
                                  dtype=dtype_ohe)
        # the input of the OneHotEncoder needs to be dense
        X_ohe = self.ohe_.fit_transform(
            X_categorical.toarray() if sparse.issparse(X_categorical)
            else X_categorical)

        # we can replace the 1 entries of the categorical features with the
        # median of the standard deviation. It will ensure that whenever
        # distance is computed between 2 samples, the difference will be equal
        # to the median of the standard deviation as in the original paper.
        X_ohe.data = (np.ones_like(X_ohe.data, dtype=X_ohe.dtype) *
                      self.median_std_ / 2)
        X_encoded = sparse.hstack((X_continuous, X_ohe), format='csr')

        X_resampled, y_resampled = super(SOTENC, self)._fit_resample(
            X_encoded, y)

        # reverse the encoding of the categorical features
        X_res_cat = X_resampled[:, self.continuous_features_.size:]
        X_res_cat.data = np.ones_like(X_res_cat.data)
        X_res_cat_dec = self.ohe_.inverse_transform(X_res_cat)

        if sparse.issparse(X):
            X_resampled = sparse.hstack(
                (X_resampled[:, :self.continuous_features_.size],
                 X_res_cat_dec), format='csr'
            )
        else:
            X_resampled = np.hstack(
                (X_resampled[:, :self.continuous_features_.size].toarray(),
                 X_res_cat_dec)
            )

        indices_reordered = np.argsort(
            np.hstack((self.continuous_features_, self.categorical_features_))
        )
        if sparse.issparse(X_resampled):
            # the matrix is supposed to be in the CSR format after the stacking
            col_indices = X_resampled.indices.copy()
            for idx, col_idx in enumerate(indices_reordered):
                mask = X_resampled.indices == col_idx
                col_indices[mask] = idx
            X_resampled.indices = col_indices
        else:
            X_resampled = X_resampled[:, indices_reordered]

        return X_resampled, y_resampled

    def _generate_sample(self, X, nn_data, nn_num, row, col, step):
        """Generate a synthetic sample with an additional steps for the
        categorical features.
        Each new sample is generated the same way than in SMOTE. However, the
        categorical features are mapped to the most frequent nearest neighbors
        of the majority class.
        """
        rng = check_random_state(self.random_state)
        sample = super(SOTENC, self)._generate_sample(X, nn_data, nn_num,
                                                      row, col, step)
        # To avoid conversion and since there is only few samples used, we
        # convert those samples to dense array.
        sample = (sample.toarray().squeeze()
                  if sparse.issparse(sample) else sample)
        all_neighbors = nn_data[nn_num[row]]
        all_neighbors = (all_neighbors.toarray()
                         if sparse.issparse(all_neighbors) else all_neighbors)

        categories_size = ([self.continuous_features_.size] +
                           [cat.size for cat in self.ohe_.categories_])

        for start_idx, end_idx in zip(np.cumsum(categories_size)[:-1],
                                      np.cumsum(categories_size)[1:]):
            col_max = all_neighbors[:, start_idx:end_idx].sum(axis=0)
            # tie breaking argmax
            col_sel = rng.choice(np.flatnonzero(
                np.isclose(col_max, col_max.max())))
            sample[start_idx:end_idx] = 0
            sample[start_idx + col_sel] = 1

        return sparse.csr_matrix(sample) if sparse.issparse(X) else sample
