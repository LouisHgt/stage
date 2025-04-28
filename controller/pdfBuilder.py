from abc import ABC, abstractmethod

from .Builder import Builder

class PdfBuilder(Builder):
    
    def __init__(self):
        pass
    
    def initDoc(self):
        pass
    
    def writeDoc(self):
        pass
    
    def addParagraph(self, elt, niveau):
        pass
        
    