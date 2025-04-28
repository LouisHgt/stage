from abc import ABC, abstractmethod

class Builder(ABC):
    @abstractmethod
    def initDoc(self):
        pass
    
    @abstractmethod
    def writeDoc(self):
        pass
    
    @abstractmethod
    def addParagraph(self, elt, niveau):
        pass