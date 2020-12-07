from constant import *
import pandas as pd
from typing import Any
import re
import html
import urllib
import w3lib.html
from opencc import OpenCC
from functools import reduce
import jieba


class Course(object):
    debug_flag = False
    output_key = "base course"
    input_key = []
    input_type = "Any"
    output_type = "Any"
    seq = ["\n"]

    def __init__(self, function=None):
        if function:
            self.run = function

    def run(self, *args, **kwargs):
        pass

    def debug_print(self, *args, **kwargs):
        if self.debug_flag:
            print(*args, **kwargs)

    def statistic_info(self, data):
        return len(data)


class CleanText(Course):
    PUNC = r"[↓：\|丨，\_《》、；‘’＂“”【「】」·@￥（）—\,\<\.\>\/\;\:\'\"\[\]\{\}\~\`\@\#\$\%\^\&\*\(\)\-\=\+]"
    output_key = "clean text"
    input_type = "string"
    output_type = "string"
    seq = ["\n***$$$&^&$$***\n"]

    def run(self, text: str, remove_url=True, email=True, weibo_at=True,
            emoji=True, weibo_topic=False, norm_url=False, norm_html=False,
            to_url=False, remove_puncts=True, remove_tags=True, t2s=False,
            remove_blank=True) -> str:
        """ 进行各种文本清洗操作，微博中的特殊格式，网址，email，html代码，等等
        :param remove_blank: 去除空行
        :param text: 输入文本
        :param remove_url: （默认使用）是否去除网址
        :param email: （默认使用）是否去除email
        :param weibo_at: （默认使用）是否去除微博的\@相关文本
        :param emoji: （默认使用）去除\[\]包围的文本，一般是表情符号
        :param weibo_topic: （默认不使用）去除##包围的文本，一般是微博话题
        :param norm_url: （默认不使用）还原URL中的特殊字符为普通格式，如(%20转为空格)
        :param norm_html: （默认不使用）还原HTML中的特殊字符为普通格式，如(\&nbsp;转为空格)
        :param to_url: （默认不使用）将普通格式的字符转为还原URL中的特殊字符，用于请求，如(空格转为%20)
        :param remove_puncts: （默认不使用）移除所有标点符号
        :param remove_tags: （默认使用）移除所有html块
        :param t2s: （默认不使用）繁体字转中文
        :return: 清洗后的文本"""

        # 反向的矛盾设置
        if norm_url and to_url:
            raise Exception("norm_url和to_url是矛盾的设置")
        if norm_html:
            text = html.unescape(text)
        if to_url:
            text = urllib.parse.quote(text)
        if remove_tags:
            text = w3lib.html.remove_tags(text)
        if remove_url:
            URL_REGEX = re.compile(
                r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]'
                r'+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))',
                re.IGNORECASE)
            text = re.sub(URL_REGEX, "", text)
        if norm_url:
            text = urllib.parse.unquote(text)
        if email:
            EMAIL_REGEX = re.compile(r"[-a-z0-9_.]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}", re.IGNORECASE)
            text = re.sub(EMAIL_REGEX, "", text)
        if weibo_at:
            text = re.sub(r"(回复)?(//)?\s*@\S*?\s*(:|：| |$)", " ", text)  # 去除正文中的@和回复/转发中的用户名
        if emoji:
            text = re.sub(r"\[\S+\]", "", text)  # 去除表情符号
        if weibo_topic:
            text = re.sub(r"#\S+#", "", text)  # 去除话题内容
        if t2s:
            cc = OpenCC('t2s')
            text = cc.convert(text)
        if remove_puncts:
            allpuncs = re.compile(self.PUNC)
            text = re.sub(allpuncs, "", text)
        if remove_blank:
            lines = text.split('\n')
            l = []
            for i in lines:
                t = re.sub(r"\s+", "", i)
                if t:
                    l.append(t)
            text = "\n".join(l)
        return text.strip()


class CutClause(Course):
    cut_punc = '。！？!?…\n'
    output_key = "clauses"
    input_type = "string"
    output_type = "StrVector"
    seq = ["\n\n", "\n"]

    def run(self, paragraph: str, main_part: StrVector = None, interference: StrVector = None) -> StrVector:
        # 分句
        split_list = re.split('([' + self.cut_punc + '])', paragraph)
        # r = map(lambda x, y: x + y, split_list[::2], split_list[1::2] + [""])
        r = [i for i in split_list[::2] if i]
        res_list = r
        if main_part:
            for i in r:
                for j in main_part:
                    if j in i:
                        res_list.append(i)
                        break
        if interference:
            inter_list = []
            for i in res_list:
                for j in interference:
                    if j in i:
                        break
                else:
                    inter_list.append(i)
            res_list = inter_list
        return list(res_list)


class Tokenizer(Course):
    output_key = "tokens"
    input_type = "StrVector"
    output_type = "StrVector_2"
    seq = ["\n\n", "\n", " "]

    def run(self, sentence_list: StrVector) -> StrVector_2:
        return [jieba.lcut(sentence) for sentence in sentence_list]

    def statistic_info(self, data):
        return sum(map(len, data))



class HandleToken(Course):
    output_key = "clean tokens"
    input_type = "StrVector_2"
    output_type = "StrVector_2"
    seq = ["\n\n", "\n", " "]

    def __init__(self):
        super().__init__()
        self.stopwords = {'责任编辑', '小结'}

    def is_number(self, s) -> bool:
        try:
            float(s)
            return True
        except ValueError:
            pass
        return False

    def run(self, tokens_list: StrVector_2) -> StrVector_2:
        r_list = []
        for tokens in tokens_list:
            t_list = []
            for token in tokens:
                if token in self.stopwords:
                    continue
                # if self.is_number(token):
                #     token = '<num>'
                t_list.append(token)
            if t_list:
                r_list.append(t_list)
        return r_list

    def statistic_info(self, data):
        return sum(map(len, data))
