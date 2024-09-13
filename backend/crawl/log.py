import logging
import traceback

# Configure logging
logging.basicConfig(
    filename='crawler.log',  # Log file name
    level=logging.DEBUG,  # Log level
    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s'
)

# Example function to log errors
def log_error(package_name, package_version, error_message):
    logging.error(
        "Package: %s, Version: %s - Error: %s",
        package_name,
        package_version,
        error_message
    )

# Example function to log exceptions
def log_exception(package_name, package_version, exception):
    logging.critical(
        "Package: %s, Version: %s - Exception: %s\nTraceback:\n%s",
        package_name,
        package_version,
        str(exception),
        traceback.format_exc()
    )

# Example usage
# try:
#     # Simulate package processing
#     package_name = "example_package"
#     package_version = "1.0.0"
#     raise ValueError("Simulated error")
# except Exception as e:
#     log_exception(package_name, package_version, e)
