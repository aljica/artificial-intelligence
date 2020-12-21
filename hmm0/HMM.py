import sys

def readData():
    i=0
    for data in sys.stdin:
        data = data.split()
        if i == 0:
            A = data
            A = [float(i) for i in A]
        if i == 1:
            B = data
            B = [float(i) for i in B]
        if i == 2:
            pi = data
            pi = [float(i) for i in pi]
        i += 1

    return A, B, pi

def main():
    a, b, pi = readData()
    pi = pi[2:] # We don't need to know its size, we can see the number of columns by the length of the list

    Arows = int(a.pop(0))
    Acols = int(a.pop(0))
    Brows = int(b.pop(0))
    Bcols = int(b.pop(0))

    # Format data
    A = []
    B = []
    for i in range(Arows):
        A.append(a[0:Acols])
        for k in range(Acols):
            a.pop(0)
    print(A)

    for i in range(Brows):
        B.append(b[0:Bcols])
        for k in range(Bcols):
            b.pop(0)
    print(B)

    # Multiply pi and A
    resPiA = []
    val = 0
    for i in range(Acols):
        for j in range(Arows):
            val += A[j][i] * pi[j]
        resPiA.append(val)
        val = 0
    print(resPiA)

    resB = []
    for i in range(Bcols):
        for j in range(Brows):
            val += B[j][i] * resPiA[j]
        resB.append(val)
        val = 0
    print(resB)

    finalOutput = "1 "
    finalOutput += str(Bcols)
    for element in resB:
        finalOutput += " " + str(element)
    print(finalOutput)


if __name__ == "__main__":
    main()
