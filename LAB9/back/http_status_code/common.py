def format(status_code, string):
    return (status_code[0].replace("ok", string), *status_code[1:])