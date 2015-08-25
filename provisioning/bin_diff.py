import sys, os, pickle, time
    
readsz = 1024

try:
    action = sys.argv[1]
    f1 = sys.argv[2]
    f2 = sys.argv[3]
except:
    print "Usage {} calc|apply <file1> <file2>".format(sys.argv[0])
    exit(1)

if(action == 'calc'):
    start = time.time()
    print "Calculating diff between: {} and {}".format(f1, f2)

    fp1 = open(f1, 'rb')
    fp2 = open(f2, 'rb')

    i = 0
    same = 0
    diff = 0

    changes = {}

    # Assume same size for now
    while(True):
        b1 = fp1.read(readsz)
        b2 = fp2.read(readsz)
        if(not b1 or not b2):
            break
        if(len(b1) != readsz or len(b2) != readsz):
            print "Diff size: {}, {}".format(len(b1), len(b2))
        
        h1 = hash(b1)
        h2 = hash(b2)
        if(h1 != h2):
            diff += 1
            changes[i] = b2
            #print([ord(b) for b in b1])
        else:
            same += 1
        i += 1

    fp1.close()
    fp2.close()

    pickle.dump(changes, open('changes.pk', 'wb'))

    print "Done same: {}, diff: {}".format(same, diff)
    print "Operation took: {}".format(time.time() - start)

elif(action == 'apply'):
    start = time.time()
    print "Applying changes from {} into {}".format(f1, f2)
    
    changes = pickle.load(open('changes.pk', 'rb'))
    
    fp1 = open(f1, 'rb')
    fp2 = open(f2, 'wb')

    i = 0

    # Assume same size for now
    while(True):
        b1 = fp1.read(readsz)
        if(not b1):
            break
        if(len(b1) != readsz):
            print "Diff size: {}".format(len(b1))
        
        # Apply diff
        if(i in changes):
            fp2.write(changes[i])
        else:
            fp2.write(b1)
        i += 1

    fp1.close()
    fp2.close()
    print "Done applying changes, check {}".format(f2)
    print "Operation took: {}".format(time.time() - start)
        
