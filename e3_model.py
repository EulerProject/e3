'''
Created on Nov 22, 2016

'''
from pinject import copy_args_to_public_fields
import hashlib
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from compiler.ast import Node

class Tap(object):
    @copy_args_to_public_fields
    def __init__(self, isCoverage, isSiblingDisjointness, regions, taxonomies, articulations):
        pass
    def add_taxonomy(self, taxonomy):
        for t in self.taxonomies:
            if t.id == taxonomy.id:
                raise Exception("Taxonomy id " + t.id + " already exists")
        self.taxonomies.append(taxonomy)
    def remove_taxonomy(self, taxonomyId):
        self.articulations = [a for a in self.articulations if not self.is_references_taxonomy(a, taxonomyId)]
        self.taxonomies = [t for t in self.taxonomies if not t.id == taxonomyId]
        pass
    def clear_taxonomy(self, taxonomyId):
        self.articulations = [a for a in self.articulations if not self.is_references_taxonomy(a, taxonomyId)]
        self.get_taxonomy(taxonomyId).clear()
    def get_referenced_taxonomies(self, articulation):
        referencedTaxonomies = []
        for l in articulation.left:
            id = l.split(".")[0]
            t = self.get_taxonomy(id)
            referencedTaxonomies.append(t)
        for r in articulation.right:
            id = r.split(".")[0]
            t = self.get_taxonomy(id)
            referencedTaxonomies.append(t) 
        return referencedTaxonomies
    def is_references_taxonomy(self, articulation, taxonomyId):
        referencedTaxonomies = self.get_referenced_taxonomies(articulation)
        for t in referencedTaxonomies:
            if t.id == taxonomyId:
                return True
        return False
    def set_taxonomy_info(self, taxonomyId, newTaxonomyId, newName):
        taxonomy = self.get_taxonomy(taxonomyId)
        taxonomy.id = newTaxonomyId
        taxonomy.name = newName
        for a in self.articulations:
            newLeft = []
            for l in a.left:
                if l.split(".")[0] == taxonomyId: newLeft.append(newTaxonomyId + "." + l.split(".")[1])
                else: newLeft.append(l)
            a.left = newLeft
            newRight = []
            for r in a.right:
                if r.split(".")[0] == taxonomyId: newRight.append(newTaxonomyId + "." + r.split(".")[1])
                else: newRight.append(r)
            a.right = newRight
                        
    def has_taxonomy(self, id):
        return self.get_taxonomy(id) is not None
    def remove_children(self, taxonomyId, parent, children):
        taxonomy = self.get_taxonomy(taxonomyId)
        taxonomy.remove_children(parent, children)
        self.articulations = [a for a in self.articulations if self.nodes_in_tap(a)]
    def nodes_in_tap(self, articulation):
        for l in articulation.left:
            id = l.split(".")[0]
            node = l.split(".")[1]
            taxonomy = self.get_taxonomy(id)
            if not taxonomy is None:
                if not taxonomy.contains_node(node):
                    return False
            else:
                return False
        for r in articulation.right:
            id = r.split(".")[0]
            node = r.split(".")[1]
            taxonomy = self.get_taxonomy(id)
            if not taxonomy is None:
                if not taxonomy.contains_node(node):
                    return False
            else:
                return False
        return True
        
    def get_taxonomy(self, id):
        for t in self.taxonomies:
            if t.id == id:
                return t
        return None
    def add_articulation(self, articulation):
        for l in articulation.left:
            id = l.split(".")[0]
            t = self.get_taxonomy(id)
            if t is None:
                raise Exception("No taxonomy with id " + id + " found.")
        for r in articulation.right:
            id = r.split(".")[0]
            t = self.get_taxonomy(id)
            if t is None:
                raise Exception("No taxonomy with id " + id + " found.")        
        self.articulations.append(articulation)
    def remove_articulation(self, articulationIndex):
        del self.articulations[int(articulationIndex)]
    def __str__(self, *args, **kwargs):
        indices = []
        for x in range(1, len(self.articulations) + 1):
            indices.append(str(x) + ". ")
        articulationLines = [x + y for x, y in zip(indices, [a.__str__() for a in self.articulations])]
        articulationLines.insert(0, 'articulation')     
        result = []
        for taxonomy in self.taxonomies:
            taxonomyLines = taxonomy.__str__().split('\n')
            result.append('\n'.join(taxonomyLines))
               
        result.append('\n'.join(articulationLines))
        result = ('Coverage:' + str(self.isCoverage) + 
                 '\nSibling Disjontness:' + str(self.isSiblingDisjointness) + 
                 '\nRegions:' + self.regions + '\n\n' + 
                '\n\n'.join(result))
        return result
        
    def get_id(self):
        return hashlib.sha1(self.__str__()).hexdigest()
    
#could be a graph at some point if desired to be able to modify the taxonomy on the fly
#e.g. adding a new child somewhere
class Taxonomy(object):
    @copy_args_to_public_fields
    def __init__(self, id, name):
        self.g = nx.DiGraph()
        pass
    def clear(self):
        self.g.clear()
    def add_children(self, parent, children):
        self.g.add_edges_from(zip([parent] * len(children), children))
    def remove_children(self, parent, children):
        self.g.remove_edges_from(zip([parent] * len(children), children))
        self.g.remove_nodes_from(children)
    def contains_node(self, node):
        return self.g.has_node(node)
    def add_node(self, parent, child):
        if parent == None:
            self.g.add_node(child)
        else:
            self.g.add_edge(parent, child)
    def remove_nodes(self, nodes):
        for n in nodes:
            self.remove_node(n)
    def remove_node(self, node):
        self.remove_children(node)
        self.g.remove_node(node)
    def remove_all_children(self, node):
        for e in self.g.out_edges(node):
            self.g.remove_node(e[1])
    def get_roots(self):
        roots = []
        for node in self.g.nodes():
            if len(self.g.predecessors(node)) == 0:
                roots.append(node)
        return roots
    def __str__(self, *args, **kwargs):
        edges = []
        for node in self.get_roots():
            self.add_cleantax_stringyfied_edges(edges, node)
        result = "taxonomy " + self.id + " " + self.name
        if len(edges) > 0:
            result = result + '\n' + '\n'.join(edges)
        return result
    def add_cleantax_stringyfied_edges(self, collector, src):
        if len(self.g.successors(src)) > 0:
            line = "(" + src
            for successor in self.g.successors(src):
                line = line + " " + successor
                self.add_cleantax_stringyfied_edges(collector, successor)
            line = line + ")"
            collector.insert(0, line)
            
relations = [ "lsum", "l3sum", "l4sum", "rsum", "r3sum", "r4sum", "ldiff", "rdiff", "e4sum", "i4sum", "equals", "includes", 
                      "is_included_in", "overlaps", "disjoint" 
                      ]            
            
#see Taxonomy comment
class Articulation(object):
    @copy_args_to_public_fields
    def __init__(self, left, right, relation):
        pass
    def __str__(self):
        return "[" + " ".join(self.left) + " " + self.relation + " " + " ".join(self.right) + "]"

if __name__ == '__main__':
    ta = Taxonomy("id", "name")
    ta.add_node(None, "a")
    ta.add_node("a", "b")
    ta.add_children("a", ["c", "d", "e"])
    #ta.remove_children("a")
    ta.remove_nodes(["c", "e"])
    pass
    