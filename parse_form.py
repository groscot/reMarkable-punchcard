import numpy as np
import cv2
import matplotlib.pyplot as plt

### Parameters

# The reference is an empty form
reference_path = "reference.png"

# A filled form from the notebook
form_path = "Coffee Log - page 2.png"

# Show the matrix of found boxes
debug = True

# width of a square in the dotted layout
w = 43

### Helpers

class pos:
    def __init__(self,x,y): self.x = x; self.y = y

# Use these two methods to debug the extraction of a vertical/horizontal row
def show_vertical(p, img, title="Title", n=10):
    fig, axes = plt.subplots(1, n)
    for i in range(n):
        P = pos(p.x, p.y + i*w)
        axes[i].imshow(img[P.y:P.y+w,P.x:P.x+w,:])
        axes[i].axis("off")
    plt.title(title)
    plt.show()

def show_horizontal(p, img, title="Title", n=10):
    fig, axes = plt.subplots(1, n)
    for i in range(n):
        P = pos(p.x + i*w, p.y)
        axes[i].imshow(img[P.y:P.y+w,P.x:P.x+w,:])
        axes[i].axis("off")
    plt.title(title)
    plt.show()

def extract_vertical(data, img, p, key, n=10):
    res = []
    for i in range(n):
        P = pos(p.x, p.y + i*w)
        res.append(img[P.y:P.y+w,P.x:P.x+w,:])
    data[key] = res
    return data

def extract_horizontal(data, img, p, key, n=10):
    res = []
    for i in range(n):
        P = pos(p.x + i*w, p.y)
        res.append(img[P.y:P.y+w,P.x:P.x+w,:])
    data[key] = res
    return data

def extract_page(img):
    """
    This function extracts all form squares in the image
    The positions have been handcoded -- I drew the template by hand and some alignments
    are imprecise
    If you want your own form, adapt these
    """
    data = dict()

    # Coffee
    a = pos(214,423)
    data = extract_vertical(data, img, a, "Coffee")

    # Dose
    a = pos(890,423)
    b = pos(a.x, a.y + 2*w)
    data = extract_horizontal(data, img, a, "Dose")
    data = extract_horizontal(data, img, b, "Dose 2")

    # Grinder
    a = pos(891,723)
    b = pos(a.x, a.y + 2*w)
    c = pos(b.x+3, b.y + 2*w - 1)
    data = extract_horizontal(data, img, a, "Grinder 1")
    data = extract_horizontal(data, img, b, "Grinder 2")
    data = extract_horizontal(data, img, c, "Grinder 3", 4)

    # Pre s 1
    a = pos(210,1230)
    b = pos(a.x + 2*w - 4, a.y)
    c = pos(b.x + 4*w + 3, b.y)
    d = pos(c.x + 2*w - 4, c.y)
    data = extract_vertical(data, img, a, "Pre g 1")
    data = extract_vertical(data, img, b, "Pre g 2")
    data = extract_vertical(data, img, c, "Pre s 1")
    data = extract_vertical(data, img, d, "Pre s 2")

    # Final s 1
    a = pos(890,1230)
    b = pos(a.x + 2*w - 4, a.y)
    c = pos(b.x + 4*w + 3, b.y)
    d = pos(c.x + 2*w - 4, c.y)
    data = extract_vertical(data, img, a, "Final g 1")
    data = extract_vertical(data, img, b, "Final g 2")
    data = extract_vertical(data, img, c, "Final s 1")
    data = extract_vertical(data, img, d, "Final s 2")

    # Score
    a = pos(508,1745)
    data = extract_horizontal(data, img, a, "Score", 11)

    return data

### Main

img = cv2.imread(reference_path, cv2.IMREAD_COLOR)
reference = extract_page(img)

img2 = cv2.imread(form_path, cv2.IMREAD_COLOR)
data = extract_page(img2)

keys = data.keys()

if debug:
    # Display difference
    fig, axes = plt.subplots(len(keys), 11)
    for i,key in enumerate(keys):
        for j in range(len(data[key])):
            axes[i][j].imshow((data[key][j] - reference[key][j])*255)
            axes[i][j].axis("off")
        for j in range(len(data[key]), 11):
            axes[i][j].axis("off")
    plt.show()

# Read values

readings = dict()
for i,key in enumerate(keys):
    diff = [np.sum(data[key][j] - reference[key][j]) > 600 for j in range(len(data[key]))]
    read = np.where(diff)[0]
    if key == "Score":
        readings[key] = [int(v) for v in read]
    else:
        read = read[0]
        if key == "Coffee": read += 1
        readings[key] = str(read)

# Consolidate into strings -- adapt this code to export to CSV instead

def combine(values, s=""): return s.join(values)
def score(values): return np.mean(values)

print("Coffee: #", readings["Coffee"])
print("Dose:", combine([readings["Dose"], readings["Dose 2"]]), "g")
print("Grinder:", combine([readings["Grinder 1"], readings["Grinder 2"], readings["Grinder 3"]], "-"))
print("Pre-infusion:",
    combine([readings["Pre g 1"], readings["Pre g 2"]]), "g /",
    combine([readings["Pre s 1"], readings["Pre s 2"]]), "s")
print("Final:",
    combine([readings["Final g 1"], readings["Final g 2"]]), "g /",
    combine([readings["Final s 1"], readings["Final s 2"]]), "s")
print("Score:", score(readings["Score"]))
