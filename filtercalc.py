from math import *

print("please let me go to bed")

def getNum(text):
    return float(input(text + ": "))

# b from equation, wct is target frequency in rad/s, desc is the capacitance
def calcLP(b, fct, desc, printer=False):
    # Prototype values
    wc = 1 # rad/sc
    c = 1 # F
    w0 = 1

    wct = fct * 2 * pi

    r1 = ((1/b) + sqrt(((1/b) ** 2) + 4)) / 2
    r2 = 1 / r1

    if printer:
        print(f"R1: {r1:.3g}\tR2: {r2:.3g}")

    # Calculate scale factors
    kf = wct / w0
    km = c / (desc * kf)
    if printer:
        print(f"km: {km:.3g}\tkf: {kf:.3g}")

    # Calculating the scaled values
    r1p = km * r1
    r2p = km * r2
    cp = c / (km * kf)

    # Returns the scaled R1, R2, C
    return (r1p, r2p, cp)

def calcBP(minf, maxf, desc, printer=False):
    # Convert the frequencies to rad/s
    minw = minf * 2 * pi
    maxw = maxf * 2 * pi
    if printer:
        print(f"minw: {minw:.3g}\tmaxw: {maxw:.3g}")

    # Calculate the bandwidth, center radian frequency, and quality
    bw = maxw - minw
    ctrw = minw + (bw / 2)
    q = bw / ctrw
    if printer:
        print(f"bw: {bw:.3g}\tcw: {ctrw:.3g}\tq: {q:.3g}")

    # Make a prototype circuit
    w0 = 1 # prototype frequency 1 rad/sec
    c = 2 * q
    r1 = 1 # ohm
    r2 = 2 * r1
    r3 = 1 / ( 2 * (c ** 2) - 1)
    if printer:
        print(f"w0: {w0:.3g}\tc: {c:.3g}\tr1: {r1:.3g}\tr2: {r2:.3g}\t {r3:.3g}")

    # Calculate scale factors
    kf = ctrw / w0
    km = c / (desc * kf)
    if printer:
        print(f"km: {km:.3g}\tkf: {kf:.3g}")

    # Calculating the scaled values
    r1p = km * r1
    r2p = km * r2
    r3p = km * r3
    cp = c / (km * kf)

    # Return the 3 resistors and the capacitor value
    return (r1p, r2p, r3p, cp)

def doThingy():
    intxt = ""
    while len(intxt) <= 0 or intxt[0] not in "hHlLbB":
        intxt = input("Filter type (H|L|B): ")

    if intxt[0] in "hH":
        print("No, you don't want to do high pass")
    elif intxt[0] in "bB":
        # Sallen key bandpass

        # Ask the user for the frequencies they want
        minf = getNum("Min freq [hz]")
        maxf = getNum("Max freq [hz]")

        # Ask the user what capacitor they want to use
        desc = getNum("Cap value")

        r1p, r2p, r3p, cp = calcBP(minf, maxf, desc)

        # RESULTS!
        print(f"Your values are c: {cp:.3g}\tr1: {r1p:.3g}\tr2: {r2p:.3g}\tr3: {r3p:.3g}")

    elif intxt[0] in "lL":
        # Low pass sallen-key circuit
        # Assummes r1=r2
        b = (0.581, sqrt(2), 1.932)

        # Ask the user for the frequencies they want
        maxf = getNum("Max freq [hz]")

        # Ask the user what capacitor they want to use
        desc = getNum("Cap value")

        # Calculate the 3 stages
        for bv in b:
            r1, r2, c = calcLP(bv, maxf, desc)
            print(f"Your values are r1':{r1:.3g}\tr2'{r2:.3g}\tc'{c:.3g}")

    else:
        print("How did you even get here, that's not allowed")

while True:
    doThingy();
