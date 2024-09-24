with open('ctu/ctu_new/val.out', mode='r',encoding="utf-8") as f:
    lines = f.readlines()
    longest_line = max(lines, key=len)
    shortest_line=min(lines,key=len)
    print('The longest len is:', len(longest_line))
    print('The shortest len is:', len(shortest_line))