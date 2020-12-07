def format_result(data, seq):
    if len(seq) == 1:
        return seq[0].join(data)
    else:
        return seq[0].join([format_result(i, seq[1:]) for i in data])


def foo(data, seq):
    if len(seq) == 1:
        return data.split(seq[0])
    else:
        return [foo(i, seq[1:]) for i in data.split(seq[0])]


def load_from_middle(seq, path):
    with open(path, "r") as f:
        string = "".join([i for i in f.readlines()])
    return foo(string, seq)
