def trim(s):
    # replace multi space, tab and new line by space
    # return string
    new_str = s.replace("\n", " ").replace("\r\n", " ")
    new_str = ' '.join(new_str.split())
    new_str = new_str.strip()
    return new_str


def convert_data(data):
    # convert list data string to dict of int
    # return dict
    dataset = dict()
    for d in data:
        ds = d.split()
        if len(ds) == 3:
            if ds[0].isnumeric() and ds[1].isnumeric() and ds[2].isnumeric():
                a = dict()
                a['x'] = int(ds[1])
                a['y'] = int(ds[2])
                dataset[int(ds[0])] = a
        if len(ds) == 2:
            if ds[0].isnumeric() and ds[1].isnumeric():
                dataset[int(ds[0])]['d'] = int(ds[1])
    return dataset


def read_dataset(filename="A/A-n9-k2.vrp"):
    # read file and convert data to dict
    # return data as dict
    path = f"./data/{filename}"
    path = path.format(filename=filename)
    with open(path, 'r') as f:
        lines = f.readlines()
    data = []
    for line in lines:
        striped = trim(line)
        data.append(striped)
    dataset = convert_data(data)
    return dataset


if __name__ == "__main__":
    data = read_dataset('A/A-n32-k5.vrp')
    print(data)
