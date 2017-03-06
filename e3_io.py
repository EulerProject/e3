'''
Created on Nov 22, 2016

@author: Thomas
'''
import os.path
from os.path import expanduser
import shutil
import uuid
from subprocess import Popen, PIPE, call
from autologging import logged
from pinject import copy_args_to_public_fields
import networkx as nx
from networkx.readwrite import json_graph
import json
from bs4 import BeautifulSoup
import datetime

e3Dir = os.path.join(expanduser("~"), ".e3")

def get_e3_dir():
    if not os.path.isdir(e3Dir):
        os.makedirs(e3Dir)
    return e3Dir

def get_e3_data_git_dir():
    e3Dir = get_e3_dir()
    e3DataGitDir = os.path.join(e3Dir, "e3_data_git")
    if not os.path.isdir(e3DataGitDir):
        os.makedirs(e3DataGitDir)
    return e3DataGitDir
    

def get_working_dir():
    return os.path.join(os.getcwd(), "e3_data")

def get_home_dir():
    return expanduser("~")

def clean_e3_dir():
    shutil.rmtree(get_e3_dir())

def clean_e3_data_git_dir():
    shutil.rmtree(get_e3_data_git_dir())
    
def clean_working_dir():
    workingDir = get_working_dir()
    if os.path.isdir(workingDir):
        shutil.rmtree(workingDir)
    
def reset():
    clean_e3_dir()
    clean_working_dir()
    ConfigManager().get_config()
    tapManager = TapManager()
    tapManager.load_demo_taps()
    tapManager.set_current_tap(tapManager.get_default_tap())
    
def clear():
    configManager = ConfigManager()
    config = configManager.get_config()
    clean_e3_dir()
    clean_working_dir()
    tapManager = TapManager()
    tapManager.load_demo_taps()
    tapManager.set_current_tap(tapManager.get_default_tap())
    configManager.store_config(config)
    
