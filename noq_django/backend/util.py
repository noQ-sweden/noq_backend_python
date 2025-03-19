import logging
from datetime import datetime


# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def format_request(request):
    msg = ""
    if request.method == "POST":
        request = request.POST
        msg = msg + "POST "
        for var in request:
            if not "csrf" in var.lower():
                msg = msg + var + ";"
    else:
        request = request.GET
        msg = msg + "GET "
        for var in request:
            if not "csrf" in var.lower():
                msg = msg + var + ";"

    return msg


def debug(*args):
    ret = ""
    datum = datetime.now().strftime("%H:%M:%S ")
    for arg in args:
        if "Request" in str(type(arg)):
            ret = "\n" + datum + ret + format_request(arg)
        elif ret == "":
            ret = datum
        if str(arg).endswith("="):
            ret = ret + f"{arg}"    
        else:
            ret = ret + f"{arg} | "
    logger.debug(ret)
