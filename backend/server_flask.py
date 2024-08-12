import html
import re
import os, sys, sqlite3, socket
from bs4 import BeautifulSoup
from functools import reduce
from pathlib import Path
from flask import Flask, Response, render_template, send_file, render_template_string
from markdown import markdown, Markdown


projectName = "personal_page"
originalDir = os.getcwd()
scriptPath = Path(__file__)
scriptDir = scriptPath.parent
moveUpDegrees = lambda originalPath, amount : reduce(lambda x, y : x.parent, range(0, amount), originalPath)
potentials = list(map(lambda x : moveUpDegrees(scriptPath, x), range(0, len(scriptPath.parts))))
rootDir: Path = list(filter(lambda x : x.name == projectName, potentials))[-1] #should always grab the shortest possible, and therefore most likely to be actual root path, even if the root directory name was reused.
sys.path.append(str(rootDir))
sys.path = sorted(list(set(sys.path)))




class Portfolio:
    """
    a project based portfolio website template built using flask.  
    the site is composed of the following pages
    1. home - an introductory page
    2. project time line - a graphical page showing the overlap of all of your projects on a stacked timeline.  generated dynmically from meta data
    3. resume - a dedicated page for your resume for potential employers
    4. your project pages - one page for each of your different projects. should be loaded as a pdf

    all page body content is constructed entirely with md files which are loaded in and converted to html to be injected
    into templates with the 'start' function.  
    """
    
    def __init__(self):
        """initializes your site, but does not loadthe md documents from disk or start the flask server"""
        self.dataFolder = rootDir / 'data'        
        self.databasePath = self.dataFolder / 'porfolio.db'
        self.databaseConstructor = self.dataFolder / 'dbDefinition.sql'
        self.templatePath = rootDir / 'frontend'
        self.mappingTable = {}
        self.pageTitles = []
        self.pageLinks = []        
        self.numberOfProjects = 0
        self.mimeTable = {
            '.png': 'image/png',
            '.ico': 'image/vnd.microsoft.icon',
            '.jpg': 'image/jpg',
            '.webp': 'image/webp',
            '.svg': 'image/svg+xml',
            '.js': 'application/json',
            '.pdf': 'application/pdf',
            '.sh': 'application/x-sh',
            '.xml': 'application/xml',
            '.7z': 'application/x-7z-compressed',
            '.zip': 'application/zip',
            '.html': 'text/html',
            '.css': 'text/css'
        }

        self.app = Flask(__name__, template_folder = self.templatePath)
        self.app.add_url_rule("/home", view_func = self.getHomePage)
        self.app.add_url_rule("/frontend/<path:name>", view_func = self.getFile)
        self.app.add_url_rule("/projects/<name>", view_func = self.getProjectPage)
        self.connection = sqlite3.connect(":memory:", check_same_thread = False) #use file once change detection has been implemented
        self.cursor = self.connection.cursor()        


    @staticmethod
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
    

    @staticmethod
    def loadTextFile(filePath: Path) -> str:        
        handle = open(filePath, "r")
        output = handle.read()
        handle.close()
        return output

        
    def getFile(self, name: str) -> Response:        
        pathToFile = self.templatePath / name
        print(f"getting file: {pathToFile}")
        mimeType = self.mimeTable[pathToFile.suffix]
        return send_file(pathToFile, mimetype = mimeType)


    def getHomePage(self) -> str:
        homePagePath = self.mappingTable["homePage.html"]
        data = Portfolio.loadTextFile(homePagePath)
        output = render_template_string(data, projectLinks = self.pageLinks, projectNames = self.pageTitles, title = "Home", len = self.numberOfProjects)
        return output
    

    def getProjectTimeLine(self) -> str:
        projectTimeLinePath = self.mappingTable["projectTimeLine.html"]
        output = render_template(projectTimeLinePath)
        return output


    #TODO: generate formatted dates
    def getProjectPage(self, name: str) -> str:
        print(name)
        projectPagePath = self.mappingTable["projectPage.html"]
        pageData = Portfolio.loadTextFile(projectPagePath)
        print(pageData)
        pageBuffer = self.cursor.execute(f"select * from articles where pageName = '{name}';")        
        data = pageBuffer.fetchone()                
        print(data)
        output = render_template_string(pageData, projectNames = self.pageTitles, projectLinks = self.pageLinks, 
                                        title = data[1], createdOn = data[2], modifiedOn = data[3], 
                                        bodyText = html.unescape(data[4]), sourceCodeLink = data[5], len = self.numberOfProjects)
        return output


    @staticmethod
    def extractTaggedText(inputBody: list[str], tagName: str) -> str:        
        tagValue = f"{{#{tagName}}}"
        buffer = list(filter(lambda x : tagValue in x, inputBody))[0]
        output = buffer.replace(tagValue, "").replace("#", "").strip()
        return output
    
    
    @staticmethod
    def removeTagFromText(inputBody: list[str], tagName: str) -> list[str]:        
        tagValue = f"{{#{tagName}}}"
        output = list(filter(lambda x : tagValue not in x, inputBody))
        return output
    

    def getProjectPages(self):
        projectLinksBuffer = self.cursor.execute("select title, pageName from articles")        
        projectLinks = projectLinksBuffer.fetchall()
        self.pageTitles = list(map(lambda x : x[0], projectLinks))
        self.pageLinks = list(map(lambda x : f"/projects/{x[1]}", projectLinks))        


    def removePreviewMaterials(data: str) -> str:
        lines = data.split('\n')
        hasPreviewTitle = any(list(map(lambda x : "#Title" in x, lines)))
        hasPreviewLink = any(list(map(lambda x : "#Link" in x, lines)))
        buffer0 = Portfolio.removeTagFromText(lines, "Title") if hasPreviewTitle else lines
        buffer1 = Portfolio.removeTagFromText(buffer0, "Link") if hasPreviewLink else buffer0
        output = reduce(lambda x , y : x + '\n' + y, buffer1)
        return output

    @staticmethod
    def modifyImgTag(imgTag):
        print("mod")
        imgTag['class'] = imgTag.get('class', []) + ['img-fluid']


    def generateDBEntries(self):               
        print("loading db contents") 

        for element in self.articlePaths:
            pageName = element.stem            
            createdOn = int(os.path.getctime(element))
            modifiedOn = int(os.path.getmtime(element))
            raw0 = Portfolio.loadTextFile(element)                        
            raw1 = Portfolio.removePreviewMaterials(raw0)
            converter = Markdown(extensions = ['extra', 'markdown_mark', 'markdown_checklist.extension', 'sane_lists', 'pymdownx.tilde', 'codehilite', 'meta'])
            bodyBuffer = converter.convert(raw1)
            metaData = converter.Meta
            title = metaData['title'][0]
            codeLink = metaData['link'][0]
            print(title, codeLink)
            doc = BeautifulSoup(bodyBuffer, features = 'html.parser')
            imageTags = doc.find_all('img')            
            list(map(lambda x : Portfolio.modifyImgTag(x), imageTags))
            bodyBuffer2 = doc.prettify()
            body = html.escape(bodyBuffer2)

            insertStatement = "insert into articles values (?, ?, ?, ?, ?, ?)"            
            self.cursor.execute(insertStatement, (pageName, title, createdOn, modifiedOn, body, codeLink))

        self.connection.commit()


    def constructDB(self):
        handle = open(self.databaseConstructor, "r")
        scriptText = handle.read()
        self.cursor.executescript(scriptText)
        self.connection.commit()
        handle.close()


    def start(self):
        self.files = Portfolio.findFiles(rootDir / 'frontend')
        self.files.extend(Portfolio.findFiles(rootDir / 'data'))
        print(self.files)
        self.articlePaths = list(filter(lambda x : (str(self.dataFolder) in str(x)) and (x.suffix == ".md"), self.files))
        print(self.articlePaths)
        list(map(lambda x : self.mappingTable.update({x.stem : x}), self.files))
        list(map(lambda x : self.mappingTable.update({x.name : x}), self.files))
        print(self.mappingTable)
        self.constructDB()
        self.generateDBEntries()
        self.getProjectPages()
        self.numberOfProjects = len(self.pageLinks)
        self.app.run(debug = True, host = socket.gethostbyname(socket.gethostname()))




if __name__ == "__main__":
    instance = Portfolio()
    instance.start()