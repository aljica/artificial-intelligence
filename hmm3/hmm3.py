import sys
import math

class HMM3:
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

        self.readData()
        self.formatData()

        self.createAlpha()
        self.alphaPass()

        self.createBeta()
        self.betaPass()

        self.createGammas()
        self.computeGammas()

        self.reEstimate()
        self.iterate()

        self.kattisPrint()

    def kattisPrint(self):
        # First, print details of transmission matrix:
        A = ""
        N = str(len(self.A)) # Number of hidden states
        A += N + " " + N + " "
        for row in self.A:
            for p in row:
                A += str(p) + " "
        print(A)

        B = ""
        N = str(len(self.B))
        M = str(len(self.B[0]))
        B += N + " " + M + " "
        for row in self.B:
            for p in row:
                B += str(p) + " "
        print(B)

    def computeLog(self):
        logProb = 0
        T = len(self.emissions)
        for i in range(T):
            logProb += math.log(self.c[i])
        logProb = -logProb

        return logProb

    def iterate(self):
        maxIters = math.inf # Maximum number of re-estimation iterations
        iters = 0
        oldLogProb = -math.inf

        logProb = self.computeLog()

        while True:
            iters += 1
            print(iters)
            if ((iters < maxIters) and (logProb > oldLogProb)):
                oldLogProb = logProb
                # Go back to step 2:
                self.initAlpha()
                self.alphaPass()

                self.initBeta()
                self.betaPass()

                self.computeGammas()

                self.reEstimate()

                logProb = self.computeLog()
            else:
                break

    def reEstimate(self):
        # Re-esimate self.pi
        for i in range(len(self.A)):
            self.pi[i] = self.gamma[0][i]

        # Re-estimate A
        T_minus_one = len(self.emissions) - 1

        for i in range(len(self.A)):
            denom = 0
            # for-loop below goes up to T-2
            for t in range(T_minus_one):
                denom += self.gamma[t][i]
            for j in range(len(self.A)):
                numer = 0
                for t in range(T_minus_one):
                    numer += self.digamma[t][i][j]
                self.A[i][j] = numer/denom

        # Re-estimate B
        T = len(self.emissions)
        M = len(self.B[0]) # Doesn't matter which row we choose, we just want to know how many columns each row has.

        for i in range(len(self.A)):
            denom = 0
            # for-loop below goes up to T-1
            for t in range(T):
                denom += self.gamma[t][i]
            # for-loop below goes up to M-1
            for j in range(M):
                numer = 0
                for t in range(T):
                    if (self.emissions[t] == j):
                        numer += self.gamma[t][i]
                self.B[i][j] = numer/denom

    def computeGammas(self):
        T_minus_one = len(self.emissions) - 1
        # for loop below does not include T_minus_one. T-1 is a special case, see below.
        for t in range(T_minus_one):
            for i in range(len(self.A)):
                self.gamma[t][i] = 0
                for j in range(len(self.A)):
                    self.digamma[t][i][j] = self.alpha[t][i] * self.A[i][j] * self.B[j][self.emissions[t+1]] * self.beta[t+1][j]
                    self.gamma[t][i] += self.digamma[t][i][j]

        # Special case for T-1
        for i in range(len(self.A)):
            self.gamma[T_minus_one][i] = self.alpha[T_minus_one][i]

    def createGammas(self):
        self.gamma = [0] * len(self.emissions)
        for t in range(len(self.gamma)):
            self.gamma[t] = [0] * len(self.A)

        self.digamma = [0] * len(self.emissions)
        for i in range(len(self.digamma)):
            self.digamma[i] = []
        for t in range(len(self.digamma)):
            for i in range(len(self.A)):
                self.digamma[t].append([])
        for t in range(len(self.digamma)):
            for i in range(len(self.A)):
                for j in range(len(self.A)):
                    self.digamma[t][i].append(0)

    def alphaPass(self):
        # Compute alpha_zero
        for t in range(1, len(self.emissions), 1):
            obs = self.emissions[t] # Column to look at in self.B given the observation at time state t
            self.c[t] = 0
            for i in range(len(self.A)):
                self.alpha[t][i] = 0
                for j in range(len(self.A)):
                    self.alpha[t][i] += self.alpha[t-1][j] * self.A[j][i]
                self.alpha[t][i] *= self.B[i][obs]
                self.c[t] += self.alpha[t][i]

            # Scaling
            self.c[t] = 1/self.c[t]
            for i in range(len(self.A)):
                self.alpha[t][i] *= self.c[t]

    def initAlpha(self):
        self.c[0] = 0
        for i in range(len(self.A)):
            self.alpha[0][i] = self.pi[i] * self.B[i][self.emissions[0]]
            self.c[0] += self.alpha[0][i]

        # Scale the AlphaZero(i)
        self.c[0] = 1/self.c[0]
        for i in range(len(self.A)):
            self.alpha[0][i] *= self.c[0]

    def createAlpha(self):
        self.alpha = [0] * len(self.emissions)
        for t in range(len(self.alpha)):
            self.alpha[t] = [0] * len(self.A)
        self.c = [0] * len(self.emissions) # Init self.C

        self.initAlpha()

    def betaPass(self):
        T_minus_two = len(self.emissions)-2
        for t in range(T_minus_two, -1, -1):
            # N - 1 = len(self.A) in the loop below
            obs = self.emissions[t+1] # Observation @ time state ahead
            for i in range(len(self.A)):
                self.beta[t][i] = 0
                for j in range(len(self.A)):
                    self.beta[t][i] += self.A[i][j] * self.B[j][obs] * self.beta[t+1][j]
                # Scale beta with same scale factor as alpha in alpha pass
                self.beta[t][i] *= self.c[t]

    def initBeta(self):
        # Initialize scaling
        T_minus_one = len(self.emissions)-1
        for i in range(len(self.A)):
            self.beta[T_minus_one][i] = self.c[T_minus_one]

    def createBeta(self):
        self.beta = [0] * len(self.emissions)
        for t in range(len(self.beta)):
            self.beta[t] = [0] * len(self.A)

        self.initBeta()

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

        #self.emissions.insert(0, -1) # To avoid problems with self.emissions (which starts from index 0 but time state begins at t=1 below)

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
    hmm = HMM3()

if __name__ == "__main__":
    main()
