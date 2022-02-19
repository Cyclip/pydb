from hashlib import sha512
import warnings

from exceptions import *

def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
    return '%s:%s: %s: %s\n' % (filename, lineno, category.__name__, message)

warnings.formatwarning = warning_on_one_line

def hashPw(pw):
    """Hash a password

    Args:
        pw (str): Password

    Returns:
        str: Hashed pw
    """
    if not isinstance(pw, str):
        raise TypeError("Password must be a string")

    for i in range(500):
        pw = sha512(pw.encode()).hexdigest()
    
    return pw


def getCreds():
    try:
        with open(".creds", "r") as f:
            content = f.read().replace("\r", "").split("\n")
            
            if content == DEFAULT_CREDS:
                warnings.warn("using default credentials.\nUsername: admin\nPassword: changeme")
    except FileNotFoundError:
        warnings.warn(".creds file does not exist, using default creds")

        with open(".creds", "w") as f:
            f.write("\n".join(DEFAULT_CREDS))
        
        return getCreds()

    if len(content) != 2:
        raise BadFormat(".creds must have 2 lines")
    
    return content


DEFAULT_CREDS = ["admin", hashPw("changeme")]