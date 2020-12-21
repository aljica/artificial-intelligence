import sys

class HMM1:
    def __init__(self):
        self.A = []
        self.Arows = 0
        self.Acols = 0
        self.B = []
        self.Brows = 0
        self.Bcols = 0
        self.pi = []
        self.pirows = 0
        self.picols = 0
        self.emissions = []
        self.numEmissions = 0

        self.cE = [] # Current state probability estimates (1x4 vector)

        self.readData()
        self.formatData()
        self.forwardAlgo()
        self.kattisPrint()

    def kattisPrint(self):
        """Create output as per instructions found on Kattis."""
        p = str(sum(self.cE)) # Find max probability in current estimates
        #print(float(p))
        #print(self.cE)
        print(''.join(map(str, p)))
        #print(p)
        #print(self.cE)

    def forwardAlgo(self):
        self.initAlgo() # Initiate the algorithm (using the initial state probs, i.e. self.pi)

        currentEstimates = [] # For storing intermediate results
        # We will have to repeat this algorithm the number of times given by self.numEmissions=len(self.emissions)
        for i in range(len(self.emissions)):
            # Figure out which column in self.B we need to look at (will be used later):
            col = self.emissions.pop(0)

            # First, we must multiply the current estimates (self.cE) by each state transition, and add them together
            for i in range(len(self.cE)):
                transition_p = 0
                for j in range(len(self.cE)):
                    # i is the number of the column in A we need to look at
                    # j is the number of the row in A we need to look at
                    transition_p += self.cE[j] * self.A[j][i]
                # Then, we multiply by the observational probabilities
                obs_p = transition_p * self.B[i][col] # The final observational probability is...
                currentEstimates.append(obs_p)

            # Transfer intermediate results storage to official storage (self.cE)
            for i in range(len(currentEstimates)):
                self.cE[i] = currentEstimates[i]
            currentEstimates = []

    def initAlgo(self):
        # First, figure out which column in self.B is relevant (based on which emission is first up)
        col = self.emissions.pop(0) # i.e. the col:th element of each row (sub-list) in self.B
        self.numEmissions -= 1 # Just in case... (because in forwardAlgo() we'll have 1 emission less to deal with)

        # Now, we wish to multiply each initial state probability by the probability of the given emission occurring for that state
        for i in range(len(self.pi)):
            p = self.pi[i] * self.B[i][col] # The probability
            self.cE.append(p)

    def formatData(self):
        self.Arows = int(self.A.pop(0))
        self.Acols = int(self.A.pop(0))
        self.Brows = int(self.B.pop(0))
        self.Bcols = int(self.B.pop(0))
        self.pirows = int(self.pi.pop(0))
        self.picols = int(self.pi.pop(0))
        self.numEmissions = int(self.emissions.pop(0))

        self.A = [float(i) for i in self.A]
        self.B = [float(i) for i in self.B]
        self.pi = [float(i) for i in self.pi]
        self.emissions = [int(i) for i in self.emissions]

        # Represent the matrices as python lists
        A = []
        for i in range(self.Arows):
            A.append(self.A[0:self.Acols])
            for k in range(self.Acols):
                self.A.pop(0)
        self.A = A

        B = []
        for i in range(self.Brows):
            B.append(self.B[0:self.Bcols])
            for k in range(self.Bcols):
                self.B.pop(0)
        self.B = B

    def readData(self):
        d = sys.stdin
        i = 0
        for x in d:
            x = x.split()
            if i == 0:
                self.A = x
            elif i == 1:
                self.B = x
            elif i == 2:
                self.pi = x
            else:
                self.emissions = x
            i += 1

def main():
    hmm = HMM1()

if __name__ == "__main__":
    main()
