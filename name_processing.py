'''Process names'''

def variant_to_root(var):
    """
    Transforms a variant of a character name to its root.
    """
    var = var.lower()
    var = var.split(' (', 1)[0]  # e.g. willy (v.o.) --> willy
    var = var.strip(':')  # carol: --> carol
    var = var.replace('. ', ' ')  # mr. wang --> mr wang

    # handle voice-overs
    if '\'s voice' in var:  # e.g. cate's voice --> cate
        var = var.split('\'s', 1)[0]
    elif 's\' voice' in var or 'z\' voice' in var:  # e.g. chris' voice --> chris
        var = var.split('\'', 1)[0]
    elif ' voice' in var or ' voice over' in var or ' voice-over' in var:
        var = var.split(' voice', 1)[0]

    return var
