import sys, os, cPickle, time, re
    
readsz = 4096

try:
    action = sys.argv[1]
    f1 = sys.argv[2]
    f2 = sys.argv[3]
except:
    print "Usage {} calc|apply <keyfile1> <file2>".format(sys.argv[0])
    exit(1)

if(action == 'calc'):
    start = time.time()
    print "Calculating diff between: {} and {}".format(f1, f2)

    fp1 = open(f1, 'rb')
    fp2 = open(f2, 'rb')
    keyf = open('/home/hyatt/testkeys/id_rsa')
    newkf = open('/home/hyatt/testkeys/new/id_rsa')
    key = bytearray(keyf.read())
    newKey = bytearray(newkf.read())
    if len(key) != len(newKey):
        print('Error key files don\'t match in length.')
        raise Exception("key lengths differ")

    i = 0
    same = 0
    diff = 0

    changes = {}

    # Assume same size for now
    while(True):
        b1 = bytearray(fp1.read(readsz))
        b2 = bytearray(fp2.read(readsz))
        if(not b1 or not b2):
            break
        if(len(b1) != readsz or len(b2) != readsz):
            print "Diff size: {}, {}".format(len(b1), len(b2))
        
        if(True):
            diff += 1
            if key in b1:
                print("Found key match in block: " + str(i))
                j = 0
                for byte in b1:
                    if byte == key[0]:
                        print('found match at byte ' + str(j))
                        k = j
                        match = True
                        for b in key:
                            if b != b1[k]:
                                match = False
                                break
                            k += 1
                        if match:
                            k = j
                            for b in newKey:
                                b1[k] = b
                                k += 1
                            print('Saving successful changes')
                            changes[i] = b1
                    j += 1

            #print([ord(b) for b in b1])
        else:
            same += 1
        i += 1

    fp1.close()
    fp2.close()

    cPickle.dump(changes, open('changes.pk', 'wb'),2)

    print "Done same: {}, diff: {}".format(same, diff)
    print "Operation took: {}".format(time.time() - start)

elif(action == 'apply'):
    start = time.time()
    print "Applying changes from {} into {}".format(f1, f2)
    
    changes = cPickle.load(open('changes.pk', 'rb'))
    
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
        
