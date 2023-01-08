import json
import time

import joblib
import numpy as np
import pandas as pd
from base_trainer import BaseTrainer
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


class Trainer(BaseTrainer):
    def __init__(self):
        super().__init__()
        self.model_name = "random_forest"

    def execute(self):
        self.load_database()
        self.split_database()
        self.set_encoder()
        self.set_model()
        self.train_model()
        self.generate_metadata()
        self.save_model()
        self.save_metadata()

    def load_database(self):
        path = f"{self.ML_DIR}/{self.DATAFILE}"
        df = pd.read_csv(path)
        df["diff_h_a"] = df.GF - df.GA
        self.database = df

    def split_database(self):
        self.features = self.database.drop(columns=self.not_usefull_columns)
        self.target = self.database[self.target_name]

    def set_encoder(self):
        categorical_preprocessor = OneHotEncoder(handle_unknown="ignore")
        numerical_preprocessor = StandardScaler()

        self.encoder = ColumnTransformer(
            [
                (
                    "one-hot-encoder",
                    categorical_preprocessor,
                    self.categoric_columns,
                ),
                (
                    "standard_scaler",
                    numerical_preprocessor,
                    self.numeric_columns,
                ),
            ]
        )

    def set_model(self):
        self.regressor = RandomForestRegressor(
            n_estimators=150, random_state=42
        )
        self.model = make_pipeline(self.encoder, self.regressor)

    def train_model(self):
        self.model.fit(self.features, self.target)

    def generate_metadata(self):
        features_importance = dict()
        importances = self.regressor.feature_importances_
        for value, var in zip(importances, list(self.features)):
            features_importance[var] = value
        self.metadata = {
            "model": self.model_name,
            "features_importance": features_importance,
            "updated_at": time.time(),
        }

    def save_model(self):
        path = f"{self.ML_DIR}/trained_model.pkl"
        joblib.dump(self.model, path, compress=3)

    def save_metadata(self):
        path = f"{self.ML_DIR}/model_metadata.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    trainer = Trainer()
    trainer.execute()
    print(trainer.metadata)
