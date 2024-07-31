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

mappingTable = {
    'index.html': rootDir / 'frontend' / 'index.html',
    'styles.css': rootDir / 'frontend' / 'styles.css',
    'favicon.ico': rootDir / 'frontend' / 'favicon.ico',
    'nwsTerminalApp.html': rootDir / 'frontend' / 'personal' /'weather-terminal' / 'nwsTerminalApp.html',
    'weather-terminal-screen-shot.jpg': rootDir / 'frontend' / 'personal' /'weather-terminal' / 'weather-terminal-screen-shot.jpg',
    'frontpage-background.webp': rootDir / 'frontend' / 'frontpage-background.webp'
}
app = FastAPI(debug = True)


@app.get("/frontend/{pageName}", response_class = FileResponse)
async def getPage(pageName):
    filePath = mappingTable[pageName]    
    return filePath


@app.get("/{pageName}", response_class = FileResponse)
async def getPage(pageName):
    filePath = mappingTable[pageName]    
    return filePath