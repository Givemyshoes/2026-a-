a = None
if a == None:
    print('a is None')

import numpy as np

object = np.zeros((1,21))
line = np.zeros((1,21))
object = np.append(object,line,axis=0)
print(object)