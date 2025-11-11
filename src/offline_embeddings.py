"""
Offline embeddings implementation using TF-IDF.

This module provides a fallback embedding solution that works completely offline
when external API calls fail due to network/SSL issues.
"""

import numpy as np
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from langchain.embeddings.base import Embeddings


class OfflineTfidfEmbeddings(Embeddings):
    """
    Offline embeddings using TF-IDF vectorization.

    This class provides a fallback when external embedding APIs are unavailable
    due to SSL/network issues. It uses scikit-learn's TfidfVectorizer to create
    document embeddings locally without any external dependencies.
    """

    def __init__(self, max_features: int = 1000):
        """
        Initialize the TF-IDF embeddings.

        Args:
            max_features: Maximum number of features for TF-IDF
        """
        self.max_features = max_features
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=(1, 2),  # unigrams and bigrams
            min_df=1,
            max_df=0.95,
            stop_words='english'
        )
        self.is_fitted = False
        self._all_texts = []

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of documents.

        Args:
            texts: List of documents to embed

        Returns:
            List of embeddings (each embedding is a list of floats)
        """
        # Store all texts for fitting if not already fitted
        if not self.is_fitted:
            self._all_texts.extend(texts)
            # Fit the vectorizer on all texts seen so far
            self.vectorizer.fit(self._all_texts)
            self.is_fitted = True

        # Transform the texts to TF-IDF vectors
        tfidf_matrix = self.vectorizer.transform(texts)

        # Convert sparse matrix to dense and then to list of lists
        embeddings = tfidf_matrix.toarray().tolist()

        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query.

        Args:
            text: Query text to embed

        Returns:
            Embedding as a list of floats
        """
        if not self.is_fitted:
            # If not fitted yet, fit on the query itself
            self.vectorizer.fit([text])
            self.is_fitted = True

        # Transform the query to TF-IDF vector
        tfidf_vector = self.vectorizer.transform([text])

        # Convert to dense and return as list
        return tfidf_vector.toarray()[0].tolist()
