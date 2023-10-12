import csv
import sys

def readinputs(filename):
    insts=[['R',0,0,0,0,0,0,0,0]]
    with open(filename) as csvfile:
        instreader=csv.reader(csvfile,delimiter=',')
        for row in instreader:
            if row[0] == 'R':
                insts.append([row[0],row[1],row[2],row[3],0,0,0,0,0])
            elif row[0] == 'L':
                insts.append([row[0],row[1],0,row[3],0,0,0,0,0])
            elif row[0] == 'I':
                insts.append([row[0],row[1],row[2],0,0,0,0,0,0])
            else: #S
                insts.append([row[0],0,row[1],row[3],0,0,0,0,0])
    return insts


def fetch(instructions, indices, cycle, stall):
    if(indices[0]!=0):
        instructions[indices[0]][4]=cycle
        if (stall):
            pass
        else:
            if(indices[0]<len(instructions)-1):
                indices[0] = indices[0] + 1
            else:
                indices[0] = 0

def decode(instructions, indices, cycle):
    if(indices[1]!=0):
        instructions[indices[1]][5]=cycle
    else:
        pass
    stall = False
    input1=instructions[indices[1]][2]
    input2=instructions[indices[1]][3]
    exOut = instructions[indices[3]][1]
    if (instructions[indices[3]][0]!= 'L'):
        exOut=0
    if exOut!=0 and ((input1==exOut and instructions[indices[1]][0]!='S') or input2==exOut):
        stall = True
        indices[2]=0
    if (stall):
        pass
    else:
        indices[1]=indices[0]
    return stall

def execute(instructions, indices, cycle):
    if(indices[2]!=0):
        instructions[indices[2]][6]=cycle
    else:
        pass
    indices[2]=indices[1]

def memory(instructions, indices, cycle):
    if(indices[3]!=0):
        instructions[indices[3]][7]=cycle
    else:
        pass
    indices[3]=indices[2]

    
def writeback(instructions, uncommittedInstructions, indices, cycle):
    if(indices[4]!=0):
        instructions[indices[4]][8]=cycle
        indices[4]=indices[3]
        return uncommittedInstructions - 1
    else:
        indices[4]=indices[3]
        return uncommittedInstructions

def simulate(instructions):
    cycle=0
    uncommittedInstructions=len(instructions) - 1
    indices=[1,0,0,0,0]
    while uncommittedInstructions > 0:        
        uncommittedInstructions = writeback(instructions,uncommittedInstructions, indices, cycle)
        memory(instructions, indices, cycle)
        execute(instructions, indices, cycle)
        stall = decode(instructions, indices, cycle)
        fetch(instructions, indices, cycle, stall)
        cycle = cycle + 1

def printcycles(instructions):
    for inst in instructions[1:]:
        for stage in range(4,8):
            print("{:02d}".format(inst[stage]),end=",")
        print("{:02d}".format(inst[8]))


def main():
    filename = sys.argv[1]
    instructions=readinputs(filename)
    simulate(instructions)
    printcycles(instructions)

if __name__ == "__main__":
    main()
