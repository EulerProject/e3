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

e3Dir = os.path.join(expanduser("~"), ".e3")

def get_e3_dir():
    if not os.path.isdir(e3Dir):
        os.makedirs(e3Dir)
    return e3Dir

def get_home_dir():
    return expanduser("~")

def clean_e3_dir():
    shutil.rmtree(get_e3_dir())
    
def reset():
    clean_e3_dir()
    ConfigManager().get_config()
    tapManager = TapManager()
    tapManager.load_demo_taps()
    tap = tapManager.get_default_tap()
    tapManager.store_tap(tap)
    tapManager.set_current_tap(tap)
    
def set_git_credencials(host, user, password):
    p = Popen("git config --global user.email \"" + user + "\"", stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = p.communicate()
    
    p = Popen("git config --global user.name \"" + user + "\"", stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = p.communicate()
    
    config = get_config()
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
                else:
                    self.__log.warn("Articulation already exists: " + line)
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
                    
    def get_tap_id_and_name(self, tapId):
        name = self.get_name(tapId)
        return name
        #if name:
        #    return name + " = " + tapId
        #else:
        #    return tapId
    
    def get_tap_id_and_name_and_status(self, tap):
        tap_id_and_name = self.get_tap_id_and_name(tap.get_id())
        status = tap.get_status()
        if status:
            return tap_id_and_name + " (" + status + ")"
        return tap_id_and_name
    
    def get_current_tap(self):
        with open(self.get_current_tap_file(), 'r') as currentTapFile:
            return self.get_tap(currentTapFile.readline())
        
    def set_current_tap(self, tap):
        with open(self.get_current_tap_file(), 'w') as currentTapfile:
            currentTapfile.write(tap.get_id())
    
    def store_tap(self, tap):
        existingName = self.get_name(tap.get_id())
        if existingName is None:
            import e3_name_generator
            randomName = e3_name_generator.get_random_name(None, None)
            names = self.get_names()
            name = randomName
            id = 1
            while name in names:
                name = randomName + "_" + id
                id = id + 1
            self.set_name(name, tap)
        
        tapFile = self.get_tap_file(tap)        
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
        cleantaxFile = self.get_cleantax_file(tap)
        with open(cleantaxFile, 'w') as f:  
            for taxonomy in tap.taxonomies:      
                f.write(taxonomy.__str__())
                f.write('\n\n')
            f.write('articulation\n')
            for articulation in tap.articulations:
                f.write(articulation.__str__() + '\n')

    def get_default_tap(self):
        config = ConfigManager().get_config()
        isCoverage = config['defaultIsCoverage']
        isSiblingDisjointness = config['defaultIsSiblingDisjointness']
        regions = config['defaultRegions']
        import e3_model
        return e3_model.Tap(isCoverage, isSiblingDisjointness, regions, [], [])
            
    def get_tap(self, tapId):
        if not tapId or tapId is None:
            return None
        tapFile = self.get_tap_file_from_id(tapId)
        if not os.path.isfile(tapFile):
            tap = self.get_default_tap()
            self.store_tap(tap)
            return tap
        
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
    
    def get_tap_file_from_id(self, tapId):
        tap_file = os.path.join(self.get_tap_dir(tapId), ".tap")
        #if not os.path.isfile(tap_file):
        #    with open(tap_file, 'w') as f:
        #        pass
        return tap_file
    
    def get_tap_file(self, tap):
        return self.get_tap_file_from_id(tap.get_id())
    
    def get_cleantax_file(self, tap):
        tap_id_and_name = self.get_tap_id_and_name(tap.get_id()).replace(" ", "")
        cleantax_file = os.path.join(self.get_taps_dir(), tap_id_and_name, ".cleantax")
        if not os.path.isfile(cleantax_file):
            with open(cleantax_file, 'w') as f:
                pass
        return cleantax_file
    
    def get_0_input_dir(self, tap):
        return os.path.join(self.get_taps_dir(), self.get_tap_id_and_name(tap.get_id()).replace(" ", ""), "0-Input")
    
    def get_1_asp_input_dir(self, tap):
        return os.path.join(self.get_taps_dir(), self.get_tap_id_and_name(tap.get_id()).replace(" ", ""), "1-ASP-input-code")
    
    def get_2_asp_output_dir(self, tap):
        return os.path.join(self.get_taps_dir(), self.get_tap_id_and_name(tap.get_id()).replace(" ", ""), "2-ASP-output")
    
    def get_3_mir_dir(self, tap):
        return os.path.join(self.get_taps_dir(), self.get_tap_id_and_name(tap.get_id()).replace(" ", ""), "3-MIR")
    
    def get_4_pws_dir(self, tap):
        return os.path.join(self.get_taps_dir(), self.get_tap_id_and_name(tap.get_id()).replace(" ", ""), "4-PWs")
    
    def get_5_aggregates_dir(self, tap):
        return os.path.join(self.get_taps_dir(), self.get_tap_id_and_name(tap.get_id()).replace(" ", ""), "5-Aggregates")
    
    def get_6_lattices_dir(self, tap):
        return os.path.join(self.get_taps_dir(), self.get_tap_id_and_name(tap.get_id()).replace(" ", ""), "6-Lattices")
    
    def get_tap_dir(self, tapId):
        tap_id_and_name = self.get_tap_id_and_name(tapId).replace(" ", "")
        tap_dir = os.path.join(get_e3_dir(), "taps", tap_id_and_name)
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
    
    def set_name(self, name, tap):
        import yaml
        oldName = self.get_name(tap.get_id())
        oldTapDir = None
        if oldName is not None:
            oldTapDir = self.get_tap_dir(tap.get_id())
        names = { }
        with open(self.get_names_file(), "r") as namesFile:
            doc = yaml.load(namesFile)
            if doc:
                for key, value in doc.iteritems():
                    names[key] = value
        if oldName in names:
            del names[oldName]
        names[name] = tap.get_id()
        with open(self.get_names_file(), "w") as namesFile:
            yaml.dump(names, namesFile, default_flow_style=False)
        if oldTapDir is not None:
            for filename in os.listdir(oldTapDir):
                shutil.move(os.path.join(oldTapDir, filename), self.get_tap_dir(tap.get_id()))
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
        
    def get_tap_from_name(self, name):
        id = self.get_tap_id(name)
        if id:
            return self.get_tap(id)
        return None
    
    def get_tap_from_id_or_name(self, name_or_id):
        tap = self.get_tap_from_name(name_or_id)
        if not tap:
            tap = self.get_tap(name_or_id)
        if not tap:
            return None
        else:
            return tap
        
    def get_tap_id(self, name):
        import yaml
        name = name.strip()
        with open(self.get_names_file(), 'r') as namesFile:
            doc = yaml.load(namesFile)
            if doc:
                if name in doc:
                    return doc[name]
        return None
    
    def get_name(self, id):
        import yaml
        with open(self.get_names_file(), 'r') as namesFile:
            doc = yaml.load(namesFile)
            if doc:
                for key, value in doc.items():
                    if value == id:
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
                    'maxPossibleWorldsToShow': 5,
                    'imageFormat': 'svg',
                    'repairMethod': 'topdown',
                    'defaultIsCoverage': True,
                    'defaultIsSiblingDisjointness': True,
                    'defaultRegions': 'mnpw',
                    'reasoner': 'dlv',
                    'gitRepository': "https://github.com/rodenhausen/my_e3_env.git",
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