def set_git_credencials(host, user, password):
    p = Popen("git config --global user.email \"" + user + "\"", stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = p.communicate()
    
    p = Popen("git config --global user.name \"" + user + "\"", stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = p.communicate()
    
    config = ConfigManager().get_config()
    netrc_file = os.path.join(get_home_dir(), ".netrc")
    if not os.path.isfile(netrc_file):
        with open(netrc_file, 'w') as f:
            f.write("machine " + host + "\n")
            f.write("login " + user + "\n")
            f.write("password " + password + "\n")
            
@logged
class CleantaxReader(object):
    def get_articulation_from_cleantax(self, cleantaxLine):
        import re
        import e3_validation
        for validRelation in e3_validation.validRelations:
            match = re.match(validRelation.regex, cleantaxLine)
            if match:
                leftNodes = list(match.groups())[:validRelation.leftCount]
                relation = list(match.groups())[validRelation.leftCount : validRelation.leftCount + 1][0]
                rightNodes = list(match.groups())[validRelation.leftCount + 1:]
                import e3_model
                articulation = e3_model.Articulation(leftNodes, rightNodes, relation)
                return articulation
        return None
    
    def get_tap_from_cleantax_file(self, cleantaxFile):
        config = ConfigManager().get_config()
        with open(cleantaxFile, 'r') as f:
            lines = f.readlines()
            return self.get_tap_from_cleantax(config['defaultIsCoverage'], config['defaultIsSiblingDisjointness'], config['defaultRegions'], lines)
    
    def get_tap_from_cleantax(self, isCoverage, isSiblingDisjointness, regions, cleantax):
        cleantax = self.get_normalized_cleantax(cleantax)
        import e3_model
        tap = e3_model.Tap(isCoverage, isSiblingDisjointness, regions, [], [])
        
        import e3_validation
        e3_validation.CleantaxValidator().validate_cleantax(cleantax)
        cleantaxTaxonomyLines = self.get_cleantax_taxonomy_lines(cleantax)
        taxonomies = []
        for taxonomyLines in cleantaxTaxonomyLines:
            header = taxonomyLines[0]
            taxonomyId = header.split()[1]
            taxonomyName = header.split()[2]
            taxonomy = e3_model.Taxonomy(taxonomyId, taxonomyName)
            for line in taxonomyLines[1:]:
                nodes = line[1:-1].split()
                if len(nodes) > 1:
                    taxonomy.add_children(nodes[0], nodes[1:])
                elif len(nodes) == 1:
                    taxonomy.add_node(nodes[0])
            tap.add_taxonomy(taxonomy)
        
        cleantaxArticulationLines = self.get_cleantax_articulation_lines(cleantax)
        for line in cleantaxArticulationLines:
            articulation = self.get_articulation_from_cleantax(line)
            
            if articulation is  None:
                raise Exception("Not a valid relation in articulation: " + line)
            else:
                import e3_validation
                if e3_validation.ModelValidator().is_valid_new_articulation(articulation, tap):
                    tap.add_articulation(articulation)
        return tap
    
    def get_normalized_cleantax(self, cleantax):
        normalizedLines = []
        for line in cleantax:
            if '#' in line:
                line = line.split('#')[0]
            line = line.strip().rstrip()
            if len(line.strip()) == 0: continue
            normalizedLines.append(line)
        return normalizedLines
    
    def get_cleantax_taxonomy_lines(self, cleantax):
        cleantax = self.get_normalized_cleantax(cleantax)
        taxonomies = []
        taxonomy = []
        for line in cleantax:
            line = line.strip().rstrip()
            if line.startswith('#'): continue
            if len(line.strip()) == 0: continue
            if line.startswith('taxonomy') and not len(taxonomy) == 0:
                if len(taxonomy) > 0: taxonomies.append(taxonomy)
                taxonomy = []
            if line.startswith("articulation"):
                if len(taxonomy) > 0: taxonomies.append(taxonomy)
                taxonomy = []
                return taxonomies
            taxonomy.append(line)
        if len(taxonomy) > 0: taxonomies.append(taxonomy)
        return taxonomies
        
    def get_cleantax_articulation_lines(self, cleantax):
        cleantax = self.get_normalized_cleantax(cleantax)
        articulations = []
        articulationStarts = False
        for line in cleantax:
            line = line.strip().rstrip()
            if len(line) == 0 or line.startswith('#'): continue
            if line.startswith("articulation"):
                articulationStarts = True
                continue
            if articulationStarts:
                articulations.append(line)
        return articulations

class TapManager(object):
    def get_history_file(self):
        historyFile = os.path.join(get_e3_dir(), ".history")
        if not os.path.isfile(historyFile):
            with open(historyFile, 'w') as f:
                pass
        return historyFile
    def get_named_history(self):
        with open(self.get_history_file(), 'r') as historyFile:
            import e3_model
            try:
                jsonData = json.load(historyFile)
                g = json_graph.node_link.node_link_graph(jsonData)
                
                namedG = nx.DiGraph()
                for node in g.nodes(data=True):
                    name = self.get_tap_name(node[0])
                    if name is None and "/" in node[0]:
                        parts = node[0].split("/")
                        name = self.get_tap_name(parts[0]) + "/" + parts[1]
                    elif name is None:
                        name = node[0]
                    namedG.add_node(name, node[1])
                for edge in g.edges(data=True):
                    nameSrc = self.get_tap_name(edge[0])
                    nameDst = self.get_tap_name(edge[1])
                    if nameSrc is None and "/" in edge[0]:
                        parts = edge[0].split("/")
                        nameSrc = self.get_tap_name(parts[0]) + "/" + parts[1]
                    elif nameSrc is None:
                        nameSrc = edge[0]
                    if nameDst is None and "/" in edge[1]:
                        parts = edge[1].split("/")
                        nameDst = self.get_tap_name(parts[0]) + "/" + parts[1]
                    elif nameDst is None:
                        nameDst = edge[1]
                    namedG.add_edge(nameSrc, nameDst, edge[2])
                return e3_model.History(namedG)
            except Exception as e:
                #print str(e)
                return e3_model.History(None)
    def get_history(self):
        with open(self.get_history_file(), 'r') as historyFile:
            import e3_model
            try:
                jsonData = json.load(historyFile)#, cls = HistoryJSONDecoder)
                g = json_graph.node_link.node_link_graph(jsonData)
                return e3_model.History(g)
            except Exception as e:
                return e3_model.History(None)
    def store_history(self, history):
        with open(self.get_history_file(), 'w') as historyFile:
            jsonData = json_graph.node_link.node_link_data(history.g)
            import e3_model
            json.dump(jsonData, historyFile)#, cls = HistoryJSONEncoder)
    def add_history_edge(self, fromTapId, toTapId, attributesDict):
        history = self.get_history()
        history.add_edge(fromTapId, toTapId, attributesDict)
        self.store_history(history)
    def add_history_node(self, tapId, attributesDict):
        history = self.get_history()
        history.add_node(tapId, attributesDict)
        self.store_history(history)
        
    def load_demo_taps(self):
        demosDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demos")
        for root, dirs, files in os.walk(demosDir):
            for dir in dirs:
                cleantaxFile = os.path.join(demosDir, os.path.join(dir, os.listdir(os.path.join(demosDir, dir))[0]))
                import e3_command
                loadTap = e3_command.LoadTap(cleantaxFile)
                loadTap.run()
                tap = self.get_current_tap()
                if tap:
                    nameTap = e3_command.NameTap(tap, "demo_" + dir)
                    nameTap.run()
    def get_current_tap_name(self):
        tap = self.get_current_tap()
        return self.get_tap_name(tap.get_id())
    
    def get_current_tap_name_and_status(self):
        tap = self.get_current_tap()
        return self.get_tap_name_and_status(tap.get_id())
    
    def get_tap_name(self, tapId):
        name = self.get_name(tapId)
        return name
        #if name:
        #    return name + " = " + tapId
        #else:
        #    return tapId
    
    def get_tap_name_and_status(self, tapId):
        tap_name = self.get_tap_name(tapId)
        tap = self.get_tap(tapId)
        status = tap.get_status_message()
        if status:
            return tap_name + " (" + status + ")"
        return tap_name
    
    def get_current_tap(self):
        with open(self.get_current_tap_file(), 'r') as currentTapFile:
            tap = self.get_tap(currentTapFile.readline())
            if tap is None:
                return self.get_default_tap()
            return tap
        
    def set_current_tap(self, tap):
        self.store_tap(tap)
        with open(self.get_current_tap_file(), 'w') as currentTapfile:
            currentTapfile.write(tap.get_id())
    
    def store_tap(self, tap):
        existingName = self.get_name(tap.get_id())
        if existingName is None:
            defaultTap = self.get_default_tap()
            name = "empty_tap"
            if tap.get_id() != defaultTap.get_id():
                import e3_name_generator
                randomName = e3_name_generator.get_random_name(None, None)
                names = self.get_names()
                name = randomName
                id = 1
                while name in names:
                    name = randomName + "_" + id
                    id = id + 1
            self.set_name(name, tap.get_id())
        
        tapFile = self.get_tap_file(tap.get_id())
        with open(tapFile, 'w') as f:
            f.write(str(tap.isCoverage) + '\n')
            f.write(str(tap.isSiblingDisjointness) + '\n')
            f.write(tap.regions + '\n')
            f.write('\n')
            for taxonomy in tap.taxonomies:
                f.write(taxonomy.__str__())
                f.write('\n\n')
            f.write('articulation\n')
            for articulation in tap.articulations:
                f.write(articulation.__str__() + '\n')
        self.store_tap_to_cleantax(tap)

    def store_tap_to_cleantax(self, tap):
        cleantaxFile = self.get_cleantax_file(tap.get_id())
        with open(cleantaxFile, 'w') as f:  
            f.write(tap.get_cleantax())

    def get_default_tap(self):
        config = ConfigManager().get_config()
        isCoverage = config['defaultIsCoverage']
        isSiblingDisjointness = config['defaultIsSiblingDisjointness']
        regions = config['defaultRegions']
        import e3_model
        return e3_model.Tap(isCoverage, isSiblingDisjointness, regions, [], [])
            
    def get_tap_from_id_or_name(self, id_or_name):
        if self.is_tap_id(id_or_name):
            return self.get_tap(id_or_name)
        if self.is_tap_name(id_or_name):
            id = self.get_tap_id(id_or_name)
            if id:
                return self.get_tap(id)
            
    def get_tap(self, tapId):
        if not tapId or tapId is None:
            return None
        tapFile = self.get_tap_file(tapId)
        if not os.path.isfile(tapFile):
            return None
        
        cleantax = []
        with open(tapFile, 'r') as f:
            config = ConfigManager().get_config()
            isCoverage = config['defaultIsCoverage']
            isSiblingDisjointness = config['defaultIsSiblingDisjointness']
            regions = config['defaultRegions']
        
            for i, line in enumerate(f):
                if i == 0:
                    isCoverage = line.rstrip() == 'True'
                elif i == 1:
                    isSiblingDisjointness = line.rstrip() == 'True'
                elif i == 2:
                    regions = line.rstrip()
                elif i >= 4:
                    cleantax.append(line)
        cleantaxReader = CleantaxReader()
        return cleantaxReader.get_tap_from_cleantax(isCoverage, isSiblingDisjointness, regions, cleantax)
    
    def get_tap_file(self, tapId):
        tapDir = self.get_tap_dir(tapId)
        if tapDir is None:
            return None
        tap_file = os.path.join(self.get_tap_dir(tapId), ".tap")
        return tap_file

    def get_cleantax_file(self, tapId):
        tap_name = self.get_tap_name(tapId).replace(" ", "")
        cleantax_file = os.path.join(self.get_taps_dir(), tap_name, ".cleantax")
        if not os.path.isfile(cleantax_file):
            with open(cleantax_file, 'w') as f:
                pass
        return cleantax_file
    
    def get_0_input_dir(self, tapId):
        return os.path.join(self.get_taps_dir(), self.get_tap_name(tapId).replace(" ", ""), "0-Input")
    
    def get_1_asp_input_dir(self, tapId):
        return os.path.join(self.get_taps_dir(), self.get_tap_name(tapId).replace(" ", ""), "1-ASP-input-code")
    
    def get_2_asp_output_dir(self, tapId):
        return os.path.join(self.get_taps_dir(), self.get_tap_name(tapId).replace(" ", ""), "2-ASP-output")
    
    def get_3_mir_dir(self, tapId):
        return os.path.join(self.get_taps_dir(), self.get_tap_name(tapId).replace(" ", ""), "3-MIR")
    
    def get_4_pws_dir(self, tapId):
        return os.path.join(self.get_taps_dir(), self.get_tap_name(tapId).replace(" ", ""), "4-PWs")
    
    def get_5_aggregates_dir(self, tapId):
        return os.path.join(self.get_taps_dir(), self.get_tap_name(tapId).replace(" ", ""), "5-Aggregates")
    
    def get_6_lattices_dir(self, tapId):
        return os.path.join(self.get_taps_dir(), self.get_tap_name(tapId).replace(" ", ""), "6-Lattices")
    
    def get_tap_dir(self, tapId):
        tap_name = self.get_tap_name(tapId)
        if tap_name is None:
            return None
        tap_name = tap_name.replace(" ", "")
        tap_dir = os.path.join(get_e3_dir(), "taps", tap_name)
        if not os.path.isdir(tap_dir):
            os.makedirs(tap_dir)
        return tap_dir
    
    def get_taps_dir(self):
        taps_dir = os.path.join(get_e3_dir(), "taps")
        if not os.path.isdir(taps_dir):
            os.makedirs(taps_dir)
        return taps_dir
    
    def get_current_tap_file(self):
        current_tap_file = os.path.join(get_e3_dir(), ".current_tap")
        if not os.path.isfile(current_tap_file):
            with open(current_tap_file, 'w') as f:
                pass
        return current_tap_file
    
    def set_name(self, name, tapId):
        import yaml
        oldName = self.get_name(tapId)
        oldTapDir = None
        if oldName is not None:
            oldTapDir = self.get_tap_dir(tapId)
        names = { }
        with open(self.get_names_file(), "r") as namesFile:
            doc = yaml.load(namesFile)
            if doc:
                for key, value in doc.iteritems():
                    names[key] = value
        if oldName in names:
            del names[oldName]
        names[name] = tapId
        with open(self.get_names_file(), "w") as namesFile:
            yaml.dump(names, namesFile, default_flow_style=False)
        if oldTapDir is not None:
            for filename in os.listdir(oldTapDir):
                shutil.move(os.path.join(oldTapDir, filename), self.get_tap_dir(tapId))
            shutil.rmtree(oldTapDir)
    
    def get_names(self):
        import yaml
        names = []
        with open(self.get_names_file(), 'r') as namesFile:
            doc = yaml.load(namesFile)
            if doc:
                for key, value in doc.items():
                    names.append(key + " = " + value)
        return sorted(names)
    
    def clear_names(self):
        with open(self.get_names_file(), 'w'): pass
    
    def is_tap_id(self, tapId):
        tapFile = self.get_tap_file(tapId)
        if tapFile is None:
            return False
        if os.path.isfile(tapFile):
            return True
        return False
    
    def is_tap_name(self, name):
        tapId = self.get_tap_id(name)
        if tapId is None:
            return False
        else:
            tapFile = self.get_tap_file(tapId)
            if not os.path.isfile(tapFile):
                return False
            else:
                return True
        
    def get_tap_id(self, name):
        import yaml
        name = name.strip()
        with open(self.get_names_file(), 'r') as namesFile:
            doc = yaml.load(namesFile)
            if doc:
                if name in doc:
                    return doc[name]
        return None
    
    def get_name(self, tapId):
        import yaml
        with open(self.get_names_file(), 'r') as namesFile:
            doc = yaml.load(namesFile)
            if doc:
                for key, value in doc.items():
                    if value == tapId:
                        return key
        return None
    
    def get_names_file(self):
        namesFile = os.path.join(get_e3_dir(), ".names")
        if not os.path.isfile(namesFile):
            with open(namesFile, 'w') as f:
                pass
        return namesFile    
    
class ProjectManager(object):
    def remove_project(self, project):
        if self.exists_project(project):
            shutil.rmtree(get_project_dir(project))
    
    def set_current_project(self, project):
        with open(self.get_current_project_file(), 'w') as currentProjectFile:
            if not project:
                pass
            else:
                currentProjectFile.write(project)
                
    def get_current_project(self):
        with open(self.get_current_project_file(), 'r') as currentProjectFile:
            return currentProjectFile.readline()
        
    def set_history(self, project, history):
        with open(self.get_history_file(project), 'w') as historyFile:
            historyFile.write(history)
        
    def get_projects(self):
        return os.listdir(self.get_projects_dir())
        
    def clear_projects(self):
        for project in self.get_projects():
            self.remove_project(project)
            
    def create_project(self, project):
        os.makedirs(os.path.join(self.get_projects_dir(), project));
            
    def exists_project(self, project):
        return os.path.isdir(self.get_project_dir(project))
    
    def append_project_history(self, input, command):
        #if not isinstance(command, e3_command.MiscCommand):
        id = str(uuid.uuid4())
        currentProject = None
        with open(self.get_current_project_file(), 'r') as currentProjectFile:
            currentProject = currentProjectFile.readline()
        if currentProject:
            with open(self.get_history_file(currentProject), 'a') as historyFile:
                historyFile.write(id + " " + input + '\n')
            tap = TapManager().get_current_tap()
            stepDir = os.path.join(self.get_project_dir(currentProject), id)
            import e3_command
            if isinstance(command, e3_command.MiscCommand):
                os.makedirs(stepDir)
            if isinstance(command, e3_command.ModelCommand):
                shutil.copytree(TapManager().get_tap_dir(tap.get_id()), stepDir)
                pass
            if isinstance(command, e3_command.Euler2Command):
                shutil.copytree(TapManager().get_tap_dir(tap.get_id()), stepDir)
                pass
            with open(os.path.join(stepDir, '.outputs'), 'w') as f:
                f.write('\n'.join(command.get_output()))
            with open(os.path.join(stepDir, '.command'), 'w') as f:
                f.write(input)
                
    def get_current_project_file(self):
        current_project_file = os.path.join(get_e3_dir(), ".current_project")
        if not os.path.isfile(current_project_file):
            with open(current_project_file, 'w') as f:
                pass
        return current_project_file
    
    def get_history_file(self, project):
        if self.exists_project(project):
            history_file = os.path.join(self.get_project_dir(project), ".history")
            if not os.path.isfile(history_file):
                with open(history_file, 'w') as f:
                    pass
            return history_file
    
    def get_projects_dir(self):
        projectsDir = os.path.join(get_e3_dir(), "projects")
        if not os.path.isdir(projectsDir):
            os.makedirs(projectsDir)
        return projectsDir
    
    def get_project_dir(self, project):
        return os.path.join(self.get_projects_dir(), project)
    
class ConfigManager(object):
    def get_config(self):
        import yaml
        config = None
        with open(self.get_config_file(), 'r') as f:
            config = yaml.safe_load(f)
            if(config):
                return config
        defaultConfig = {
                    'euler2Executable': 'euler2', #os.path.join(get_home_dir(), 'git', 'EulerX'),
                    'imageViewer': 'xdg-open {file}',
                    'htmlViewer': 'xdg-open {file}',
                    'maxPossibleWorldsToShow': 5,
                    'imageFormat': 'svg',
                    'repairMethod': 'topdown',
                    'defaultIsCoverage': True,
                    'defaultIsSiblingDisjointness': True,
                    'defaultRegions': 'mnpw',
                    'reasoner': 'dlv',
                    'cacheGitRepo': '',
                    'workspaceGitRepo': '',
                    'showOutputFileLocation': False
                    #'gitUser': "",
                    #'gitPassword': ""
                    }
        config = defaultConfig
        with open(self.get_config_file(), 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        return config
    
    def store_config(self, config):
        import yaml
        with open(self.get_config_file(), 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
            
    def get_config_file(self):
        config_file = os.path.join(get_e3_dir(), ".config")
        if not os.path.isfile(config_file):
            with open(config_file, 'w+') as f:
                pass
        return config_file
    
class GraphCreator(object):
    def create_graph(self, targetDir, templateName, targetName, dataDict):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "graphs", templateName + ".html"),"r+") as htmlTemplateFile:
            htmlTemplate = htmlTemplateFile.read()
            soup = BeautifulSoup(htmlTemplate, 'lxml')
            for key in dataDict:
                dataElement = soup.find(id = key)
                data = dataDict[key]
                if data[0] == "json":
                    dataElement.string = json.dumps(data[1])
                elif data[0] == "plain":
                    dataSoup = BeautifulSoup(data[1], 'html.parser')
                    #x = dataSoup.find("svg")
                    #if x is not None:
                    #    x['height'] = "100%"
                    #    x['width'] = "100%"
                    dataElement.append(dataSoup)
                elif data[0] == "insert":
                    dataElement.insert(0, data[1])
            htmlDoc = soup.prettify("utf-8")
            with open(os.path.join(targetDir, targetName + ".html"), "wb") as file:
                file.write(htmlDoc)
    def create_history_graph(self, targetDir):
        history = TapManager().get_named_history()
        jsonData = json_graph.node_link.node_link_data(history.g)
        
        data = {}
        data['name'] = "history"
        data['children'] = []
        
        #for node in jsonData['nodes']:
        #    newJsonDataNodes.append(node)
        
        import e3_parse
        commandProvider = e3_parse.CommandProvider()
        jsonData['link'] = jsonData['links'].sort(key=lambda l: l['startTime'], reverse=False)
        lastTapNode = None
        e3DataDir = get_working_dir()
        for link in jsonData['links']:
            link['source'] = jsonData['nodes'][link['source']]
            link['target'] = jsonData['nodes'][link['target']]
            command = commandProvider.provide(link['command'])
            startTime = datetime.datetime.utcfromtimestamp(link['startTime']).strftime('%m/%d/%Y %H:%M:%S')
            endTime = datetime.datetime.utcfromtimestamp(link['endTime']).strftime('%m/%d/%Y %H:%M:%S')
            runTime =  str(round(link['endTime'] - link['startTime'], 2)) + " sec."
            
            #if isinstance(command, Euler2Command):
            #    child = {}
            #    child['name'] = link['command']
            #    child['children'] = []
            #    data['children'].append(child)
            if lastTapNode is None:
                sourceNode = {}
                sourceNode['name'] = link['source']['id']
                sourceNode['type'] = "tap"
                sourceNode['href'] = os.path.join("_".join(sourceNode['name'].split()), "index.html")
                sourceNode['children'] = []
                data['children'].append(sourceNode)
                lastTapNode = sourceNode
                
            import e3_command
            if isinstance(command, e3_command.ModelCommand):
                commandNode = {}
                commandNode['name'] = link['command']
                commandNode['type'] = "modelCommand"
                commandNode['startTime'] = startTime
                commandNode['endTime'] = endTime
                commandNode['runTime'] = runTime
                commandNode['children'] = []
                lastTapNode['children'].append(commandNode)
                
                targetNode = {}
                targetNode['name'] = link['target']['id']
                targetNode['type'] = "tap"
                targetNode['href'] = os.path.join("_".join(targetNode['name'].split()), "index.html")
                targetNode['children'] = []
                data['children'].append(targetNode)
                lastTapNode = targetNode
                
            if isinstance(command, e3_command.Euler2Command):
                commandNode = {}
                commandNode['name'] = link['command']
                commandNode['type'] = "euler2Command"
                commandNode['startTime'] = startTime
                commandNode['endTime'] = endTime
                commandNode['runTime'] = runTime
                commandNode['children'] = []
                lastTapNode['children'].append(commandNode)
                
                targetNode = {}
                targetNode['name'] = link['target']['output']
                targetNode['type'] = "commandOutput"
                targetNode['children'] = []
                runDir = os.path.join(e3DataDir, "_".join(lastTapNode['name'].split()), "_".join(link['command'].split()))
                relativeRunDir = os.path.join("_".join(lastTapNode['name'].split()), "_".join(link['command'].split()))
                
                if os.path.isdir(runDir):
                    files = os.listdir(runDir)
                    files = sorted(files)#.sort(key=lambda f: os.path.basename(f), reverse=True)
                    for filename in files:
                        file = os.path.join(relativeRunDir, filename)
                        outputNode = {}
                        outputNode['name'] = filename
                        outputNode['type'] = "commandOutputFile"
                        outputNode['href'] = file
                        outputNode['children'] = []
                        targetNode['children'].append(outputNode)
                commandNode['children'].append(targetNode)
                
            if isinstance(command, e3_command.MiscCommand):
                commandNode = {}
                commandNode['name'] = link['command']
                commandNode['type'] = link['miscCommand']
                commandNode['startTime'] = startTime
                commandNode['endTime'] = endTime
                commandNode['runTime'] = runTime
                commandNode['children'] = []
                lastTapNode['children'].append(commandNode)
                
                targetNode = {}
                targetNode['name'] = link['target']['output']
                commandNode['type'] = link['commandOutput']
                targetNode['children'] = []
                commandNode['children'].append(targetNode)
                
        return self.create_graph(targetDir, "history", "index", {   "title" : ("plain", "e3 history"), 
                                                                    "data" : ("json", data)})
    
        '''for node in jsonData['nodes']:
            tap = TapManager().get_tap_from_id_or_name(node['id'])
            statusMessage = ""
            size = 10
            if tap is not None:
                size = len(tap.articulations)
            if tap is not None and tap.get_status_message() is not None:
                statusMessage = tap.get_status_message()
            name = node['id']
            href = os.path.join(node['id'], "tap.html")
            color = "blue"
            if "/" in name:
                color = "red"
                tapId = node['id'].split("/")[0]
                command = node['id'].split("/")[1]
                href = os.path.join(tapId, "_".join(command.split()), "index.html")
                #if not os.path.isfile(os.path.join(get_working_dir(), href)):
                #    href = ""
                name = node['output']
            newJsonDataNodes.append(
                {
                    'id': node['id'],
                    'name': name,
                    'href': href,
                    'status': statusMessage,
                    'size': size,
                    'color': color
                }
                )'''
        #jsonData['nodes'] = newJsonDataNodes
        
        
        #jsonData['nodes'] = [
        #    {
        #        'id': node['id'],
        #        'name': node['id'],
        #        'href': os.path.join(node['id'], "tap.html"),
        #        'status': TapManager().get_tap_from_id_or_name(node['id']).get_status_message(),
        #        'size': len(TapManager().get_tap_from_id_or_name(node['id']).articulations)
        #    }
        #    for node in jsonData['nodes']]
        
        '''newJsonDataNodes = []
        for node in jsonData['nodes']:
            tap = TapManager().get_tap_from_id_or_name(node['id'])
            statusMessage = ""
            size = 10
            if tap is not None:
                size = len(tap.articulations)
            if tap is not None and tap.get_status_message() is not None:
                statusMessage = tap.get_status_message()
            name = node['id']
            href = os.path.join(node['id'], "tap.html")
            color = "blue"
            if "/" in name:
                color = "red"
                tapId = node['id'].split("/")[0]
                command = node['id'].split("/")[1]
                href = os.path.join(tapId, "_".join(command.split()), "index.html")
                #if not os.path.isfile(os.path.join(get_working_dir(), href)):
                #    href = ""
                name = node['output']
            newJsonDataNodes.append(
                {
                    'id': node['id'],
                    'name': name,
                    'href': href,
                    'status': statusMessage,
                    'size': size,
                    'color': color
                }
                )
        jsonData['nodes'] = newJsonDataNodes
        #jsonData['links'] = [
        #    {
        #        'source': jsonData['nodes'][link['source']]['id'],
        #        'target': jsonData['nodes'][link['target']]['id'],
        #        'command': link['command']
        #    }
        #    for link in jsonData['links']]
        self.create_graph(targetDir, "history", "index", { "data" : ("json", jsonData)})'''
    def create_tap_graph(self, targetDir):
        tap = TapManager().get_current_tap()
        tapName = TapManager().get_tap_name(tap.get_id())
        
                        
        '''               
        #create dataAdjacency
        g = nx.MultiDiGraph()
        i = 0;
        for taxonomy in tap.taxonomies:
            #mapping = {}
            for node in taxonomy.g:
                g.add_node(taxonomy.id + "." + node, group = taxonomy.id) 
                #color = nodeColors[i]
            for edge in taxonomy.g.edges():
                relation = "taxonomy_outgoing." + taxonomy.id
                g.add_edge(taxonomy.id + "." + edge[0], taxonomy.id + "." + edge[1], relation = relation)
                #relation = "taxonomy_incoming." + taxonomy.id
                #g.add_edge(taxonomy.id + "." + edge[1], taxonomy.id + "." + edge[0], relation = relation)
        for articulation in tap.articulations:*/
            #for now only these: how to deal with other type of relations?
            if len(articulation.leftNodes) == 1 and len(articulation.rightNodes) == 1:
                g.add_edge(articulation.leftNodes[0], articulation.rightNodes[0], relation = articulation.relation)
                
                #if articulation.relation  == "equals" or articulation.relation  == "disjoint" or articulation.relation  == "overlaps":
                #    g.add_edge(articulation.rightNodes[0], articulation.leftNodes[0], relation = articulation.relation)
                #if articulation.relation == "includes": 
                #    g.add_edge(articulation.rightNodes[0], articulation.leftNodes[0], relation = "is_included_in")
                #if articulation.relation == "is_included_in": 
                #    g.add_edge(articulation.rightNodes[0], articulation.leftNodes[0], relation = "includes")
        
        jsonData = json_graph.node_link.node_link_data(g)
        
        dataC = []
        for node in g:
            outNeighbors = []
            for successor in g.successors(node):
                outNeighbors.append(successor)
            dataC.append({ 
                "name" : node ,
                "outNeighbors" : outNeighbors
                })
        
        self.create_graph(targetDir, "tap", "tap", {    "data" : ("json", jsonData), 
                                                        "sectionA" : ("plain", svg),
                                                        "dataC" : ("json", dataC),
                                                        "sectionF-textarea" : ("insert", tap.get_cleantax())
                                                    })
        #print jsonData'''
        self.create_graph(targetDir, "tap", "index", { 
                                                    "title" : ("plain", "Tap: " + tapName),
                                                    "cleantax-textarea" : ("insert", tap.get_cleantax()), 
                                                    "visualization" : ("plain", self.create_visualization_data(tap)),
                                                    "dataAdjacency" : ("json", self.create_adjacency_data(tap)),
                                                     })
        
    def create_visualization_data(self, tap):
        import e3_command
        graphTap = e3_command.GraphTap(tap)
        graphTap.run()
        svg = ""
        if graphTap.outputFiles:
            file = graphTap.outputFiles[0]
            with open(file, 'r') as f:
                svgFound = False
                for i, line in enumerate(f):
                    if svgFound or line.strip().startswith("<svg"):
                        svgFound = True
                        svg += line
        return svg
        
    def create_adjacency_data(self, tap):
        g = nx.MultiDiGraph()
        i = 0;
        for taxonomy in tap.taxonomies:
            for node in taxonomy.g:
                g.add_node(taxonomy.id + "." + node, group = taxonomy.id) 
            for edge in taxonomy.g.edges():
                relation = "taxonomy_outgoing." + taxonomy.id
                g.add_edge(taxonomy.id + "." + edge[0], taxonomy.id + "." + edge[1], relation = relation)
                relation = "taxonomy_incoming." + taxonomy.id
                g.add_edge(taxonomy.id + "." + edge[1], taxonomy.id + "." + edge[0], relation = relation)
        for articulation in tap.articulations:
            #for now only these: how to deal with other type of relations?
            if len(articulation.leftNodes) == 1 and len(articulation.rightNodes) == 1:
                g.add_edge(articulation.leftNodes[0], articulation.rightNodes[0], relation = articulation.relation)
                
                if articulation.relation  == "equals" or articulation.relation  == "disjoint" or articulation.relation  == "overlaps":
                    g.add_edge(articulation.rightNodes[0], articulation.leftNodes[0], relation = articulation.relation)
                if articulation.relation == "includes": 
                    g.add_edge(articulation.rightNodes[0], articulation.leftNodes[0], relation = "is_included_in")
                if articulation.relation == "is_included_in": 
                    g.add_edge(articulation.rightNodes[0], articulation.leftNodes[0], relation = "includes")
        
        return json_graph.node_link.node_link_data(g)