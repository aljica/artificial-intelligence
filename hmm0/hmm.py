import sys

class HMM:

    def __init__(self):
        self.A = []
        self.Arows = 0
        self.Acol = 0
        self.B = []
        self.Brows = 0
        self.Bcol = 0
        self.pi = []
        self.pirows = 0
        self.picol = 0

        self.readData()
        self.multMatrices()

    def readData(self):
        i = 0
        for data in sys.stdin:
            data = data.split()
            columns = int(data.pop(0))
            rows = int(data.pop(0))
            data = [float(i) for i in data] # Turn all elements into floats (from strings).

            # Format matrices/vectors
            for j in range(columns):
                if i == 0:
                    self.A.append(data[0:rows])
                    self.Arows = rows
                    self.Acol = columns
                elif i == 1:
                    self.B.append(data[0:rows])
                    self.Brows = rows
                    self.Bcol = columns
                elif i == 2:
                    self.pi.append(data[0:rows])
                    self.pirows = rows
                    self.picol = columns
                else:
                    sys.exit("Fatal error, exiting.") # Error.

                # Remove first #columns elements, because we've already retrieved them.
                for k in range(rows):
                    data.pop(0)

            i+=1

    def multMatrices(self):
        # The output will always be of size 1xself.Bcol, i.e. 1 row and as many columns as matrix B has.
        # First, multiply self.pi by self.A:
        piA = []
        for col in range(self.Arows):
            totalVal = 0
            for i in range(len(self.pi[0])):
                totalVal += self.pi[0][i] * self.A[i][col]
            piA.append(totalVal)
        #print(piA)

        resB = []
        for col in range(self.Brows): # I messed up the readdata pretty bad, but the brows are actually its columns
            totalVal = 0
            for i in range(len(piA)):
                totalVal += piA[i] * self.B[i][col]
            resB.append(totalVal)
        #print(resB)

        #resB = ["{:.1f}".format(i) for i in resB] # Formatting to 1 decimal place
        resB = [float(i) for i in resB]
        finalOutput = ""
        finalOutput += "1 " + str(self.Brows) # self.Brows is actually its columns... my mistake
        for r in resB:
            finalOutput += " " + str(r)
        print(finalOutput)

def main():
    hmm = HMM()

if __name__ == "__main__":
    main()
