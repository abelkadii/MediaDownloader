import logging

def setup_logging():
    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Set the logging level

    # Create a console handler and set its level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Set the desired level for console output

    # Create a file handler and set its level
    # file_handler = logging.FileHandler('app.log')
    # file_handler.setLevel(logging.log)  # Set the desired level for file output

    # Create a formatter and set its format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    # file_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(console_handler)
    # logger.addHandler(file_handler)