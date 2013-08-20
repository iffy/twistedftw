
def _u(txt):
    """
    Encode unicode and leave strings alone
    """
    if type(txt) == unicode:
        return txt.encode('utf-8')
    return txt


def enter(who):
    return {'event': 'enter', 'who': _u(who)}


def leave(who):
    return {'event': 'leave', 'who': _u(who)}


def kick(who):
    return {'event': 'kick', 'who': _u(who)}


def msg(message, who):
    return {'event': 'msg', 'msg': _u(message), 'who': _u(who)}
