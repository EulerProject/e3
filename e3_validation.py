'''
Created on Nov 22, 2016

@author: Thomas
'''
import e3_io

class ValidationException(Exception):
    pass

def validate_cleantax(cleantax):
    taxonomies = e3_io.get_taxonomies(cleantax)
    for taxonomy in taxonomies:
        validate_taxonomy(taxonomy)
    articulations = e3_io.get_articulations(cleantax)
    
    for articulation in articulations[1:]:
        validate_articulation(articulation, taxonomies)
        
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

def validate_articulation(articulation, taxonomies):
    validRelations = ['equals', 'overlaps', 'includes', 'is_included_in', 'disjoint', 'lsum', 'rsum']
    taxonomyIdToNodes = { }
    for taxonomy in taxonomies:
        id = taxonomy[0].split()[1]
        taxonomyIdToNodes[id] = []
        for line in taxonomy[1:]:
            taxonomyIdToNodes[id].extend(line.strip()[1:-1].split())
    articulation = articulation[1:-1]
    parts = articulation.split()
    
    relationIndex = None
    for i, part in enumerate(parts):
        if part in validRelations:
            relation = part
            relationIndex = i
            break
    if not relationIndex:    
        raise ValidationException("No valid relation found. The set of supported relations is: {validRelations}.".format(
            validRelations = ', '.join(validRelations)))
    leftNodes = parts[0:i]
    rightNodes = parts[i+1:]
    if len(leftNodes) == 0:
        raise ValidationException("Missing left part of articulation")
    if len(rightNodes) == 0:
        raise ValidationException("Missing right part of articulation")
    
    taxonomyIds = ', '.join(taxonomyIdToNodes.keys())
    taxonomyIdNotFoundText = "{taxonomyId} of {node} not found in the list of taxonomies ({taxonomyIds})"
    nodeNotFoundText = "{nodeName} of {node} not found in the nodes of taxonomy {taxonomyId}"
    for node in leftNodes + rightNodes:
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
    
    leftNodesId = leftNodes[0].split('.')[0]
    for node in leftNodes:
        nodeTaxonomyId = node.split('.')[0]
        if not nodeTaxonomyId == leftNodesId:
            raise ValidationException("All nodes of the left part of the articulation have to stem from the same taxonomy")
    rightNodesId = rightNodes[0].split('.')[0]
    for node in rightNodes:
        nodeTaxonomyId = node.split('.')[0]
        if not nodeTaxonomyId == rightNodesId:
            raise ValidationException("All nodes of the right part of the articulation have to stem from the same taxonomy")