def LoadData(fileName):
    with open(fileName) as f:
        data = f.readlines()

    ranks = {}
    order = []
    for lines in data:
        params = lines.split(",")
        name = params[0]
        score = params[1]
        ranks[name] = float(score)
        order.append(name)

    return [ranks, order]


def GetAvgRank(name, ranks, num_files):
    sum = 0
    for i in xrange(0, num_files):
        if name in ranks[i]:
            sum += ranks[i][name]
    return sum / num_files


def CheckSeenAll(seen, name, num_files):
    for i in xrange(0, num_files):
        if (name not in seen[i]):
            return False
    return True


def isScanFinished(iter, order, num_files):
    for i in xrange(0, num_files):
        if len(order[i]) > iter:
            return False
    return True


def FaginAlg(data, num_files):
    # Setup
    seen = {}
    order = {}
    ranks = {}

    for i in xrange(0, num_files):
        seen[i] = {}
        ranks[i] = data[i][0]
        order[i] = data[i][1]

    seen_all = {}
    ranks_aggr = {}
    iter = 0
    stop = False

    # Work
    while not stop:
        # Check if already scanned through all files
        if isScanFinished(iter, order, num_files):
            stop = True
            break

        for i in xrange(0, num_files):
            # Check if scanned through all current file
            if len(order[i]) < iter:
                continue
            # Get the file name from each file according to iteration position
            entry_name = order[i][iter]
            # Calculate it's avg rank and store it
            ranks_aggr[entry_name] = GetAvgRank(entry_name, ranks, num_files)
            # Mark as seen
            seen[i][entry_name] = 1
            # Check for seen all
            if CheckSeenAll(seen, entry_name, num_files):
                seen_all[entry_name] = ranks_aggr[entry_name]

        iter += 1
    return sorted(ranks_aggr.items(), key=lambda x: x[1], reverse=True)


def GenFaginAlg(files):
    data = {}
    num_files = 0
    for file_name in files:
        file_data = LoadData(file_name)
        data[num_files] = {}
        data[num_files][0] = file_data[0]
        data[num_files][1] = file_data[1]
        num_files += 1
    print("** Result **")
    print(FaginAlg(data, len(files)))


GenFaginAlg(["data1.csv", "data2.csv", "data3.csv"])
