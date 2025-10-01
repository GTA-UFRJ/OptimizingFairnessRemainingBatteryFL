import os

def print_dict_struct(d, save=None):        
    def print_tabs(n):
        for _ in range(n): 
            print('  ',end='')
    def print_nested_dict_keys(d:dict,n=0):
        print('{')
        for key, value in d.items():
            n+=1
            print_tabs(n)
            print(key,end=': ')
            if isinstance(value, dict):
                print_nested_dict_keys(value,n)
            else:
                print(type(value))
            n-=1
        print_tabs(n)
        print('}')
    if save:
        import sys
        s = sys.stdout
        sys.stdout = open(save,'w')
        print_nested_dict_keys(d)
        sys.stdout = s
    else:
        print_nested_dict_keys(d)