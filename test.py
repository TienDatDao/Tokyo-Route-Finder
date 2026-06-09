n = int(input())

for i in range(1, n + 1):
    tong = 0
    for j in range(i, n + 1):
        tong += j

        if tong == n and j > i:
            for x in range(i, j + 1):
                print(x, end= " ")
            exit()

        if tong > n:
            break

print(n)
