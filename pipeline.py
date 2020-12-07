from course import *
from typing import List
import hanlp
from IO import *

CourseList = List[Course]


class BasePipeline(object):
    def __init__(self, course_list: CourseList):
        self.pipeline = hanlp.pipeline()
        self.course_list = course_list
        self.course_dict = {}
        self.result = None

        self.pipeline_init()

    def handle(self, text):
        result = self.pipeline(text)
        return result

    def batch_handle(self, text_list, key=None):
        if not key:
            key = self.course_list[-1].output_key
        if not self.result:
            self.result = [self.pipeline(i) for i in text_list]
        return [i[key] for i in self.result]

    def get_key(self, key):
        if not self.result:
            raise ValueError
        return [i[key] for i in self.result]

    def show_pipeline(self):
        input_key = "original data"
        info = ""
        for i in self.course_list:
            if i.input_key:
                input_key = i.input_key
            info += f"{input_key}: {i.input_type} ==> {i.output_key}: {i.output_type}\n"
            input_key = i.output_key
        print(info)

    def pipeline_init(self):
        for c in self.course_list:
            self.pipeline = self.pipeline.append(c.run, output_key=c.output_key, input_key=c.input_key)
            self.course_dict[c.output_key] = c

    def add_pipeline(self, *args, **kwargs):
        self.pipeline.append(*args, **kwargs)

    def save(self, key, path="data/st.txt"):
        with open(path, "w") as f:
            f.write(format_result(self.get_key(key), self.course_dict[key].seq))

    def statistic(self, key):
        return [self.course_dict[key].statistic_info(i) for i in self.get_key(key)]
