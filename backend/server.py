import os, sys
from functools import reduce
from pathlib import Path
from fastapi import FastAPI
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

homePagePath = rootDir / 'frontend' / 'index.html'
styleSheetPath = rootDir / 'frontend' / 'styles.css'
faviconPath = rootDir / 'frontend' / 'favicon.ico'
app = FastAPI(debug = True)


@app.get("/frontend/index.html", response_class = HTMLResponse)
async def getHome():
    fileHandle = open(homePagePath, "r")
    data = fileHandle.read()
    return data


@app.get("/frontend/styles.css", response_class = FileResponse)
async def getStyleSheet():
    return styleSheetPath


@app.get("/frontend/favicon.ico", response_class = FileResponse)
async def getFavicon():
    print("get favicon")
    return faviconPath