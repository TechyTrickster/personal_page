import os, sys
from functools import reduce
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse


projectName = "personal_page"
originalDir = os.getcwd()
scriptPath = Path(__file__)
scriptDir = scriptPath.parent
moveUpDegrees = lambda originalPath, amount : reduce(lambda x, y : x.parent, range(0, amount), originalPath)
potentials = list(map(lambda x : moveUpDegrees(scriptPath, x), range(0, len(scriptPath.parts))))
rootDir = list(filter(lambda x : x.name == projectName, potentials))[-1] #should always grab the shortest possible, and therefore most likely to be actual root path, even if the root directory name was reused.
sys.path.append(str(rootDir))
sys.path = sorted(list(set(sys.path)))


def findFiles(dir: Path) -> list[Path]:
    """
    small function to recursively search a given folder to list out all of the contained
    files.

    Parameters:
    dir (Path) : path to start the search in

    Returns:
    (list[Path]) : the list of paths of all of the files under the input directory
    """
    output = []
    dirs = list(os.walk(dir))
    for element in dirs:
        if (".git" not in str(element)) and ("venv_page" not in str(element)):
            data = list(map(lambda x : Path(element[0]) / x, element[2]))
            output.extend(data)

    return output

mappingTable = {}
files = findFiles(rootDir / 'frontend')
list(map(lambda x : mappingTable.update({x.name : x}), files))
print(mappingTable)

app = FastAPI(debug = True)


@app.get("/frontend/{pageName}", response_class = FileResponse)
async def getPage(pageName):
    filePath = mappingTable[pageName]    
    return filePath


@app.get("/{pageName}", response_class = FileResponse)
async def getPage(pageName):
    filePath = mappingTable[pageName]    
    return filePath


