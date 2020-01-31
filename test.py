def global_test():
    global name
    global new_name
    name = 'a'

    print(name)

    new_name=name
    name = 'b'
    print(new_name)
    print(name)
    return 0


print(global_test())