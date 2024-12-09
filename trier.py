total_mis = []

for i in range(1, 13):
    
    print('Week:', i)

    with open(f'testtrier/Python/spends_{i}.csv', 'r') as py, open(f'testtrier/MATLAB/id_{i}.csv', 'r') as mat:
        pylines = py.readlines()
        print(len(pylines))
        matlines = mat.readlines()
        print(len(matlines))
        collect_mismatch = []
        collect_match = []
        for matline, pyline in zip(matlines, pylines):
            matline = matline.strip()
            pyline = pyline.strip()
            if matline != pyline:
                collect_mismatch.append(matline)
            else:
                collect_match.append(matline)
        
        total_mis.append(len(matline))
        
        print('Mismatches:', len(collect_mismatch))

    # print(collect_match)            
    # print(collect_mismatch)
