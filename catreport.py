#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Timewarrior extension: catreport
# Author: Frank Stollmeier
# License: MIT


import sys
from timewreport.parser import TimeWarriorParser


class Node(dict):
    '''This node represents a task or a category of tasks and may contain other nodes.'''
    
    def __init__(self, name, parent):
        '''
        Parameters
        ----------
        name:   string
        parent: instance of Node()
        '''
        self.intervals = []
        self.name = name
        self.parent = parent
        dict.__init__(self)
    
    def get_node(self, path_to_node, create_if_not_existing = False):
        '''Return a node which is somewhere deeper in the hierarchy. 
        If the specified node does not exist return None. If create_if_not_existing is True and the specified node does not exist, create the node and return the new node.
        
        Parameters
        ----------
        path_to_node:           list of strings, e. g. ["projectA", "subprojectA1", "task13"]
        create_if_not_existing: bool, optional, default is False.
        '''
        if len(path_to_node) == 0:
            return self
        else:
            child = path_to_node.pop(0)
            if child in self:
                return self[child].get_node(path_to_node, create_if_not_existing)
            elif create_if_not_existing:
                self[child] = Node(child, self)
                return self[child].get_node(path_to_node, create_if_not_existing)
            else:
                return None
    
    def add_node(self, path_to_node):
        '''Add a new node and return it.
        
        Parameters
        ----------
        path_to_node:   list of strings, e. g. ["projectA", "subprojectA1", "task13"]
        '''
        return self.get_node(path_to_node, create_if_not_existing = True)
    
    def is_leaf(self):
        '''Return True, if the node has no child nodes, and False, if it has child nodes.'''
        return len(self) == 0
    
    def get_duration(self):
        '''Return the total number of seconds spend in this task/category excluding time spend in subcategories.'''
        return sum([i.get_duration().total_seconds() for i in self.intervals])
    
    def get_cumulated_duration(self):
        '''Return the total number of seconds spend in this task/category including the spend in subcategories.'''
        return self.get_duration() + sum([child.get_cumulated_duration() for child in self.values()])


def store_intervals_in_tree(intervals):
    '''Create and return a tree structure containing all tracked time intervals.
    
    Parameters
    ----------
    intervals:  list of intervals, as returned by TimeWarriorParser(stdin).get_intervals()
    '''
    root = Node('root', None)
    for interval in intervals:
        for tags in interval.get_tags():
            node = root.add_node(tags.split('.'))
            node.intervals.append(interval)
    return root


def print_report(root):
    '''Create the catreport.
    
    Parameters
    ----------
    root:   instance of class Node, as returned by store_intervals_in_tree()
    '''
    #tabular layout
    width_col1 = 60
    width_col2 = 30
    width_col3 = 30
    #print header
    print("\n")
    print("{0:<{wc1}}{1:<{wc2}}{2:<{wc3}}".format('Task', 'Time [h]', 'Share [%]', wc1 = width_col1, wc2 = width_col2, wc3 = width_col3))
    print((width_col1+width_col2+width_col3)*"=")
    #print data
    def print_recursively(node, level = 0):
        #print line
        hours = node.get_cumulated_duration()/(60*60)
        if node.parent is None:
            share = 100
        else:
            share = 100 * hours / (node.parent.get_cumulated_duration()/(60*60))
        shift = level * '    '
        print("{0:<{wc1}}{1:<{wc2}}{2:<{wc3}}".format(shift + node.name, shift + "{:.1f}".format(hours), shift + "{:.1f}".format(share) , wc1 = width_col1, wc2 = width_col2, wc3 = width_col3))
        
        #go down the tree
        for key in sorted(node.keys()):
            print_recursively(node[key], level + 1)
        if node.get_duration() > 0 and len(node) > 0:
            h = node.get_duration()/(60*60)
            s = 100 * h / hours
            shift = (level + 1) * '    '
            print("{0:<{wc1}}{1:<{wc2}}{2:<{wc3}}".format(shift + 'unknown', shift + "{:.1f}".format(h), shift + "{:.1f}".format(s) , wc1 = width_col1, wc2 = width_col2, wc3 = width_col3))
    
    print_recursively(root)
    print("\n")

    
def main(stdin):
    parser = TimeWarriorParser(stdin)
    tw_config = parser.get_config()
    tw_intervals = parser.get_intervals()
    
    root = store_intervals_in_tree(tw_intervals)
    print_report(root)
    #sys.exit(0)


if __name__ == "__main__":
    main(sys.stdin)
    #print(stdin.read())


######################################################################
##    The following code is just for development and debugging.     ##
######################################################################


def load_testdata(filename):
    '''This function allows testing functions with a static data set instead of the real data from timewarrior.
    To create a static data set from your real data, comment main(sys.stdin) and uncomment print(stdin.read()) in if __name__ == "__main__", and then run timew catreport > static-data
    '''
    with open(filename, "r") as f:
        parser = TimeWarriorParser(f)
    tw_config = parser.get_config()
    tw_intervals = parser.get_intervals()
    return tw_config.get_dict(), tw_intervals    

def test():
    config,intervals = load_testdata("./static-data")
    root = store_intervals_in_tree(intervals)
    print_report(root)

def show_intervals_with(keyword, intervals):
    '''Filter intervals by key.'''
    for i in intervals:
        if keyword in i.get_tags():
            print(i.get_date(),i.get_tags())

