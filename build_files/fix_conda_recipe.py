import sys

with open(sys.argv[1]) as f:
    ilines = f.readlines()

print('Read {} lines'.format(len(ilines)))

processing = False
olines = []

for x in ilines:
    if processing:
        if x == 'build:\n':
            olines.append(x)

            processing = False

        continue

    if x == 'source:\n':
        olines.append(x)
        olines.append('  path: {}\n\n'.format(sys.argv[2]))

        processing = True
    elif 'number:' in x:
        olines.append('  number: 0\n')
    else:
        olines.append(x)

print(sys.argv[1])

with open(sys.argv[1], 'w') as f:
    f.writelines(olines)
