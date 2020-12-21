import sys
import operator

class HMM2:
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

        self.delta = [] # Store probability of each hidden state at each time step
        self.delta_idx = [] # Index of which hidden state in prev time state to point at, for each hidden state in current time state

        self.readData()
        self.formatData()
        self.viterbiAlgo()
        self.backtrack()

    def viterbiAlgo(self):
        self.initAlgo()

        for t in range(len(self.emissions)):
            col = self.emissions.pop(0)
            self.delta.append([])
            self.delta_idx.append([])

            # For each prob in the current time state (starting at t=1):
            for j in range(len(self.delta[t])):
                all_p = [] # All (four) probabilities to move from hidden state A, B, C and D at time state t to hidden state A/B/C/D at t+1
                for k in range(len(self.delta[t])):
                    # We have to loop twice to run through each state transition once.
                    current_p = self.delta[t][k]
                    transition_p = self.A[k][j] # State transitional probability
                    obs_p = self.B[j][col]
                    all_p.append(current_p*transition_p*obs_p)
                # Now, we only care about the max probability
                max_p_index, max_p = max(enumerate(all_p), key=operator.itemgetter(1)) # See https://stackoverflow.com/questions/6193498/pythonic-way-to-find-maximum-value-and-its-index-in-a-list
                # max_p_index tells us which hidden state at time state t gives max_p for hidden state j at time state t+1
                self.delta[t+1].append(max_p)
                self.delta_idx[t+1].append(max_p_index)

    def backtrack(self):
        # Backtracking is done by selecting the index of the hidden state with highest probability at the
        # final time state in self.delta, and then backtracking with the help of self.delta_idx.
        #print(self.delta)
        #print(self.delta_idx)

        order_of_backtracks = []
        max_p_index, max_p = max(enumerate(self.delta[len(self.delta)-1]), key=operator.itemgetter(1))
        order_of_backtracks.append(max_p_index)
        for t in range(len(self.delta_idx)-1, 0, -1):
            order_of_backtracks.append(self.delta_idx[t])
        #print(order_of_backtracks)

        pointers = []
        pointers.append(order_of_backtracks[0])
        order_of_backtracks.pop(0)
        for i in range(len(order_of_backtracks)):
            idx = pointers[i]
            pointers.append(order_of_backtracks[i][idx])
        #print(pointers)

        output = ""
        for i in range(len(pointers)-1, -1, -1):
            output += str(pointers[i]) + " "
        print(output)

    def initAlgo(self):
        # Simply multiply the initial state p-vector by the emission at t=1, and store result in self.delta
        # self.delta[0] will be the probability of each hidden state at t=1
        # self.delta_idx[0] should be an empty list

        col = self.emissions.pop(0) # i.e. the col:th element of each row (sub-list) in self.B
        self.delta.append([])

        for i in range(len(self.pi)):
            p = self.pi[i] * self.B[i][col]
            self.delta[0].append(p)
        self.delta_idx.append([]) # Just to make things simpler when backtracking later

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
    hmm = HMM2()

if __name__ == "__main__":
    main()
