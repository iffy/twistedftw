

def enter(who):
    return {'event': 'enter', 'who': who}


def leave(who):
    return {'event': 'leave', 'who': who}


def kick(who):
    return {'event': 'kick', 'who': who}


def msg(message, who):
    return {'event': 'msg', 'msg': message, 'who': who}
