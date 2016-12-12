'''
Created on Nov 22, 2016

@author: Thomas
'''
import yaml
import os.path
import e3_model
import e3_command
import e3_validation
from os.path import expanduser
import shutil
import uuid

def reset():
    shutil.rmtree(get_e3_dir())
    get_config()

def get_config():
    config = None
    with open(get_config_file(), 'r') as f:
        config = yaml.safe_load(f)
        if(config):
            return config
    defaultConfig = {
                'euler2Executable': 'euler2', #os.path.join(get_home_dir(), 'git', 'EulerX'),
                'imageViewer': 'xdg-open {file}',
                'maxPossibleWorldsToShow': '5',
                'imageFormat': 'svg',
                'repairMethod': 'topdown',
                'defaultIsCoverage': 'True',
                'defaultIsSiblingDisjointness': 'True',
                'defaultRegions': 'mnpw',
                'reasoner': 'dlv'
                }
    config = defaultConfig
    with open(get_config_file(), 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    return config

def exists_config(key):
    return key in get_config()


def set_config(key, value):
    config = get_config()
    config[key] = value
    with open(get_config_file(), 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

def set_name(name, tap):
    names = { }
    with open(get_names_file(), "r+") as namesFile:
        doc = yaml.load(namesFile)
        if doc:
            for key, value in doc.iteritems():
                names[key] = value
        names[name] = tap.get_id()
        yaml.dump(names, namesFile, default_flow_style=False)

def get_names():
    names = []
    with open(get_names_file(), 'r') as namesFile:
        doc = yaml.load(namesFile)
        if doc:
            for key, value in doc.items():
                names.append(key + " = " + value)
    return names       

def clear_names():
    with open(get_names_file(), 'w'): pass

def remove_project(project):
    if exists_project(project):
        shutil.rmtree(get_project_dir(project))

def set_current_project(project):
    with open(get_current_project_file(), 'w') as currentProjectFile:
        if not project:
            pass
        else:
            currentProjectFile.write(project)
            
def get_current_project():
    with open(get_current_project_file(), 'r') as currentProjectFile:
        return currentProjectFile.readline()
    
def set_history(project, history):
    with open(get_history_file(project), 'w') as historyFile:
        historyFile.write(history)
    
def get_projects():
    return os.listdir(get_projects_dir())
    
def clear_projects():
    for project in get_projects():
        remove_project(project)
        
def create_project(project):
    os.makedirs(os.path.join(get_projects_dir(), project));
        
def exists_project(project):
    return os.path.isdir(get_project_dir(project))

def get_tap_id_and_name(tap):
    name = get_tap_name(tap.get_id())
    if name:
        return name + " = " + tap.get_id()
    else:
        return tap.get_id()

def get_current_tap():
    with open(get_current_tap_file(), 'r') as currentTapFile:
        return get_tap(currentTapFile.readline())
        
def set_current_tap(tap):
    with open(get_current_tap_file(), 'w') as currentTapfile:
        currentTapfile.write(tap.get_id())

def store_tap(tap):
    tapFile = get_tap_file(tap)
    with open(tapFile, 'w') as f:
        f.write(str(tap.isCoverage) + '\n')
        f.write(str(tap.isSiblingDisjointness) + '\n')
        f.write(tap.regions + '\n')
        f.write('\n')
        for taxonomy in tap.taxonomies:
            for line in taxonomy:
                f.write(line + '\n')
            f.write('\n')
        for line in tap.articulations:
            f.write(line + '\n')
    store_tap_to_cleantax(tap)

def store_tap_to_cleantax(tap):
    cleantaxFile = get_cleantax_file(tap)
    with open(cleantaxFile, 'w') as f:  
        for taxonomy in tap.taxonomies:      
            for line in taxonomy:
                f.write(line + '\n')
            f.write('\n')
        for line in tap.articulations:
            f.write(line + '\n')
            
def get_tap(tapId):
    tapFile = get_tap_file_from_id(tapId)
    if not os.path.isfile(tapFile):
        return None
    config = get_config()
    cleantax = []
    with open(tapFile, 'r') as f:
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
    return get_tap_from_cleantax(isCoverage, isSiblingDisjointness, regions, cleantax)
      
def get_tap_from_cleantax_file(cleantaxFile):
    config = get_config()
    with open(cleantaxFile, 'r') as f:
        lines = f.readlines()
        return get_tap_from_cleantax(config['defaultIsCoverage'], config['defaultIsSiblingDisjointness'], config['defaultRegions'], lines)
    
      
def get_tap_from_cleantax(isCoverage, isSiblingDisjointness, regions, cleantax):
    e3_validation.validate_cleantax(cleantax)
    taxonomies = get_taxonomies(cleantax)
    articulations = get_articulations(cleantax)
    return e3_model.Tap(isCoverage, isSiblingDisjointness, regions, taxonomies, articulations)

def get_taxonomies(cleantax):
    taxonomies = []
    taxonomy = []
    articulations = []
    taxonomiesComplete = False
    for line in cleantax:
        line = line.rstrip()
        if len(line.strip()) == 0:
            if not taxonomiesComplete and not len(taxonomy) == 0:
                taxonomies.append(taxonomy)
                taxonomy = []
                continue
        
        if line.startswith("articulation"):
            return taxonomies
        if not taxonomiesComplete:
            taxonomy.append(line)
    return taxonomies
    
def get_articulations(cleantax):
    articulations = []
    articulationStarts = False
    for line in cleantax:
        line = line.rstrip()
        if line.startswith("articulation"):
            articulationStarts = True
        if articulationStarts:
            articulations.append(line)
    return articulations

def get_tap_from_name(name):
    id = get_tap_id(name)
    if id:
        return get_tap(id)
    return None

def get_tap_from_id_or_name(name_or_id):
    tap = get_tap_from_name(name_or_id)
    if not tap:
        tap = get_tap(name_or_id)
    if not tap:
        return None
    else:
        return tap

def get_tap_id(name):
    name = name.strip()
    with open(get_names_file(), 'r') as namesFile:
        doc = yaml.load(namesFile)
        if doc:
            if doc[name]:
                return doc[name]
    return None

def get_tap_name(id):
    with open(get_names_file(), 'r') as namesFile:
        doc = yaml.load(namesFile)
        if doc:
            for key, value in doc.items():
                if value == id:
                    return key
    return None

def append_project_history(input, command):
    #if not isinstance(command, e3_command.MiscCommand):
        id = str(uuid.uuid4())
        currentProject = None
        with open(get_current_project_file(), 'r') as currentProjectFile:
            currentProject = currentProjectFile.readline()
        if currentProject:
            with open(get_history_file(currentProject), 'a') as historyFile:
                historyFile.write(id + " " + input + '\n')
            tap = get_current_tap()
            stepDir = os.path.join(get_project_dir(currentProject), id)
            if isinstance(command, e3_command.MiscCommand):
                os.makedirs(stepDir)
            if isinstance(command, e3_command.ModelCommand):
                shutil.copytree(get_tap_dir(tap.get_id()), stepDir)
                pass
            if isinstance(command, e3_command.Euler2Command):
                shutil.copytree(get_tap_dir(tap.get_id()), stepDir)
                pass
            with open(os.path.join(stepDir, '.outputs'), 'w') as f:
                f.write('\n'.join(command.get_output()))
            with open(os.path.join(stepDir, '.command'), 'w') as f:
                f.write(input)

def get_tap_file_from_id(tapId):
    tap_file = os.path.join(get_tap_dir(tapId), ".tap")
    #if not os.path.isfile(tap_file):
    #    with open(tap_file, 'w') as f:
    #        pass
    return tap_file

def get_tap_file(tap):
    return get_tap_file_from_id(tap.get_id())
                    
def get_cleantax_file(tap):
    cleantax_file = os.path.join(get_taps_dir(), tap.get_id(), ".cleantax")
    if not os.path.isfile(cleantax_file):
        with open(cleantax_file, 'w') as f:
            pass
    return cleantax_file

def get_0_input_dir(tap):
    return os.path.join(get_taps_dir(), tap.get_id(), "0-Input")

def get_1_asp_input_dir(tap):
    return os.path.join(get_taps_dir(), tap.get_id(), "1-ASP-input-code")

def get_2_asp_output_dir(tap):
    return os.path.join(get_taps_dir(), tap.get_id(), "2-ASP-output")

def get_3_mir_dir(tap):
    return os.path.join(get_taps_dir(), tap.get_id(), "3-MIR")

def get_4_pws_dir(tap):
    return os.path.join(get_taps_dir(), tap.get_id(), "4-PWs")

def get_5_aggregates_dir(tap):
    return os.path.join(get_taps_dir(), tap.get_id(), "5-Aggregates")

def get_6_lattices_dir(tap):
    return os.path.join(get_taps_dir(), tap.get_id(), "6-Lattices")

def get_current_project_file():
    current_project_file = os.path.join(get_e3_dir(), ".current_project")
    if not os.path.isfile(current_project_file):
        with open(current_project_file, 'w') as f:
            pass
    return current_project_file

def get_history_file(project):
    if exists_project(project):
        history_file = os.path.join(get_project_dir(project), ".history")
        if not os.path.isfile(history_file):
            with open(history_file, 'w') as f:
                pass
        return history_file
    

def get_tap_dir(tapId):
    tap_dir = os.path.join(get_e3_dir(), "taps", tapId)
    if not os.path.isdir(tap_dir):
        os.makedirs(tap_dir)
    return tap_dir

def get_taps_dir():
    taps_dir = os.path.join(get_e3_dir(), "taps")
    if not os.path.isdir(taps_dir):
        os.makedirs(taps_dir)
    return taps_dir

def get_current_tap_file():
    current_tap_file = os.path.join(get_e3_dir(), ".current_tap")
    if not os.path.isfile(current_tap_file):
        with open(current_tap_file, 'w') as f:
            pass
    return current_tap_file
    
def get_names_file():
    names_file = os.path.join(get_e3_dir(), ".names")
    if not os.path.isfile(names_file):
        with open(names_file, 'w') as f:
            pass
    return names_file

def get_config_file():
    config_file = os.path.join(get_e3_dir(), ".config")
    if not os.path.isfile(config_file):
        with open(config_file, 'w+') as f:
            pass
    return config_file

def get_projects_dir():
    projectsDir = os.path.join(get_e3_dir(), "projects")
    if not os.path.isdir(projectsDir):
        os.makedirs(projectsDir)
    return projectsDir

def get_project_dir(project):
    return os.path.join(get_projects_dir(), project)

def get_e3_dir():
    e3Dir = os.path.join(get_home_dir(), ".e3")
    if not os.path.isdir(e3Dir):
        os.makedirs(e3Dir)
    return e3Dir

def get_home_dir():
    return expanduser("~")