class SaveMiddleFile(object):
    def __init__(self, data: iter, seq: list, path: str):
        self.seq = seq
        self.data = data
        self.path = path

    def save(self):
        seq_len = len(self.seq)
        if seq_len == 1:
            string = self.seq[0].join(self.data)
        elif seq_len == 2:
            string = self.seq[0].join([self.seq[1].join(i) for i in self.data])
        else:
            string = self.seq[0].join([self.seq[1].join([self.seq[2].join(i) for i in j]) for j in self.data])
        return string
