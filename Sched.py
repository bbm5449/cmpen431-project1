import csv
import sys
from collections import deque

def readinputs(filename):
    insts=[]
    numRegisters, issueWidth = -1, -1
    with open(filename) as csvfile:
        instreader = list(csv.reader(csvfile,delimiter=','))
        numRegisters, issueWidth = instreader[0][0], instreader[0][1]
        for i in range(1, len(instreader)):
            row = instreader[i]
            if row[0] == 'R':
                insts.append([row[0],row[1],row[2],row[3],0,0,0,0,0,0,0])
            elif row[0] == 'L':
                insts.append([row[0],row[1],0,row[3],0,0,0,0,0,0,0])
            elif row[0] == 'I':
                insts.append([row[0],row[1],row[2],0,0,0,0,0,0,0,0])
            else: #S
                insts.append([row[0],0,row[1],row[3],0,0,0,0,0,0,0])
    return insts, int(numRegisters), int(issueWidth)

def initializeStructures(numRegisters):
    freeList = deque([i for i in range(32, numRegisters)])
    mapTable = [i for i in range(32)]
    readyTable = [1]*32 + [0]*32
    renameBuffer = deque([])
    iq = {}
    rob = deque([])
    return freeList, mapTable, readyTable, renameBuffer

def fetch(instructions, indices, cycle):
    print(indices)
    for i in range(len(indices[0])):
        if indices[0][i] != -1:
            instructions[indices[0][i]][4] = cycle
            if indices[0][i] + len(indices[0]) < len(instructions):
                indices[0][i] = indices[0][i] + len(indices[0])
            else:
                indices[0][i] = -1

def decode(instructions, indices, cycle):
    for i in range(len(indices[1])):
        if indices[1][i] != -1:
            instructions[indices[1][i]][5] = cycle
        indices[1][i] = indices[0][i]

def rename(instructions, indices, cycle, renameBuffer, freeList, mapTable):
    for i in range(len(indices[2])):
        if indices[2][i] != -1:
            instructions[indices[2][i]][6] = cycle
        if indices[1][i] != -1:
            renameBuffer.append(indices[1][i])

    for i in range(len(indices[2])):
        if freeList:
            return 0



        
    

def dispatch():
    return 0

def issue():
    return 0
    
def writeback():
    return 0

def commit(committedInstructions):
    return committedInstructions + 1

def simulate(instructions, numRegisters, issueWidth):
    cycle = 0
    committedInstructions = 0
    freeList, mapTable, readyTable, renameBuffer = initializeStructures(numRegisters)
    indices = [[i for i in range(issueWidth)],
               [-1 for i in range(issueWidth)],[-1 for i in range(issueWidth)],[-1 for i in range(issueWidth)],
               [-1 for i in range(issueWidth)],[-1 for i in range(issueWidth)],[-1 for i in range(issueWidth)]]
    while committedInstructions < len(instructions):
        committedInstructions = commit(committedInstructions)
        writeback()
        issue()
        dispatch()
        rename(instructions, indices, cycle, renameBuffer, freeList, mapTable)
        decode(instructions, indices, cycle)
        fetch(instructions, indices, cycle)
        cycle += 1

def printcycles(instructions):
    for inst in instructions[0:]:
        for stage in range(4,10):
            print("{:02d}".format(inst[stage]),end=",")
        print("{:02d}".format(inst[10]))

def main():
    filename = sys.argv[1]
    instructions, numRegisters, issueWidth = readinputs(filename)
    print('Before:')
    printcycles(instructions)
    simulate(instructions, numRegisters, issueWidth)
    print('After:')
    printcycles(instructions)
    
if __name__ == "__main__":
    main()
