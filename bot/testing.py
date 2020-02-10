from enum import Enum

def printA(text):
    print("A: " + text)

def printB(text):
    print("B: " + text)

myDict = {
    "a": printA,
    "b": printB
}

myDict["a"]("dffdvgf")