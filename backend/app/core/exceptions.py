class AdPersonalizerError(Exception):
    """Base error for all app errors."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AdAnalysisError(AdPersonalizerError):
    """Raised when Claude Vision fails to analyze the ad image."""
    def __init__(self, message: str = "Failed to analyze ad creative."):
        super().__init__(message, status_code=422)


class PageScrapingError(AdPersonalizerError):
    """Raised when the landing page cannot be fetched or parsed."""
    def __init__(self, message: str = "Failed to scrape the landing page."):
        super().__init__(message, status_code=422)


class PersonalizationError(AdPersonalizerError):
    """Raised when Claude fails to generate personalized copy."""
    def __init__(self, message: str = "Failed to personalize the page."):
        super().__init__(message, status_code=422)


class InvalidURLError(AdPersonalizerError):
    """Raised when a provided URL is invalid or unreachable."""
    def __init__(self, message: str = "The provided URL is invalid or unreachable."):
        super().__init__(message, status_code=400)