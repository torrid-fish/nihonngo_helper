n = int(input())

# 右轉，左轉，迴轉
rt, lt, ut = 0, 0, 0

# 右是0，上是1，左是2，下是3
lx, ly, d = 0, 0, 0
for i in range(n):
    x, y = map(int, input().split())
    dx, dy = x - lx, y - ly
    lx, ly = x, y
    if dx == 0 and dy != 0:     # 上下移動
        if d == 0:
            rt += dy < 0
            lt += dy > 0
        elif d == 1:
            ut += dy < 0
        elif d == 2:
            rt += dy > 0
            lt += dy < 0
        else:
            ut += dy > 0
        # 更新方向
        d = 1 if dy > 0 else 3
    else:                       # 左右移動
        if d == 0:
            ut += dx < 0
        elif d == 1:
            rt += dx > 0
            lt += dx < 0
        elif d == 2:
            ut += dx > 0
        else:
            rt += dx < 0
            lt += dx > 0
        # 更新方向
        d = 0 if dx > 0 else 2   

print(lt, rt, ut)