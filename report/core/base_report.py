

class BaseReport:

    def run(self, *args, **kwargs):
        raise NotImplementedError()

    def write_document(self, *args, **kwargs):
        raise NotImplementedError()
