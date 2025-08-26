class KafkaProducerError(Exception):
    """Custom exception for Kafka producer related errors"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
class KafkaProducerError(Exception):
    """Custom exception for Kafka producer related errors"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
