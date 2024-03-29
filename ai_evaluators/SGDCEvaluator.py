from sklearn.linear_model import SGDClassifier
from ai_evaluators.IEvaluator import IEvaluator, TRAINING_RANDOM_STATE
from sklearn.metrics import f1_score

import ray
from ray import train, tune


class SGDCEvaluator(IEvaluator):
    def __init__(self):
        super().__init__()
        self.hyperparameters = {
            "alpha": ([1e-5, 1e-4, 1e-3, 1e-2, 1e-1], (1e-4, 1e-1)),
            "eta0": ([1e-5, 1e-4, 1e-3, 1e-2, 1e-1], (1e-4, 1e-1)),
            "power_t": ([-2, -1, 0.5, 1, 2], (-5, 5)),
            "max_iter": ([100, 300, 500, 700, 1000], (100, 1000)),
        }

    def evaluate(self, config):
        clf = SGDClassifier(
            alpha=config['alpha'],
            eta0=config['eta0'],
            power_t=config['power_t'],
            max_iter=int(config["max_iter"]),
            loss="hinge"
        )

        X_train = ray.get(config["X_train_id"])
        X_test = ray.get(config["X_test_id"])
        y_train = ray.get(config["y_train_id"])
        y_test = ray.get(config["y_test_id"])


        clf.fit(X_train, y_train)
        predictions = clf.predict(X_test)
        f1 = f1_score(y_test, predictions, average='micro')

        train.report({"f1_score": f1})