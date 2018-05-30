import sys

n = 1000000

'''
for i in range(n):
  sys.stdout.write('\r')
  percent = 100*i/(max(n-1,1))
  sys.stdout.write("[%-50s] %d%%" % ('='*int((percent/2)), percent))
  #sys.stdout.write("[%-20s] %d%%" % ('='*int((percent/5)), percent))
  sys.stdout.flush()
sys.stdout.write('\n')
'''


def progress_bar(i,n):
  sys.stdout.write('\r')
  percent = 100*i/(max(n-1,1))
  sys.stdout.write("[%-50s] %d%%" % ('+'*int((percent/2)), percent))
  sys.stdout.flush()

# tests the progress bar
for i in range(n):
  progress_bar(i,n)
print(' ')
