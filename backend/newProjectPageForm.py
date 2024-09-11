import os, sys
from pathlib import Path
from functools import reduce
from multiprocessing import Process
from wtforms import Form, StringField, validators, TextAreaField
from flask_wtf import FlaskForm

projectName = "personal_page"
originalDir = os.getcwd()
scriptPath = Path(__file__)
scriptDir = scriptPath.parent
moveUpDegrees = lambda originalPath, amount : reduce(lambda x, y : x.parent, range(0, amount), originalPath)
potentials = list(map(lambda x : moveUpDegrees(scriptPath, x), range(0, len(scriptPath.parts))))
rootDir: Path = list(filter(lambda x : x.name == projectName, potentials))[-1] #should always grab the shortest possible, and therefore most likely to be actual root path, even if the root directory name was reused.
sys.path.append(str(rootDir))
sys.path = sorted(list(set(sys.path)))
initial = str(Process.pid)



class NewProjectPage(FlaskForm):
    title = StringField('project title', validators = [validators.Length(min = 5, max = 64)])
    summary = StringField('project summary', validators = [validators.Length(min = 10, max = 128)])
    body = TextAreaField('project body', validators = [validators.Length(min = 10, max = 16000)])
    sourceCodeLink = StringField('source code URL', validators = [validators.URL(), validators.Length(min = 5, max = 512)])