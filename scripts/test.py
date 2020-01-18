# -*- coding: utf-8 -*-

test = "Bämme".encode('ascii', 'xmlcharrefreplace')
test = test.decode('utf-8')
print(test)

