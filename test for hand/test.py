for i in range(1, len(triangle)):
    for j in range(len(triangle[i])):
        if j == 0:
            triangle[i][j] += triangle[i-1][j]
        elif j == len(triangle[i]) -1:
            triangle[i][j] += triangle[i-1][j-1]
        else:
            l = j-1
            r = j
            triangle[i][j] += max(triangle[i-1][l], triangle[i-1][r])