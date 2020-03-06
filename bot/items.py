def __init__(self):
    pass

class Doc:
    def __init__(self, value, user, description = None, folder = None):
        self.value = value
        self.user = user
        self.description = description
        self.folder = folder


class Link:
    def __init__(self, value, user, description = None, folder = None):
        self.value = value
        self.user = user
        self.description = description
        self.folder = folder