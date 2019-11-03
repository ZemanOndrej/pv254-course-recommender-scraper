import os
import json
from pathlib import Path


def saveJson(json_output, filename='courses.json'):
    file_dir = Path(filename).parent.absolute()
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    with open(filename, 'w+', encoding="utf-8") as f:
        json.dump(json_output, f,indent=4)


def get_subject_urls(subject):
    with open(f'courses/urls/{subject}_courses.json') as f:
        return json.load(f)


def get_course_id(url):
    course_url = url.split('/')
    return course_url[len(course_url)-1]



