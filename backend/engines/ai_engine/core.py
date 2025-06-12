import logging
from .exceptions import AIEngineError

logger = logging.getLogger("ai_engine")

class AIModel:
    def __init__(self, model=None):
        self.model = model

    def train(self, X, y):
        if not self.model:
            logger.error("Model not initialized")
            raise AIEngineError("No model initialized!")
        self.model.fit(X, y)
        logger.info("AI model trained.")

    def predict(self, X):
        if not self.model:
            logger.error("Model not initialized for predict")
            raise AIEngineError("No model initialized!")
        logger.debug("Prediction started.")
        return self.model.predict(X)
