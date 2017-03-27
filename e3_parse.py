'''
Created on Nov 22, 2016

@author: Thomas
'''
from autologging import logged
from pinject import copy_args_to_public_fields
import e3_command

@logged
class CommandParser(object):
    @copy_args_to_public_fields
    def __init__(self, pattern):
        import re
        import e3_io
        self.re = re.compile(pattern, re.IGNORECASE)
        self.tapManager = e3_io.TapManager()
        pass
    def is_input(self, input):
        return self.re.match(input)
    def get_command(self, input):
        pass
    def get_help(self):
        pass

@logged
class ResetParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^reset$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.Reset()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "reset\nResets to factory settings."
    
@logged
class ClearParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^clear$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.Clear()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "clear\nClears the history and cache. Keeps the config."

@logged
class ResetConfigParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^reset config$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.ResetConfig()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "reset config\nResets the configuration to default."

@logged
class ResetStyleParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^reset style$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.ResetStyle()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "reset style\nResets the style to default."
    
@logged
class ClearHistoryParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^clear history$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.ClearHistory()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "clear history\nClears the history."
@logged               
class ByeParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^(?:bye|exit|quit)$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.Bye()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "bye\nExit e3."
    
@logged               
class HelpParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^help$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.Help()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "help\nShows this help."
    
@logged               
class GitPullParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^git pull (?P<path>.+)$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.GitPull(match.group("path"))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "git pull <path>\nClones or pulls an e3_data workspace from the <path> at the configured git repository."

@logged               
class GitStatePullParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^git state pull (?P<path>.+)')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.GitStatePull(match.group("path"))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "git state pull <path>\nClones or pulls the e3 state from the ptah at the configured git repository."
    
@logged
class ShowHistoryParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^show history$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.ShowHistory()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "show history\nShows the html rendered history."

@logged               
class SetGitCredentialsParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^git credentials (.+) (.+) "(.*)"$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.SetGitCredentials(match.group(1), match.group(2), match.group(3))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "git credentials <host> <username> \"<password>\"\nSets the <username> and <password> for the git <host>."

