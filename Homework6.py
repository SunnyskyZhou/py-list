print("比大小游戏现在开始")
print("   ")

import random
computer = random.randint(1,100)
con=True
number=0

while con:
    player=int(input("请输入你猜的数字："))
    number+=1

if player == computer:
    print("猜对了！猜的数字是：",player)
    print("猜的次数是：",number)
    con=False

elif player > computer:
    print("猜错了！猜的数字大了！")

else:
    print("猜错了！猜的数字小了！")