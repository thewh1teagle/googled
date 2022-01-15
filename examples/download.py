from googled import Drive
import random


p = Drive()
files = p.listFiles(show_output=True)
f = random.choice(files)
p.downloadFile( f['id'], f['name'] )
