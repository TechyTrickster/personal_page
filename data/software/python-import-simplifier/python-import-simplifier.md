---
title: Python Import Simplifier
summary: a handy import code block for all your projects
created-on: 01/04/2024 01:04PM CDT
last-modified: 09/06/2024 04:39PM CDT
author: Andrew Phifer
link: NA
folder: software
---


----

Large python projects can often be difficult to deal with for a number of reasons.  One of them is the way the language handles importing custom source code files.  Typically, a python source code file can only import other source code files from deeper into the folder / project hierarchy.  If you want to import something from higher up, things get tricky.  Thats where this neat little code block comes in.  


````python
import os, sys
from functools import reduce
from pathlib import Path

projectName = "personal_page"
originalDir = os.getcwd()
scriptPath = Path(__file__)
scriptDir = scriptPath.parent
moveUpDegrees = lambda originalPath, amount : reduce(lambda x, y : x.parent, range(0, amount), originalPath)
potentials = list(map(lambda x : moveUpDegrees(scriptPath, x), range(0, len(scriptPath.parts))))
rootDir: Path = list(filter(lambda x : x.name == projectName, potentials))[-1] #should always grab the shortest possible, and therefore most likely to be actual root path, even if the root directory name was reused.
sys.path.append(str(rootDir))
sys.path = sorted(list(set(sys.path)))
````

I've been adding it near the top of all my projects for quite some time, now.  What it does is fairly simple; it addes the project root folder to your system path variable.  It knows what your project root folder name is by you telling it what it is in the 'projectName' variable.  No matter where your python source file is in your project folder structure, this code block will always find the project root directory.  It also saves that path to a handy 'rootDir' variable, available to the rest of your code.  Finally, it will clean up your path variable and remove any duplicate entries, which is absolutely necessary when you're running this little block over and over from multiple different source files. 

As a result of this script, you get to have nice uniform imports of any script in your code base, no matter where you are.  