from abc import ABC, abstractmethod
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

class BaseAnalyzer(ABC):
    def __init__(self, data_collector):
        self.collector = data_collector
        self.model = None
    
    @abstractmethod
    def prepare_features(self) -> pd.DataFrame:
        """Prepare features for model training"""
        pass
        
    @abstractmethod
    def prepare_targets(self) -> pd.Series:
        """Prepare target variables for model training"""
        pass
        
    def train_model(self, test_size=0.2):
        """Train the prediction model"""
        X = self.prepare_features()
        y = self.prepare_targets()
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        self.model.fit(X_train, y_train)
        predictions = self.model.predict(X_test)
        
        return accuracy_score(y_test, predictions) 