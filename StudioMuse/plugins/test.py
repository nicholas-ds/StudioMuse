#!/usr/bin/env python

from gimpfu import *

def plugin_test(image, drawable):
    pdb.gimp_message("Test plugin works!")

register(
    "test_plugin",
    "Test Plugin",
    "A test plugin",
    "You",
    "You",
    "2024",
    "<Image>/Test/Test Plugin",
    "*",
    [],
    [],
    plugin_test)

main() 