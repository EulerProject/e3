'''
Created on Nov 22, 2016

@author: Thomas
'''
import e3_io
import re

validRelations = [ "lsum", "l3sum", "l4sum", "rsum", "r3sum", "r4sum", "ldiff", "rdiff", "e4sum", "i4sum", "equals", "includes", 
                      "is_included_in", "overlaps", "disjoint" 
                      ]

class ValidationException(Exception):
    pass

def validate_cleantax(cleantax):
    taxonomies = e3_io.get_taxonomy_lines(cleantax)
    for taxonomy in taxonomies:
        validate_taxonomy(taxonomy)
    articulations = e3_io.get_articulation_lines(cleantax)
    
    validated_articulations = []
    for articulation in articulations[1:]:
        validate_articulation(articulation, taxonomies, validated_articulations)
        validated_articulations.append(articulation)
        
def validate_taxonomy(taxonomy):
    if not len(taxonomy[0].split()) == 3:
        raise ValidationException("Taxonomy head must consist of three parts")
    #what are the validation requirements for a taxonomy in the euler context? one or multiple roots possible?
    #utilize a graph lirary before going ahead with this 
    #only validate syntax for now
    for line in taxonomy[1:]:
        line = line.strip()
        if not line[0] == '(' or not line[-1] == ')':
             raise ValidationException("Taxonomy line has to start with '(' and end with ')'")
        inside = line[1:-1]
        if len(inside.split()) <= 1:
            raise ValidationException("Taxonomy line has to consist of two or more nodes")

def validate_articulation(articulation, taxonomies, articulations):  
    if articulation in articulations:
        raise ValidationException("This articulation already exists")
    node = "(.+\..+)"  
    validRelationsRegex = [
        "\[" + node + " " + node + " lsum " + node + "\]",
        "\[" + node + " " + node + " " + node + " l3sum " + node + "\]",
        "\[" + node + " " + node + " " + node + " " + node + " l4sum " + node + "\]",
        "\[" + node + " " + " rsum "  + node + " " + node + "\]",
        "\[" + node + " " + " r3sum " + node + " " + node + " " + node + "\]",
        "\[" + node + " " + " r4sum " + node + " " + node + " " + node + " " + node + "\]",
        "\[" + node + " " + node + " ldiff " + node + "\]",
        "\[" + node + " " + " rdiff "  + node + " " + node + "\]",
        "\[" + node + " " + node + " e4sum "  + node + " " + node + "\]",
        "\[" + node + " " + node + " i4sum "  + node + " " + node + "\]",
        "\[" + node + " equals " + node + "\]",
        "\[" + node + " includes " + node + "\]",
        "\[" + node + " is_included_in " + node + "\]",
        "\[" + node + " overlaps " + node + "\]",
        "\[" + node + " disjoint " + node + "\]",
        ]
    taxonomyIdToNodes = { }
    for taxonomy in taxonomies:
        id = taxonomy[0].split()[1]
        taxonomyIdToNodes[id] = []
        for line in taxonomy[1:]:
            taxonomyIdToNodes[id].extend(line.strip()[1:-1].split())
    
    for validRelationRegex in validRelationsRegex:
        match = re.match(validRelationRegex, articulation)
        if match:
            valid = True
            for group in match.groups():
                validate_node(group, taxonomyIdToNodes)
            return 
    raise ValidationException("No valid relation found. The set of supported relations is: {validRelations}.".format(
        validRelations = ', '.join(validRelations)))
        
def validate_node(node, taxonomyIdToNodes):
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