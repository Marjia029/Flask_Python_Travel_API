import warnings

def pytest_configure(config):
    warnings.filterwarnings(
        "ignore", 
        category=DeprecationWarning, 
        module="flask_restx.api"
    )