import logging
from logging import handlers

def pull_events_basic_logging():
    basic_formatter = logging.Formatter(fmt="-- %(levelname)s:%(asctime)s:%(name)s --\n%(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    #smtp_handler = logging.handlers.SMTPHandler(mailhost=("smtp.example.com", 25),
    #                                            fromaddr="from@example.com",
    #                                            toaddrs="to@example.com",
    #                                            subject=u"AppName error!")
    smtp_handler = handlers.RotatingFileHandler(filename="../../log/errors.log")
    smtp_handler.setFormatter(basic_formatter)
    smtp_handler.setLevel(logging.ERROR)

    file_handler = handlers.RotatingFileHandler(filename="../../log/aggregator.log")
    file_handler.setFormatter(basic_formatter)
    file_handler.setLevel(logging.INFO)

    logging.root.addHandler(smtp_handler)
    logging.root.addHandler(file_handler)
