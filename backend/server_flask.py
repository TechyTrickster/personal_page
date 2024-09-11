import html
import random
import os, sys, sqlite3, socket
import time
from bs4 import BeautifulSoup
from functools import reduce
from pathlib import Path
from flask import Flask, Response, redirect, render_template, send_file, render_template_string, request
from markdown import  Markdown
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
from multiprocessing import Process

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

from backend.newProjectPageForm import NewProjectPage

#TODO: add caching of pages
#TODO: add auto-update of pages with md or image files are updated
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
        self.linkData = []
        self.numberOfProjects = 0
        self.mimeTable = {
            '.png': 'image/png',
            '.ico': 'image/vnd.microsoft.icon',
            '.jpg': 'image/jpg',
            '.webp': 'image/webp',
            '.svg': 'image/svg+xml',
            '.js': 'text/javascript',
            '.pdf': 'application/pdf',
            '.sh': 'application/x-sh',
            '.xml': 'application/xml',
            '.7z': 'application/x-7z-compressed',
            '.zip': 'application/zip',
            '.html': 'text/html',
            '.css': 'text/css'
        }

        #TODO: load this list dynamically
        self.cardColorList = [
            'vapor-green',
            'vapor-blue',
            'vapor-purple',
            'vapor-red',
            'vapor-yellow'
        ]        

        self.connection = None
        self.cursor = None
        self.insertStatement = "insert into articles values (?, ?, ?, ?, ?, ?, ?, ?)"
        self.app = Flask(__name__, template_folder = self.templatePath)
        self.app.config['SECRET_KEY'] = os.urandom(32)
        self.app.config['WTF_CSRF_SECRET_KEY'] = os.urandom(32)
        self.app.add_url_rule("/<name>", view_func = self.getCorePage)
        # self.app.add_url_rule("/<name>", view_func = self.getDirectoryPage)
        # self.app.add_url_rule("/<name>", view_func = self.getLoginPage)
        self.app.add_url_rule("/create-new-project", view_func = self.getNewProjectPage)
        self.app.add_url_rule("/favicon.ico", view_func = self.getFront)
        self.app.add_url_rule("/newPageSubmit", methods = ['GET', 'POST'], view_func = self.addPage)
        # self.app.add_url_rule("/<name>", view_func = self.getProjectsTimeLinePage)
        
        self.app.add_url_rule("/data/<path:name>", view_func = self.getData)
        self.app.add_url_rule("/frontend/<name>", view_func = self.getFront)
        self.app.add_url_rule("/<folder>/<name>", view_func = self.getProjectPage)
        self.colorOrder = []
        self.appThread = None
        self.updateTime = None


    def getCorePage(self, name: str) -> str:        
        """
        function to construct the template data for the core pages, like the homepage
        and about me

        Parameters:
            None

        Returns:
            str: html text rendered by the Flask templating engine representing the complete project page to be shown to the user's browser
        """
        print(f"core page {name}")
        if name in ['home', 'contact-me', 'resume', 'about-me']:
            corePagePath = self.mappingTable["corePage.html"]            
            pageBuffer = self.cursor.execute(f"select * from articles where pageName = '{name}';")        
            data = pageBuffer.fetchone()
            pageData = Portfolio.loadTextFile(corePagePath)
            output = render_template_string(pageData, pageData = self.linkData, 
                        title = data[1], len = self.numberOfProjects, cardColor = self.colorOrder,
                        bodyText = html.unescape(data[4]))
        elif name == "directory":
            pass
        elif name == "login":
            pass
        elif name == "new-project-page":
            pass
        elif name == "projects-timeline":
            pass

        return output



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
        """
        small helper function to load an entire text file as a single string and return it.

        Parameters:
            filePath (Path): the path to the file you would like to load

        Returns:
            str: a string containing the raw text contained in the file at the provided path.
        """ 

        handle = open(filePath, "r")
        output = handle.read()
        handle.close()
        return output
    

    def getData(self, name: str) -> Response:
        """
        function to trick Flask into letting you re-use the helper-function 'getFile'
        Used to route requests for files in the data folder

        Parameters:
            name (str): the relative path to the file being requested

        Returns:
            Response: returns the file requested by the user

        """

        return self.getFile("data", name)
    

    def getFront(self, name: str = None) -> Response:
        """
        function to trick Flask into letting you re-use the helper-function 'getFile'
        Used to route requests for files in the frontend folder

        Parameters:
            name (str): the relative path to the file being requested

        Returns:
            Response: returns the file requested by the user

        """
        
        if name == None:
            name = Path(request.path).name

        return self.getFile("frontend", name)

        
    def getFile(self, folder: str, name: str) -> Response:
        """
        reusable function used to serve requested files back to the web users with correctly
        defined mime-types.

        Parameters:
            folder (str): the top level folder containing the files needed, defined by code, not through requests due to inherent limitations of request routing
            name (str): the relative path to the file desired by the requester, minus the top level folder

        Returns:
            Response: returns the file requested by the user
        """        

        pathToFile = rootDir / folder / str(name)        
        mimeType = self.mimeTable[pathToFile.suffix]
        return send_file(pathToFile, mimetype = mimeType)

    
    def getProjectPage(self, folder: str, name: str) -> str:
        """
        function to construct the template data for the requested project page.
        recalls the pre-rendered html for each page from an in-memory sqlite3 database.

        Parameters:
            name (str): the internal name (rather than the title) of the project being requested

        Returns:
            str: html text rendered by the Flask templating engine representing the complete project page to be shown to the user's browser
        """

        projectPagePath = self.mappingTable["projectPage.html"]
        pageData = Portfolio.loadTextFile(projectPagePath)
        pageBuffer = self.cursor.execute(f"select * from articles where pageName = '{name}';")        
        data = pageBuffer.fetchone()
        output = render_template_string(pageData, pageData = self.linkData, title = data[1], 
                    createdOn = data[2], modifiedOn = data[3], 
                    bodyText = html.unescape(data[4]), sourceCodeLink = data[6], 
                    len = self.numberOfProjects, cardColor = self.colorOrder,
                    systemUpdateTime = self.updateTime)
        return output


    #TODO: make this not crash when the input doesn't contain a matching tag
    @staticmethod
    def extractTaggedText(inputBody: list[str], tagName: str) -> str:        
        """
        a custom function which will return the text of the first element in the input list which contains a match for the given markdown attribute tag
        will crash if there is no matching element.

        Parameters:
            inputBody (list[str]): a list of strings (each string in the list is a new line) of markdown formatted text
            tagName (str): the name of the attribute tag you'd like the relevant text for
        
        Returns:
            str: a string containing the text on the matching line of input strings, minus the attribute tag used to find it
        """

        tagValue = f"{{#{tagName}}}"
        buffer = list(filter(lambda x : tagValue in x, inputBody))[0]
        output = buffer.replace(tagValue, "").replace("#", "").strip()
        return output
    
    
    @staticmethod
    def removeTagFromText(inputBody: list[str], tagName: str) -> list[str]:        
        """
        a custom function which will remove instances of input tag from the list of input strings in the output

        Parameters:
            inputBody (list[str]): a list of strings of markdown formatted text, presumably with tagged attributes
            tagName (str): the name of the attribute you'd like to remove lines of text with matches for

        Returns
            list[str]: a copy of the input list of strings, minus any elements which contained matches for the input tag
        """

        tagValue = f"{{#{tagName}}}"
        output = list(filter(lambda x : tagValue not in x, inputBody))
        return output
    

    def getProjectPages(self):
        projectLinksBuffer = self.cursor.execute("select pageName, title, summary, folder from articles")        
        projectLinks = projectLinksBuffer.fetchall()
        print("==========================")
        print("project links generated here")
        print(projectLinks)
        print(len(projectLinks))
        print()
        print()
        self.linkData = [] #config is somehow getting called twice????
        print("link data")
        print(self.linkData)

        for element in projectLinks:
            print(element)
            newURL = f"/{element[3]}/{element[0]}" if element[3] != "core" else f"/{element[0]}"
            buffer = {
                'URL': newURL,
                'title': element[1],
                'summary': element[2]
            }
            self.linkData.append(buffer)
            print("space")
        
        print(len(self.linkData))
        self.numberOfProjects = len(self.linkData)


    def getNewProjectPage(self):
        print("create new project page")
        form = NewProjectPage()
        projectPagePath = self.mappingTable["newProjectPage.html"]
        pageData = Portfolio.loadTextFile(projectPagePath)        
        output = render_template_string(pageData, pageData = self.linkData, title = 'Create a New Project',                     
                    len = self.numberOfProjects, cardColor = self.colorOrder,
                    systemUpdateTime = self.updateTime, projectForm = form)
        
        return output
    

    def addPage(self):
        print("adding page")
        form = NewProjectPage()
        # form.validate_on_submit()
        print(form.body.data)
        self.insertNewPageToDB(form)
        return redirect('/home')


    def insertNewPageToDB(self, form):
        buffer = (
            form.title.data.strip().replace(" ", "-"),
            form.title.data.strip(),
            time.time(),
            time.time(),
            form.body.data.strip(),
            form.summary.data.strip(),
            form.sourceCodeLink.data.strip(),
            form.folder.data.strip()
        )
        self.cursor.execute(self.insertStatement, buffer)
        self.config()

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
        imgTag['class'] = imgTag.get('class', []) + ['img-fluid']


    @staticmethod
    def modifyTableTag(tableTag):
        tableTag['class'] = tableTag.get('class', []) + ['table']


    def modifyCodeBlock(divTag):
        check = divTag.get('class', [])
        style = divTag.get('style', [])

        if "codehilite" in check:
            divTag['class'] = check + ['rounded']
            divTag['style'] = style + ['background-color: #fffef7;'] + ['padding-top: 1%;'] + ['padding-bottom: 1%;'] + ['padding-left: 1%;'] + ['padding-right: 1%;'] + ['max-width:calc(50vw - 1px);']


    def generateDBEntries(self):               
        print("loading db contents") 
        print(self.articlePaths)

        for element in self.articlePaths:
            pageName = element.stem                        
            raw0 = Portfolio.loadTextFile(element)
            print(f"file: {pageName}\n {raw0}")
            raw1 = Portfolio.removePreviewMaterials(raw0)
            converter = Markdown(extensions = ['extra', 'markdown_mark', 'markdown_checklist.extension', 'sane_lists', 'pymdownx.tilde', 'codehilite', 'meta', 'nl2br', 'toc'])
            bodyBuffer = converter.convert(raw1)
            metaData = converter.Meta
            title = metaData['title'][0]
            codeLink = metaData['link'][0]
            summary = metaData['summary'][0]
            createdOn = time.mktime(datetime.strptime(metaData['created-on'][0].strip(), "%d/%m/%Y %I:%M%p %Z").timetuple())
            modifiedOn = time.mktime(datetime.strptime(metaData['last-modified'][0].strip(), "%d/%m/%Y %I:%M%p %Z").timetuple())
            folder = metaData['folder'][0]
            doc = BeautifulSoup(bodyBuffer, features = 'html.parser')
            imageTags = doc.find_all('img') 
            tableTags = doc.find_all('table')           
            divTags = doc.find_all('div')
            list(map(lambda x : Portfolio.modifyImgTag(x), imageTags)) #could these be converted to clever css?
            list(map(lambda x : Portfolio.modifyTableTag(x), tableTags))
            list(map(lambda x : Portfolio.modifyCodeBlock(x), divTags))
            bodyBuffer2 = doc.prettify()
            body = html.escape(bodyBuffer2)

            self.cursor.execute(self.insertStatement, (pageName, title, createdOn, modifiedOn, body, summary, codeLink, folder))

        self.connection.commit()


    def constructDB(self):
        handle = open(self.databaseConstructor, "r")
        scriptText = handle.read()
        self.cursor.executescript(scriptText)
        self.connection.commit()
        handle.close()


    #caution, running this on bootup each time could leak information to hostile hackers indicating that they successfully crashed the server!
    #TODO: add reject check if color list contains duplicates when the link count is less than the color pallet size
    def generateCardColorList(self, numberOfLinks) -> list[str]:
        northNeighborSame = lambda index, data : False if index == 0 else data[index] == data[index -1]
        southNeighborSame = lambda index, data : False if index == (len(data) - 1) else data[index + 1] == data[index]
        differentFromNeighbors = lambda index, data : not northNeighborSame(index, data) and not southNeighborSame(index, data)
        validCardColorList = lambda data : list(map(lambda index : differentFromNeighbors(index, data), range(0, len(data))))
        copyListExcluding = lambda data, exclusions : list(filter(lambda x : x not in exclusions, data))        
        generateColorList = lambda colorList, length : reduce(lambda accu, i : accu + [random.choice(copyListExcluding(colorList, accu[-1]))], range(0, length - 1), [random.choice(colorList)])
        containsAllColors = lambda data, reference : all(list(map(lambda x : x in data, reference)))

        go = True
        output = []
        while go:
            output = generateColorList(self.cardColorList, numberOfLinks)
            print(output)
            colorCheck = containsAllColors(output, self.cardColorList) or (numberOfLinks < len(self.cardColorList))
            go = not (validCardColorList(output) and colorCheck)

        return output
    

    def setupDB(self):
        """
        sets up the sqlite3, in-memory database.  will close out a pre-existing instance if one 
        is already running.  Loads in data from the project markdown documents into the database
        """

        if self.connection != None:
            self.cursor.close()
            self.connection.close()
        
        self.connection = sqlite3.connect(":memory:", check_same_thread = False) #use file once change detection has been implemented        
        self.cursor = self.connection.cursor()        
        self.constructDB()
        self.generateDBEntries()
        
            


    def config(self):
        """
        this coordinates all of the configuration and setup processes necessary before the webserver can start
        It performs the following tasks, in order
        1. finds all of the assets in the frontend folder (reusable / shared assets assets)
        2. finds all of the assets in the data folder (actual project files)
        3. generates the local paths to all of the project markdown documents
        4. configures an in memory sqlite3 database using an sql script and loads in all the project data
        5. generates all the pairs of project titles and URLs
        6. pseudo-randomly generates the colors for the link cards in the side bar across the whole site
        """

        self.files = Portfolio.findFiles(rootDir / 'frontend')
        self.files.extend(Portfolio.findFiles(rootDir / 'data'))
        self.articlePaths = list(filter(lambda x : (str(self.dataFolder) in str(x)) and (x.suffix == ".md"), self.files))        
        list(map(lambda x : self.mappingTable.update({x.stem : x}), self.files))
        list(map(lambda x : self.mappingTable.update({x.name : x}), self.files))
        self.setupDB()
        self.getProjectPages()
        self.colorOrder = self.generateCardColorList(self.numberOfProjects)
        self.updateTime = int(time.time())


    def stop(self):
        """
        kills the process holding the Flask web server.  must be called if you want to update any of
        the servers assets due to some undocumented(?) deep copy behavior of Flask and data that it
        has access to.
        """

        self.appThread.kill()


    def start(self):
        """
        runs all of the various config and setup processes and the starts the webserver on a seperate process so that execution is not halting

        Parameters:
            None

        Returns:
            None
        """
        self.config()        
        appRun = lambda : self.app.run(debug = False, host = socket.gethostbyname(socket.gethostname()))
        self.appThread = Process(target = appRun)
        self.appThread.start()
        print("running")





class BasicEventHandler(FileSystemEventHandler):
    """
    custom Watchdog event handler which will set a flag high whenever the files and folders
    being monitored get updated, and will set the flag low after you check for an update.
    """

    def __init__(self):
        super(BasicEventHandler, self).__init__()
        self.eventFlag = True


    def on_any_event(self, event):
        super(BasicEventHandler, self).on_any_event(event)        
        if(event.event_type != 'opened'):
            print(event)            
            self.eventFlag = True

    def anythingHappen(self) -> bool:
        output = self.eventFlag
        self.eventFlag = False
        return output
        






if __name__ == "__main__":
    instance = Portfolio()
    instance.start()
    observer = Observer()
    eventHanlder = BasicEventHandler()
    observer.schedule(eventHanlder, rootDir / 'data', recursive = True)
    observer.start()
    print(f"intial process {initial}")

    #TODO: start implementing a smarter, more efficient update method
    while (str(Process.pid) == initial):        
        if eventHanlder.anythingHappen():
            print("reload")
            instance.stop()
            instance.start()

        time.sleep(1)

        
        

    