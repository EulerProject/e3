'''
Created on Nov 22, 2016

@author: Thomas
'''
from autologging import logged
from pinject import copy_args_to_public_fields
import networkx as nx

@logged
class ValidRelation(object):
    @copy_args_to_public_fields
    def __init__(self, regex, leftCount, rightCount):
        pass
    def __str__(self):
        return self.regex
        
node = "(\S+\.\S+)"
anyRCC5 = "(?:equals|includes|is_included_in|overlaps|disjoint)"
combinedRCC5s = "{\s*(?:" + anyRCC5 + "\s*)+\s*}"
validRelations = [
        ValidRelation("\[\s*" + node + "\s+" + node + "\s+(lsum)\s+" + node + "\s*\]", 2, 1), 
        ValidRelation("\[\s*" + node + "\s+" + node + "\s+" + node + "\s+(l3sum)\s+" + node + "\s*\]", 3, 1),
        ValidRelation("\[\s*" + node + "\s+" + node + "\s+" + node + "\s+" + node + "\s+(l4sum)\s+" + node + "\s*\]", 4, 1),
        ValidRelation("\[\s*" + node + "\s+(rsum)\s+"  + node + "\s+" + node + "\s*\]", 1, 2),
        ValidRelation("\[\s*" + node + "\s+(r3sum)\s+" + node + "\s+" + node + "\s+" + node + "\s*\]", 1, 3),
        ValidRelation("\[\s*" + node + "\s+(r4sum)\s+" + node + "\s+" + node + "\s+" + node + "\s+" + node + "\s*\]", 1, 4),
        ValidRelation("\[\s*" + node + "\s+" + node + "\s+(ldiff)\s+" + node + "\s*\]", 2, 1),
        ValidRelation("\[\s*" + node + "\s+(rdiff)\s+"  + node + "\s+" + node + "\s*\]", 1, 2),
        ValidRelation("\[\s*" + node + "\s+" + node + "\s+(e4sum)\s+"  + node + "\s+" + node + "\s*\]", 2, 2),
        ValidRelation("\[\s*" + node + "\s+" + node + "\s+(i4sum)\s+"  + node + "\s+" + node + "\s*\]", 2, 2),
        ValidRelation("\[\s*" + node + "\s+(equals)\s+" + node + "\s*\]", 1, 1),
        ValidRelation("\[\s*" + node + "\s+(includes)\s+" + node + "\s*\]", 1, 1),
        ValidRelation("\[\s*" + node + "\s+(is_included_in)\s+" + node + "\s*\]", 1, 1),
        ValidRelation("\[\s*" + node + "\s+(overlaps)\s+" + node + "\s*\]", 1, 1),
        ValidRelation("\[\s*" + node + "\s+(disjoint)\s+" + node + "\s*\]", 1, 1),
        ValidRelation("\[\s*" + node + "\s+(" + combinedRCC5s + ")\s+"+ node + "\s*\]", 1, 1)
    ]

@logged
class ModelValidator(object):
    def is_valid_new_articulation(self, newArticulation, tap):
        for a in tap.articulations:
            if a.leftNodes == newArticulation.leftNodes and a.rightNodes == newArticulation.rightNodes and a.relation == newArticulation.relation:
                self.__log.warn("This articulation already exists: " + newArticulation.__str__())
                return False
        return True
    def is_dag(self, taxonomy):
        if taxonomy.g.number_of_nodes() == 0:
            return False
        return nx.is_directed_acyclic_graph(taxonomy.g)
    def is_tree(self, taxonomy):
        #nx returns exception if graph empty
        if taxonomy.g.number_of_nodes() == 0:
            return False
        return nx.is_tree(taxonomy.g)

@logged
class CleantaxValidator(object):
    def validate_cleantax(self, cleantax):
        import e3_io
        cleantaxReader = e3_io.CleantaxReader()
        cleantax = cleantaxReader.get_normalized_cleantax(cleantax)
        
        cleantaxTaxonomyLines = cleantaxReader.get_cleantax_taxonomy_lines(cleantax)
        for taxonomy in cleantaxTaxonomyLines:
            self.validate_cleantax_taxonomy(taxonomy)
        
        cleantaxArticulationLines = cleantaxReader.get_cleantax_articulation_lines(cleantax)
        validated_articulations = []
        for articulation in cleantaxArticulationLines[1:]:
            self.validate_cleantax_articulation(articulation, cleantaxTaxonomyLines, validated_articulations)
            validated_articulations.append(articulation)
            
    def validate_cleantax_taxonomy(self, taxonomy):
        if not len(taxonomy[0].split()) == 3:
            raise ValidationException("Taxonomy head must consist of the three parts: taxonomy <id> <name>")
        #what are the validation requirements for a taxonomy in the euler context? one or multiple roots possible?
        #utilize a graph lirary before going ahead with this 
        #only validate syntax for now
        for line in taxonomy[1:]:
            line = line.strip()
            if not line[0] == '(' or not line[-1] == ')':
                 raise ValidationException("Taxonomy line has to start with '(' and end with ')'")
            inside = line[1:-1]
            
    def validate_cleantax_articulation(self, articulation, taxonomies, articulations):  
        if articulation in articulations:
            self.__log.warn("This articulation already exists: " + articulation)
        taxonomyIdToNodes = { }
        for taxonomy in taxonomies:
            id = taxonomy[0].split()[1]
            taxonomyIdToNodes[id] = []
            for line in taxonomy[1:]:
                taxonomyIdToNodes[id].extend(line.strip()[1:-1].split())
        
        import re
        for validRelation in validRelations:
            match = re.match(validRelation.regex, articulation)
            if match:
                valid = True
                leftNodes = list(match.groups())[:validRelation.leftCount]
                relation = list(match.groups())[validRelation.leftCount : validRelation.leftCount + 1][0]
                rightNodes = list(match.groups())[validRelation.leftCount + 1:]
                for node in leftNodes + rightNodes:
                    self.validate_cleantax_node(node, taxonomyIdToNodes)
                return 
        import e3_model
        raise ValidationException("No valid relation found for articulation {articulation}. The set of supported relations is: {validRelations}.".format(
            articulation = articulation,
            validRelations = ', '.join(e3_model.relations)))
            
    def validate_cleantax_node(self, node, taxonomyIdToNodes):
        taxonomyIds = ', '.join(taxonomyIdToNodes.keys())
        taxonomyIdNotFoundText = "{taxonomyId} of {node} not found in the list of taxonomies ({taxonomyIds})"
        nodeNotFoundText = "{nodeName} of {node} not found in the nodes of taxonomy {taxonomyId}"
        
        if not '.' in node:
            raise ValidationException(node + " has an invalid node syntax. The period is missing.")
        if not len(node.split('.')) == 2:
            raise ValidationException(node + " has an invalid node syntax. More than one period contained.")
            
        nodeTaxonomyId = node.split('.')[0]
        nodeName = node.split('.')[1]
        if not nodeTaxonomyId in taxonomyIdToNodes:
            raise ValidationException(taxonomyIdNotFoundText.format(taxonomyId = nodeTaxonomyId, node = node, taxonomyIds = taxonomyIds))
        if not nodeName in taxonomyIdToNodes[nodeTaxonomyId]:
            raise ValidationException(nodeNotFoundText.format(nodeName = nodeName, node = node, taxonomyId = nodeTaxonomyId))

class ValidationException(Exception):
    pass