@logged               
class GitPushParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^git push (?P<path>.+)(?: (?P<message>.*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            if match.group("message"):
                return e3_command.GitPush(match.group("path"), match.group("message"))
            else:
                return e3_command.GitPush(match.group("path"), "e3 git push") 
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "git push <path> <message>\nCommits (with <message>) and pushes the e3_data workspace to the <path> at the configured git repository."

@logged               
class GitStatePushParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^git state push (?P<path>.+)(?: (?P<message>.*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            if match.group("message"):
                return e3_command.GitStatePush(match.group("path"), match.group("message"))
            else:
                return e3_command.GitStatePush(match.group("path"), "e3 git state push") 
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "git state push <path> <message>\nCommits (with <message>) and pushes the e3 state to the path at the configured git repository."

class LoadTapParser(CommandParser):
    def __init__(self):
        #example:
        #load tap abstract.txt
        CommandParser.__init__(self, '^load tap (\S*)$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.LoadTap(match.group(1))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "load tap <cleantax file>\nLoads a tap from a cleantax file."

class ClearTapParser(CommandParser):
    def __init__(self):
        #example:
        #load tap abstract.txt
        CommandParser.__init__(self, '^clear tap$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.ClearTap()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "clear tap\nSets the empty tap as the current tap."
    
class RenameConceptParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^rename concept (?P<taxonomyId>.+) (?P<oldName>.+) (?P<newName>.+)(?: (?P<tap>\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group("tap"):
                tap = self.tapManager.get_tap_from_id_or_name(match.group("tap"))  
            if tap:   
                return e3_command.RenameConcept(tap, match.group("taxonomyId"), match.group("oldName"), match.group("newName"))
            else:
                raise Exception('Tap %s not found' % match.group("tap"))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "rename concept <taxonomyId> <oldName> <newName> [<tap>]\nRenames the concept in taxonomy with <taxonomyId> from <oldName> to <newName> for the current tap, or the optionally provided <tap>."
    
class AddConceptsParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^add concepts (.+) (\\(.+\\))( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(3) and match.group(4):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(4))  
            if tap:   
                return e3_command.AddConcepts(tap, match.group(1), match.group(2))
            else:
                raise Exception('Tap %s not found' % match.group(4))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "add concepts <taxonomyId> (<parentConcepts> <childConcept 1> ... <childConcept n>) [<tap>]\nAdds set of <childConcept> to <parentConcept>, creating non-existing concept's as needed to the taxonomy with <taxonomyId> of the current tap, or the optionally provided <tap>."

class RemoveConceptsParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^remove concepts(?: recursive)? (.+) (\\(.+\\))( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        recursive = input.startswith("remove concepts recursive")
        if match:
            tap = self.tapManager.get_current_tap()        
            if match.group(3) and match.group(4):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(4))  
            if tap:   
                return e3_command.RemoveConcepts(tap, match.group(1), match.group(2), recursive)
            else:
                raise Exception('Tap %s not found' % match.group(4))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "remove concepts <recursive> <taxonomyId> (<parentConcepts> <childConcept 1> ... <childConcept n>) [<tap>]\nRemoves set of <childConcept> from <parentConcept> in the taxonomy with <taxonomyId> of the current tap, or the optionally provided <tap>."
    
class AddTaxonomyParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^add taxonomy (.+) (.+)( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(3) and match.group(4):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(4))  
            if tap:   
                return e3_command.AddTaxonomy(tap, match.group(1), match.group(2))
            else:
                raise Exception('Tap %s not found' % match.group(4))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "add taxonomy <taxonomyId> <taxonomyName> [<tap>]\nAdds a taxonomy with <taxonomyId> and <taxonomyName> to the current tap, or the optionally provided <tap>."

class RemoveTaxonomyParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^remove taxonomy (.+)( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(2) and match.group(3):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(3))  
            if tap:   
                return e3_command.RemoveTaxonomy(tap, match.group(1))
            else:
                raise Exception('Tap %s not found' % match.group(3))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "remove taxonomy <taxonomyId> [<tap>]\nRemoves the taxonomy with <taxonomyId> and all referencing articulations from the current tap, or the optionally provided <tap>."

class ClearTaxonomyParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^clear taxonomy (.+)( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(2) and match.group(3):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(3))  
            if tap:   
                return e3_command.ClearTaxonomy(tap, match.group(1))
            else:
                raise Exception('Tap %s not found' % match.group(3))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "clear taxonomy <taxonomyId> [<tap>]\nClears the taxonomy with <taxonomyId> of the current tap, or the optionally provided <tap>."

class ClearArticulationsParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^clear articulations( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(1) and match.group(2):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(2))  
            if tap:   
                return e3_command.ClearArticulations(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "clear articulations [<tap>]\nClears the articulations of the current tap, or the optionally provided <tap>."

class SetTaxonomyInfoParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^set taxonomy info (.+) (.+) (.+)( (\S*))?$$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(4) and match.group(5):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(5))  
            if tap:
                return e3_command.SetTaxonomyInfo(tap, match.group(1), match.group(2), match.group(3))
            else:
                raise Exception('Tap %s not found' % match.group(5))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "set taxonomy info <oldTaxonomyId> <newTaxonomyId> <newTaxonomyName> [<tap>]\nSets the <newTaxonomyid> and <newTaxonomyName> to the taxonomy with <oldTaxonomyId> of the current tap, or the optionally provided <tap>."
    
class AddArticulationParser(CommandParser):
    def __init__(self):
        #example: 
        #add articulation [1.A equals 2.B]
        #add articulation [1.A equals 2.B] 2312842819299391
        #add articulation [1.A equals 2.B] my_tap_name
        CommandParser.__init__(self, '^add articulation (.+)( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(2) and match.group(3):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(3))  
            if tap:          
                return e3_command.AddArticulation(tap, match.group(1))
            else:
                raise Exception('Tap %s not found' % match.group(3))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "add articulation <articulation> [<tap>]\nAdds <articulation> to the current tap, or the optionally provided <tap>."

class RemoveArticulationParser(CommandParser):
    def __init__(self):
        #example: 
        #remove articulation 1
        #remove articulation 1 2312842819299391
        #remove articulation 1 my_tap_name
        CommandParser.__init__(self, '^remove articulation (?P<articulation>.+)(?: (?P<tap>\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group("tap"):
                tap = self.tapManager.get_tap_from_id_or_name(match.group("tap"))
            if tap:
                try:
                    articulationIndex = int(match.group("articulation"))
                    return e3_command.RemoveArticulationByIndex(tap, articulationIndex) 
                except ValueError as e:
                    return e3_command.RemoveArticulation(tap, match.group("articulation"))
            else:
                raise Exception('Tap %s not found' % match.group(3))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "remove articulation <articulation_index|articulation> [<tap>]\nRemoves articulation with index <articulation_index> or string <articulation> from the current tap, or the optionally provided <tap>."
        
class SetCoverageParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^set coverage (\S+)( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(2) and match.group(3):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(3))
            if tap:
                value = match.group(1)
                return e3_command.SetCoverage(tap, True if not (value == 'false' or value == 'False') else False)
            else:
                raise Exception('Tap %s not found' % match.group(3))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "set coverage <true|false> [<tap>]\nSets the coverage for the current tap, or the optionally provided <tap>."

class SetConfigParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^set config (\S+)\s*=\s*(.*)$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.SetConfig(match.group(1), match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "set config <parameter>=<value>\nSets the configuration <parameter> with <value>."
    
class SetStyleParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^set style (\S+)\s*=\s*(.*)$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.SetStyle(match.group(1), match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "set style <parameterPath>=<value>\nSets the style parameter with <parameterPath> (e.g. aggregate/graphstyle/legend) with <value>."

class PrintConfigParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^print config$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.PrintConfig()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "print config\nPrints the configuration settings."

class PrintStyleParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^print style$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.PrintStyle()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "print style\nPrints the style settings."

class SetSiblingDisjointnessParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^set sibling disjointness (\S+)( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(2) and match.group(3):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(3))
            if tap:
                value = match.group(1)
                return e3_command.SetSiblingDisjointness(tap, True if not (value == 'false' or value == 'False') else False)
            else:
                raise Exception('Tap %s not found' % match.group(3))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "set sibling disjointness <true|false> [<tap>]\nSets the sibling disjointness for the current tap, or the optionally provided <tap>."

class SetRegionsParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^set regions (\S+)( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(2) and match.group(3):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(3))
            if tap:
                return e3_command.SetRegions(tap, match.group(1))
            else:
                raise Exception('Tap %s not found' % match.group(3))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "set regions <mnpw|mncb|mnve|vrpw|vrve> [<tap>]\nSets the regions for the current tap, or the optionally provided <tap>."


class NameTapParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^name tap (\S*)( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input);
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(2) and match.group(3):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(3))
            if tap:
                return e3_command.NameTap(tap, match.group(1))
            else:
                raise Exception('Tap %s not found' % match.group(3))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "name tap <name> [<tap>]\nNames the current tap, or the optionally provided <tap> as <name>."

class PrintNamesParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^print names$')
    def get_command(self, input):
        match = self.is_input(input);
        if match:
            return e3_command.PrintNames()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "print names\nShows all stored names and their corresponding taps."
    
class UseTapParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^use tap (\S+)$')
    def get_command(self, input):
        match = self.is_input(input);
        if match:
            tap = self.tapManager.get_tap_from_id_or_name(match.group(1))
            if tap:
                return e3_command.UseTap(tap)
            else:
                raise Exception('Tap %s not found' % match.group(1))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "use tap <tap>\nMakes <tap> the current tap."
    
class PrintTapParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^print tap( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(1) and match.group(2):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.PrintTap(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "print tap [<tap>]\nPrints the current tap, or the optionally provided <tap>."
        
class PrintTaxonomiesParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^print taxonomies( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(1) and match.group(2):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.PrintTaxonomies(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')   
    def get_help(self):
        return "print taxonomies [<tap>]\nPrints the taxonomies of the current tap, or the optionally provided <tap>."
         
class PrintArticulationsParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^print articulations( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)    
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(1) and match.group(2):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.PrintArticulations(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "print articulations [<tap>]\nPrints the articulations of the current tap, or the optionally provided <tap>."

class MoreWorldsThanParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^more than (\d+) worlds( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(2) and match.group(3):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(3))
            if tap:
                return e3_command.MoreWorldsThan(tap, int(match.group(1)))
            else:
                raise Exception('Tap %s not found' % match.group(3))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "more than <count> worlds [<tap>]\nChecks if there are more than <count> number of worlds in the current tap, or the optionally provided <tap>."

class IsAmbiguousParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^is ambiguous( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(1) and match.group(2):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.IsAmbiguous(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "is ambiguous [<tap>]\nChecks if there is more than 1 world for the current tap, or the optionally provided <tap>."

class IsUniqueParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^is unique( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(1) and match.group(2):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.IsUnique(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "is unique [<tap>]\nChecks if there is a unique world for the current tap, or the optionally provided <tap>."

class GraphWorldsParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^graph worlds( (?P<maxWorlds>\d+))?( (?P<tap>\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group("tap"):
                tap = self.tapManager.get_tap_from_id_or_name(match.group("tap"))
            if tap:
                maxWorlds = None
                if match.group("maxWorlds"):
                    maxWorlds = int(match.group("maxWorlds"))
                return e3_command.GraphWorlds(tap, maxWorlds)
            else:
                raise Exception('Tap %s not found' % match.group("tap"))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "graph worlds [<maxWorlds>] [<tap>]\nCreates graph visualizations of the worlds, if any exist, and if provided maximally <maxWorlds> for the current tap, or the optionally provided <tap>."

class GraphTapParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^graph tap( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(1) and match.group(2):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.GraphTap(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "graph tap [<tap>]\nCreates a graph visualization of the current tap, or the optionally provided <tap>."
    
class GraphFourInOneParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^graph four in one( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(1) and match.group(2):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.GraphFourInOne(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "graph four in one [<tap>]\nCreates a four-in-one visualization of the current tap, or the optionally provided <tap>."
    
class GraphSummaryParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^graph summary( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(1) and match.group(2):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.GraphSummary(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "graph summary [<tap>]\nCreates a summary visualization of the current tap, or the optionally provided <tap>."
        
class GraphAmbiguityParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^graph ambiguity( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(1) and match.group(2):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.GraphAmbiguity(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "graph ambiguity [<tap>]\nCreates an ambiguity visualization of the current tap, or the optionally provided <tap>."
        
class IsConsistentParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^is consistent( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(1) and match.group(2):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.IsConsistent(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "is consistent [<tap>]\nChecks the consistency of the current tap, or the optionally provided <tap>."
                             
class PrintWorldsParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^print worlds( (?P<maxWorlds>\d+))?( (?P<tap>\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group("tap"):
                tap = self.tapManager.get_tap_from_id_or_name(match.group("tap"))
            if tap:
                maxWorlds = None
                if match.group("maxWorlds"):
                    maxWorlds = int(match.group("maxWorlds"))
                return e3_command.PrintWorlds(tap, maxWorlds)
            else:
                raise Exception('Tap %s not found' % match.group("tap"))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "print worlds [<maxWorlds>] [<tap>]\nPrints the worlds, if any exist, and if provided maximally <maxWorlds> for the current tap, or the optionally provided <tap>."
        
class GraphInconsistencyParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^graph\s+(?:(?P<type>full|reduced)\s+)?inconsistency( (?P<tap>\S+))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            type = match.group("type")
            tapName = match.group("tap")
            if tapName:
                tap = self.tapManager.get_tap_from_id_or_name(tapName)
            if tap:
                return e3_command.GraphInconsistency(tap, type)
            else:
                raise Exception('Tap %s not found' % match.group("tap"))
        else:
            raise Exception('Unrecognized command line')   
    def get_help(self):
        return "graph [<full|reduced>] inconsistency [<tap>]\nCreates a graph visualization of the inconsistency, if any exists, for the current tap, or the optionally provided <tap>."
    
class PrintFixParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^print fix( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(1) and match.group(2):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.PrintFix(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "print fix [<tap>]\nPrints a suggested fix of the inconsistency, if any exists, for the current tap, or the optionally provided <tap>."
     
class PrintMinimalArticulationsParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^print minimal articulations( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(1) and match.group(2):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.PrintMinimalArticulations(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "print minimal articulations [<tap>]\nPrints minimal sets articulations for the unique world of the current tap, or the optionally provided <tap>."

class UseMinimalArticulationsParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^use minimal articulations (?P<minimalArticulationSetId>\d+)( (?P<tap>\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group("tap"):
                tap = self.tapManager.get_tap_from_id_or_name(match.group("tap"))
            if tap:
                minimalArticulationSetId = int(match.group("minimalArticulationSetId"))
                return e3_command.UseMinimalArticulations(tap, minimalArticulationSetId)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "use minimal articulations <minimal articulation set id> [<tap>]\nReplaces the articulations of the current tap or the optionally provided <tap> with the articulations of the given <minimal articulation set id>."

class UseMinimalUniquenessParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^use minimal uniqueness (?P<setId>\d+)( (?P<tap>\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group("tap"):
                tap = self.tapManager.get_tap_from_id_or_name(match.group("tap"))
            if tap:
                setId = int(match.group("setId"))
                return e3_command.UseMinimalUniqueness(tap, setId)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "use minimal uniqueness <set id> [<tap>]\nReplaces the articulations of the current tap or the optionally provided <tap> with the articulations of the given minimal uniqueness <set id>."

class UseMinimalInconsistencyParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^use minimal inconsistency (?P<setId>\d+)( (?P<tap>\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group("tap"):
                tap = self.tapManager.get_tap_from_id_or_name(match.group("tap"))
            if tap:
                setId = int(match.group("setId"))
                return e3_command.UseMinimalInconsistency(tap, setId)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "use minimal inconsistency <set id> [<tap>]\nReplaces the articulations of the current tap or the optionally provided <tap> with the articulations of the given minimal inconsistency <set id>."

class UseMaximalConsistencyParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^use maximal consistency (?P<setId>\d+)( (?P<tap>\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group("tap"):
                tap = self.tapManager.get_tap_from_id_or_name(match.group("tap"))
            if tap:
                setId = int(match.group("setId"))
                return e3_command.UseMaximalConsistency(tap, setId)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "use maximal consistency <set id> [<tap>]\nReplaces the articulations of the current tap or the optionally provided <tap> with the articulations of the given maximal consistency <set id>."

class UseMaximalAmbiguityParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^use maximal ambiguity (?P<setId>\d+)( (?P<tap>\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group("tap"):
                tap = self.tapManager.get_tap_from_id_or_name(match.group("tap"))
            if tap:
                setId = int(match.group("setId"))
                return e3_command.UseMaximalAmbiguity(tap, setId)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "use maximal ambiguity <set id> [<tap>]\nReplaces the articulations of the current tap or the optionally provided <tap> with the articulations of the given maximal ambiguity <set id>."

class UseMaximalArticulationsParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^use maximal articulations (?P<maximalArticulationSetId>\d+)( (?P<tap>\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group("tap"):
                tap = self.tapManager.get_tap_from_id_or_name(match.group("tap"))
            if tap:
                maximalArticulationSetId = int(match.group("maximalArticulationSetId"))
                return e3_command.UseMaximalArticulations(tap, maximalArticulationSetId)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "use maximal articulations <maximal articulation set id> [<tap>]\nReplaces the articulations of the current tap or the optionally provided <tap> with the articulations of the given <maximal articulation set id>."

class UseWorldParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^use world( (?P<worldId>\d+))?( (?P<tap>\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group("tap"):
                tap = self.tapManager.get_tap_from_id_or_name(match.group("tap"))
            if tap:
                worldId = int(match.group("worldId"))
                return e3_command.UseWorld(tap, worldId)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "use world [<worldId>] [<tap>]\nReplaces the articulations of the current tap or the optionally provided <tap> with all the articulations extracted from the given <worldId> or the unique world of the tap, if applicable and no <worldId> is given."

class CreateTapFromWorldsParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^create tap from worlds(?: (.*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            taps = []
            match
            for tapId in match.group(1).split():
                tap = self.tapManager.get_tap_from_id_or_name(tapId)
                if not tap:
                    raise Exception('Tap %s not found' % tapId)
                taps.append(tap)
            return e3_command.CreateTapFromWorlds(taps)
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "create tap from worlds <tap_1> ... <tap_n> \nCreates a tap with the unique worlds of <tap_1> ... <tap_n> as taxonomies."

class PrintMaximalArticulationsParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^print maximal articulations( (?P<tap>\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group("tap"):
                tap = self.tapManager.get_tap_from_id_or_name(match.group("tap"))
            if tap:
                return e3_command.PrintMaximalArticulations(tap)
            else:
                raise Exception('Tap %s not found' % match.group("tap"))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "print maximal articulations [<tap>]\nPrints maximal sets of articulations for all worlds of the current tap, or the optionally provided <tap>."
    
class PrintMinimalUniquenessParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^print minimal uniqueness( (?P<tap>\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group("tap"):
                tap = self.tapManager.get_tap_from_id_or_name(match.group("tap"))
            if tap:
                return e3_command.PrintMinimalUniqueness(tap)
            else:
                raise Exception('Tap %s not found' % match.group("tap"))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "print minimal uniqueness [<tap>]\nPrints the minimal subsets of articulations that create uniqueness for the current tap, or the optionally provided <tap>."
        
class PrintMinimalInconsistencyParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^print minimal inconsistency( (?P<tap>\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group("tap"):
                tap = self.tapManager.get_tap_from_id_or_name(match.group("tap"))
            if tap:
                return e3_command.PrintMinimalInconsistency(tap)
            else:
                raise Exception('Tap %s not found' % match.group("tap"))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "print minimal inconsistency [<tap>]\nPrints the minimal subsets of articulations that create inconsistency for the current tap, or the optionally provided <tap>."

class PrintMaximalConsistencyParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^print maximal consistency( (?P<tap>\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group("tap"):
                tap = self.tapManager.get_tap_from_id_or_name(match.group("tap"))
            if tap:
                return e3_command.PrintMaximalConsistency(tap)
            else:
                raise Exception('Tap %s not found' % match.group("tap"))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "print maximal consistency [<tap>]\nPrints the maximal subsets of articulations that create consistency for the current tap, or the optionally provided <tap>."

class PrintMaximalAmbiguityParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^print maximal ambiguity( (?P<tap>\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group("tap"):
                tap = self.tapManager.get_tap_from_id_or_name(match.group("tap"))
            if tap:
                return e3_command.PrintMaximalAmbiguity(tap)
            else:
                raise Exception('Tap %s not found' % match.group("tap"))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "print maximal ambiguity [<tap>]\nPrints the maximal subsets of articulations that create ambiguity for the current tap, or the optionally provided <tap>."

class UseFixParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^use fix (?P<setId>\d+)( (?P<tap>\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group("tap"):
                tap = self.tapManager.get_tap_from_id_or_name(match.group("tap"))
            if tap:
                setId = int(match.group("setId"))
                return e3_command.UseFix(tap, setId)
            else:
                raise Exception('Tap %s not found' % match.group("tap"))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "use fix <fix set id> [<tap>]\nUses the fix with <fix set id> to create a consistent input from the current tap, or the optionally provided <tap>."

class IsTrueParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^is true\s+(?P<articulation>.+)( (?P<tap>\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group("tap"):
                tap = self.tapManager.get_tap_from_id_or_name(match.group("tap"))
            if tap:
                articulation = match.group("articulation")
                return e3_command.IsTrue(tap, articulation)
            else:
                raise Exception('Tap %s not found' % match.group("tap"))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "is true <articulation> [<tap>]\nChecks if the articulation holds true for the current tap, or the optionally provided <tap>."

commandParsers = [  ByeParser(),
                    HelpParser(), 
                    ResetParser(),
                    ClearParser(),
                    ResetConfigParser(),
                    ResetStyleParser(),
                    ClearHistoryParser(),
                    SetConfigParser(),
                    SetStyleParser(),
                    PrintConfigParser(),
                    PrintStyleParser(),
                    LoadTapParser(),
                    ClearTapParser(),
                    PrintTapParser(),
                    PrintTaxonomiesParser(),
                    PrintArticulationsParser(),
                    AddTaxonomyParser(),
                    RemoveTaxonomyParser(),
                    SetTaxonomyInfoParser(),
                    RenameConceptParser(),
                    AddConceptsParser(),
                    RemoveConceptsParser(),
                    ClearTaxonomyParser(),
                    AddArticulationParser(),
                    RemoveArticulationParser(),
                    ClearArticulationsParser(),
                    SetSiblingDisjointnessParser(),
                    SetCoverageParser(),
                    SetRegionsParser(),
                    NameTapParser(),
                    PrintNamesParser(),
                    UseTapParser(), 
                    GraphTapParser(), 
                    IsConsistentParser(),
                    IsAmbiguousParser(),
                    IsUniqueParser(),
                    MoreWorldsThanParser(),
                    GraphWorldsParser(), 
                    PrintWorldsParser(),
                    GraphSummaryParser(),
                    GraphFourInOneParser(),
                    GraphInconsistencyParser(),
                    GraphAmbiguityParser(),
                    PrintFixParser(),
                    PrintMinimalArticulationsParser(),
                    UseMinimalArticulationsParser(),
                    PrintMaximalArticulationsParser(),
                    UseMaximalArticulationsParser(),
                    UseWorldParser(),
                    CreateTapFromWorldsParser(),
                    PrintMinimalUniquenessParser(),
                    UseMinimalUniquenessParser(),
                    PrintMinimalInconsistencyParser(),
                    UseMinimalInconsistencyParser(),
                    PrintMaximalConsistencyParser(),
                    UseMaximalConsistencyParser(),
                    PrintMaximalAmbiguityParser(),
                    UseMaximalAmbiguityParser(),
                    UseFixParser(),
                    IsTrueParser(),
                    GitPullParser(),
                    GitPushParser(),
                    GitStatePullParser(),
                    GitStatePushParser(),
                    SetGitCredentialsParser(),
                    ShowHistoryParser()
                ]

class CommandProvider(object):
    def __init__(self):
        #self.commands = Command.__subclasses__()#
        pass
    def provide(self, input):
        for parser in commandParsers:
            if parser.is_input(input):
               return parser.get_command(input)