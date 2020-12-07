from pipeline import BasePipeline
from course import *
from IO import *


def read_data():
    data = pd.read_csv('data/train_data.csv', nrows=20)
    x = data['内容']
    return x


clean_text = CleanText()
sentence_split = CutClause()
tokenizer = Tokenizer()
handle_tokens = HandleToken()
x = read_data()
pre = BasePipeline([clean_text, sentence_split, tokenizer, handle_tokens])
result = pre.batch_handle(x)
print(pre.statistic("clean tokens"))
# pre.save("clean tokens")
# print(load_from_middle(handle_tokens.seq, "data/st.txt")[0])
