def server_plurality(instances):
    if len(instances) == 1:
        return "server"
    else:
        return "servers"

def is_plurality(instances):
    if len(instances) == 1:
        return "is"
    else:
        return "are"

def it_plurality(instances):
    if len(instances) == 1:
        return "it"
    else:
        return "them"
