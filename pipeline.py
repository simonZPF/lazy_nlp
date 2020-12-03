from course import *
from typing import List
import hanlp

CourseList = List[Course]


class BasePipeline(object):
    def __init__(self, course_list: CourseList):
        self.pipeline = hanlp.pipeline()
        self.course_list = course_list
        self.pipeline_init()

    def handle(self, text):
        result = self.pipeline(text)
        return result

    def batch_handle(self, text_list, key=None):
        if not key:
            key = self.course_list[-1].output_key
        result = [self.pipeline(i)[key] for i in text_list]
        return result

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

    def add_pipeline(self, *args, **kwargs):
        self.pipeline.append(*args, **kwargs)
