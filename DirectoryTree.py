from FileButtons import SelectDirectoryButton
import IPython.display as ipd
from ipytree import Tree, Node
import os

class Directory(Node):
    path = None

class DirectoryTree():
    def __init__(self, rootPath=None):
        self.paths = []
        if rootPath is None:
            self.directoryButton = SelectDirectoryButton(self.processFilesFromButton)
            ipd.display(self.directoryButton)
        else:
            self.path = rootPath
            self.processFiles()

    def processFilesFromButton(self):
        self.path = self.directoryButton.files
        self.processFiles()

    def processFiles(self):
        tree = Tree(stripes=True)
        oldNode = Node("Base")
        self.parseDir(self.path, oldNode)
        tree.add_node(oldNode)
        ipd.display(tree)

    def handle_click(self, event):
        print("Handling Click!")
        if event['new']:
            self.paths.append(event['owner'].path)
        else:
            self.paths.remove(event['owner'].path)

    def parseDir(self, path, previousNode):
        for file in os.scandir(path):
            newPath = os.path.join(path, file)
            if os.path.isdir(newPath):
                newNode = Directory(os.path.basename(file))
                newNode.path = newPath
                newNode.observe(self.handle_click, 'selected')
                newNode.opened = False
                previousNode.add_node(newNode)
                self.parseDir(newPath, newNode)
