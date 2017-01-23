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
import e3_name_generator

e3Dir = os.path.join(expanduser("~"), ".e3")

def clean_e3_dir():
    shutil.rmtree(get_e3_dir())
    
def reset():
    clean_e3_dir()
    get_config()
    tap = get_default_tap()
    store_tap(tap)
    set_current_tap(tap)

def set_git_credencials(host, user, password):
    config = get_config()
    netrc_file = os.path.join(get_home_dir(), ".netrc")
    if not os.path.isfile(netrc_file):
        with open(netrc_file, 'w') as f:
            f.write("machine " + host + "\n")
            f.write("login " + user + "\n")
            f.write("password " + password + "\n")

def get_config():
    config = None
    with open(get_config_file(), 'r') as f:
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
    with open(get_config_file(), 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    return config

def store_config(config):
    with open(get_config_file(), 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
        
def set_name(name, tap):
    oldName = get_name(tap.get_id())
    oldTapDir = get_tap_dir(tap.get_id())
    names = { }
    with open(get_names_file(), "r") as namesFile:
        doc = yaml.load(namesFile)
        if doc:
            for key, value in doc.iteritems():
                names[key] = value
    if oldName in names:
        del names[oldName]
    names[name] = tap.get_id()
    with open(get_names_file(), "w") as namesFile:
        yaml.dump(names, namesFile, default_flow_style=False)
    for filename in os.listdir(oldTapDir):
        shutil.move(os.path.join(oldTapDir, filename), get_tap_dir(tap.get_id()))
    shutil.rmtree(oldTapDir)

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

def get_tap_id_and_name(tapId):
    name = get_name(tapId)
    if name:
        return name + " = " + tapId
    else:
        return tapId

def get_tap_id_and_name_and_status(tap):
    tap_id_and_name = get_tap_id_and_name(tap.get_id())
    status = tap.get_status()
    if status:
        return tap_id_and_name + " (" + status + ")"
    return tap_id_and_name

def get_current_tap():
    with open(get_current_tap_file(), 'r') as currentTapFile:
        return get_tap(currentTapFile.readline())
    
def set_current_tap(tap):
    with open(get_current_tap_file(), 'w') as currentTapfile:
        currentTapfile.write(tap.get_id())

def store_tap(tap):
    existingName = get_name(tap.get_id())
    if existingName is None:
        randomName = e3_name_generator.get_random_name(None, None)
        names = get_names()
        name = randomName
        id = 1
        while name in names:
            name = randomName + "_" + id
            id = id + 1
        set_name(name, tap)
    
    tapFile = get_tap_file(tap)        
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
    store_tap_to_cleantax(tap)

def store_tap_to_cleantax(tap):
    cleantaxFile = get_cleantax_file(tap)
    with open(cleantaxFile, 'w') as f:  
        for taxonomy in tap.taxonomies:      
            f.write(taxonomy.__str__())
            f.write('\n\n')
        f.write('articulation\n')
        for articulation in tap.articulations:
            f.write(articulation.__str__() + '\n')

def get_default_tap():
    config = get_config()
    isCoverage = config['defaultIsCoverage']
    isSiblingDisjointness = config['defaultIsSiblingDisjointness']
    regions = config['defaultRegions']
    return e3_model.Tap(isCoverage, isSiblingDisjointness, regions, [], [])
            
def get_tap(tapId):    
    if not tapId or tapId is None:
        tap = get_default_tap()
        store_tap(tap)
        return tap
    tapFile = get_tap_file_from_id(tapId)
    if not os.path.isfile(tapFile):
        tap = get_default_tap()
        store_tap(tap)
        return tap
    
    cleantax = []
    with open(tapFile, 'r') as f:
        config = get_config()
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
    tap = e3_model.Tap(isCoverage, isSiblingDisjointness, regions, [], [])
    
    e3_validation.validate_cleantax(cleantax)
    cleantaxTaxonomyLines = get_cleantax_taxonomy_lines(cleantax)
    taxonomies = []
    for taxonomyLines in cleantaxTaxonomyLines:
        header = taxonomyLines[0]
        taxonomyId = header.split()[1]
        taxonomyName = header.split()[2]
        taxonomy = e3_model.Taxonomy(taxonomyId, taxonomyName)
        for line in taxonomyLines[1:]:
            nodes = line[1:-1].split()
            taxonomy.add_children(nodes[0], nodes[1:])
        tap.add_taxonomy(taxonomy)
    
    cleantaxArticulationLines = get_cleantax_articulation_lines(cleantax)
    articulations = []
    for line in cleantaxArticulationLines[1:]:
        line = line.strip()[1:-1]
        foundRelation = False
        for validRelation in e3_model.relations:
            split = " " + validRelation + " "
            if split in line:
                parts = line.split(split)
                left = parts[0].split()
                right = parts[1].split()
                tap.add_articulation(e3_model.Articulation(left, right, validRelation))
                foundRelation = True
        if not foundRelation:
            raise Exception("Not a valid relation in articulation: " + line)
            
    return tap

def get_cleantax_taxonomy_lines(cleantax):
    taxonomies = []
    taxonomy = []
    articulations = []
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
    
def get_cleantax_articulation_lines(cleantax):
    articulations = []
    articulationStarts = False
    for line in cleantax:
        line = line.strip().rstrip()
        if len(line) == 0 or line.startswith('#'): continue
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
            if name in doc:
                return doc[name]
    return None

def get_name(id):
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
    tap_id_and_name = get_tap_id_and_name(tap.get_id())
    cleantax_file = os.path.join(get_taps_dir(), tap_id_and_name, ".cleantax")
    if not os.path.isfile(cleantax_file):
        with open(cleantax_file, 'w') as f:
            pass
    return cleantax_file

def get_0_input_dir(tap):
    return os.path.join(get_taps_dir(), get_tap_id_and_name(tap.get_id()), "0-Input")

def get_1_asp_input_dir(tap):
    return os.path.join(get_taps_dir(), get_tap_id_and_name(tap.get_id()), "1-ASP-input-code")

def get_2_asp_output_dir(tap):
    return os.path.join(get_taps_dir(), get_tap_id_and_name(tap.get_id()), "2-ASP-output")

def get_3_mir_dir(tap):
    return os.path.join(get_taps_dir(), get_tap_id_and_name(tap.get_id()), "3-MIR")

def get_4_pws_dir(tap):
    return os.path.join(get_taps_dir(), get_tap_id_and_name(tap.get_id()), "4-PWs")

def get_5_aggregates_dir(tap):
    return os.path.join(get_taps_dir(), get_tap_id_and_name(tap.get_id()), "5-Aggregates")

def get_6_lattices_dir(tap):
    return os.path.join(get_taps_dir(), get_tap_id_and_name(tap.get_id()), "6-Lattices")

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
    tap_id_and_name = get_tap_id_and_name(tapId)
    tap_dir = os.path.join(get_e3_dir(), "taps", tap_id_and_name)
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
    namesFile = os.path.join(get_e3_dir(), ".names")
    if not os.path.isfile(namesFile):
        with open(namesFile, 'w') as f:
            pass
    return namesFile

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
    if not os.path.isdir(e3Dir):
        os.makedirs(e3Dir)
    return e3Dir

def get_home_dir():
    return expanduser("~")    