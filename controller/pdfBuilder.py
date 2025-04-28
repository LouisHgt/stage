from abc import ABC, abstractmethod

from .builder import builder

class pdfBuilder(builder):
    
    def __init__(self):
        pass
    
    def initDoc(self):
        pass
    
    def writeDoc(self):
        pass
    
    def addParagraph(self, elt, niveau):
        pass
        
    