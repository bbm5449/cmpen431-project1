import csv
import sys
from collections import deque
import heapq

def readinputs(filename):
    insts=[]
    numRegisters, issueWidth = -1, -1
    with open(filename) as csvfile:
        instreader = list(csv.reader(csvfile,delimiter=','))
        numRegisters, issueWidth = instreader[0][0], instreader[0][1]
        for i in range(1, len(instreader)):
            row = instreader[i]
            if row[0] == 'R':
                insts.append([row[0],int(row[1]),-1,int(row[2]),int(row[3]),0,0,0,0,0,0,0])
            elif row[0] == 'L':
                insts.append([row[0],int(row[1]),-1,-1,int(row[3]),0,0,0,0,0,0,0])
            elif row[0] == 'I':
                insts.append([row[0],int(row[1]),-1,int(row[2]),-1,0,0,0,0,0,0,0])
            else: #S
                insts.append([row[0],-1,-1,int(row[1]),int(row[3]),0,0,0,0,0,0,0])
    return insts, int(numRegisters), int(issueWidth)

def initializeStructures(numRegisters):
    freeList = deque([i for i in range(32, numRegisters)])
    mapTable = [i for i in range(32)]
    readyTable = [1]*32 + [0]*32
    renameBuffer = deque([])
    iq = []
    lsq = deque([])
    return freeList, mapTable, readyTable, renameBuffer, iq, lsq

def fetch(instructions, indices, cycle):
    for i in range(len(indices[0])):
        if indices[0][i] != -1:
            instructions[indices[0][i]][5] = cycle
            if indices[0][i] + len(indices[0]) < len(instructions):
                indices[0][i] = indices[0][i] + len(indices[0])
            else:
                indices[0][i] = -1

def decode(instructions, indices, cycle):
    for i in range(len(indices[1])):
        if indices[1][i] != -1:
            instructions[indices[1][i]][6] = cycle
        indices[1][i] = indices[0][i]

def rename(instructions, indices, cycle, renameBuffer, freeList, mapTable):
    print(freeList)
    for i in range(len(indices[2])):
        if indices[2][i] != -1:
            instructions[indices[2][i]][7] = cycle
        if indices[1][i] != -1:
            renameBuffer.append(indices[1][i])
        indices[2][i] = -1

    for i in range(len(indices[2])):
        if freeList and renameBuffer:
            indices[2][i] = renameBuffer.popleft()
            dst = instructions[indices[2][i]][1]
            src1 = instructions[indices[2][i]][3]
            src2 = instructions[indices[2][i]][4]
            if src1 != -1:
                instructions[indices[2][i]][3] = mapTable[src1]
            if src2 != -1:
                instructions[indices[2][i]][4] = mapTable[src2]            
            if dst != -1:
                instructions[indices[2][i]][2] = mapTable[dst]
                instructions[indices[2][i]][1] = mapTable[dst] = freeList.popleft()


def dispatch(instructions, indices, cycle, readyTable, iq, lsq):
    for i in range(len(indices[3])):
        if indices[3][i] != -1:
            instructions[indices[3][i]][8] = cycle
        if indices[2][i] != -1:
            indices[3][i] = indices[2][i]
            instr = instructions[indices[3][i]][0]
            dst = instructions[indices[3][i]][1]
            src1 = instructions[indices[3][i]][3]
            src2 = instructions[indices[3][i]][4]
            src1Ready, src2Ready = readyTable[src1], readyTable[src2]
            if instr == 'L' or instr == 'S':
                lsq.append(indices[3][i])
            if src1 == -1:
                src1Ready = 1
            if src2 == -1:
                src2Ready = 1
            iq.append([indices[3][i], instr, dst, src1, src1Ready, src2, src2Ready])
            readyTable[dst] = 0
        else:
            indices[3][i] = -1

def issue(instructions, indices, cycle, readyTable, iq):
    for issue in iq:
        issue[4] = readyTable[issue[3]]
        issue[6] = readyTable[issue[5]]
        if issue[3] == -1:
            issue[4] = 1
        if issue[5] == -1:
            issue[6] = 1

    for i in range(len(indices[4])):
        if indices[4][i] != -1:
            instructions[indices[4][i]][9] = cycle
        indices[4][i] = -1

    count, i = 0, 0
    idx = []
    while count < len(indices[4]) and i < len(iq):
        issue = iq[i]
        if issue[4] and issue[6]:
            indices[4][count] = issue[0]
            idx.append(i)
            count += 1
        i += 1
    idx.sort(reverse=True)
    for i in idx:
        del iq[i]

def writeback(instructions, indices, cycle, readyTable, lsq):
    for i in range(len(indices[5])):
        if indices[5][i] != -1:
            instructions[indices[5][i]][10] = cycle
        instr = instructions[indices[5][i]][0]
        indices[5][i] = indices[4][i]
        dst = instructions[indices[5][i]][1]
        if instr == 'L' and lsq[0] == indices[5][i]:
            lsq.popleft()
        readyTable[dst] = 1

def commit(instructions, indices, cycle, freeList, lsq, committedInstructions):
    for i in range(len(indices[6])):
        if committedInstructions<len(instructions) and instructions[committedInstructions][10]:
            instr = instructions[committedInstructions][0]
            overwriteReg = instructions[committedInstructions][2]
            if instr == 'L' and committedInstructions not in lsq:
                freeList.append(overwriteReg)
                indices[6][i] = committedInstructions
                committedInstructions += 1
            elif instr == 'S' and committedInstructions == lsq[0]:
                lsq.popleft()
                indices[6][i] = committedInstructions
                committedInstructions += 1
            else:
                freeList.append(overwriteReg)
                indices[6][i] = committedInstructions
                committedInstructions += 1
        else:
            indices[6][i] = -1
        if indices[6][i] != -1:
            instructions[indices[6][i]][11] = cycle

    return committedInstructions

def simulate(instructions, numRegisters, issueWidth):
    cycle = 0
    committedInstructions = 0
    freeList, mapTable, readyTable, renameBuffer, iq, lsq = initializeStructures(numRegisters)
    issueWidth = min(issueWidth, len(instructions))
    indices = [[i for i in range(issueWidth)],
               [-1 for i in range(issueWidth)],[-1 for i in range(issueWidth)],[-1 for i in range(issueWidth)],
               [-1 for i in range(issueWidth)],[-1 for i in range(issueWidth)],[-1 for i in range(issueWidth)]]
    while committedInstructions < len(instructions):
        committedInstructions = commit(instructions, indices, cycle, freeList, lsq, committedInstructions)
        writeback(instructions, indices, cycle, readyTable, lsq)
        issue(instructions, indices, cycle, readyTable, iq)
        dispatch(instructions, indices, cycle, readyTable, iq, lsq)
        rename(instructions, indices, cycle, renameBuffer, freeList, mapTable)
        decode(instructions, indices, cycle)
        fetch(instructions, indices, cycle)
        cycle += 1

def printcycles(instructions):
    for inst in instructions[0:]:
        for stage in range(5,11):
            print("{:02d}".format(inst[stage]),end=",")
        print("{:02d}".format(inst[11]))

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
