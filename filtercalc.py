from math import *

print("please let me go to bed")

def getNum(text):
    return float(input(text + ": "))

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

        # Convert the frequencies to rad/s
        minw = minf * 2 * pi
        maxw = maxf * 2 * pi
        print(f"minw: {minw:.3g}\tmaxw: {maxw:.3g}")

        # Ask the user what capacitor they want to use
        desc = getNum("Cap value")

        # Calculate the bandwidth, center radian frequency, and quality
        bw = maxw - minw
        cw = minw + (bw / 2)
        q = bw / cw
        print(f"bw: {bw:.3g}\tcw: {cw:.3g}\tq: {q:.3g}")

        # Make a prototype circuit
        w0 = 1 # prototype frequency 1 rad/sec
        c = 2 * q
        r1 = 1 # ohm
        r2 = 2 * r1
        r3 = 1 / ( 2 * (c ** 2) - 1)
        print(f"w0: {w0:.3g}\tc: {c:.3g}\tr1: {r1:.3g}\tr2: {r2:.3g}\t {r3:.3g}")

        # Calculate scale factors
        kf = cw / w0
        km = c / (desc * kf)
        print(f"km: {km:.3g}\tkf: {kf:.3g}")

        # Calculating the scaled values
        r1p = km * r1
        r2p = km * r2
        r3p = km * r3
        cp = c / (km * kf)

        # RESULTS!
        print(f"c: {cp:.3g}\tr1: {r1p:.3g}\tr2: {r2p:.3g}\tr3: {r3p:.3g}")

    elif intxt[0] in "lL":
        # Low pass sallen-key circuit
        # Assummes r1=r2
        b0 = 0.581
        b1 = sqrt(2)
        b2 = 1.932


        # b from equation, wct is target frequency in rad/s, zt is target impedence
        def calcLP(b, wct, zt):
            # Prototype values
            wc = 1 # rad/sc
            r = 1 # ohm
            c1 = 2/b
            c2 = 1/c1

            # calculating scale factors
            kf = wct / wc
            km = zt / r

            # Calculating the scaled values
            rp = km * r
            c1p = c1 / (km * kf)
            c2p = c2 / (km * kf)

            # print(f"c1:{c1}\tc2{c2}")
            print(f"c1':{c1p:.3g}\tc2'{c2p:.3g}\tr'{rp:.3g}")

            # Returns the scaled C1, C2, and R
            return (c1p, c2p, rp)

            # Calculate the 3 stages
        for b in [b0, b1, b2]:
            calcLP(b, 100, 100)

    else:
        print("How did you even get here, that's not allowed")

while True:
    doThingy();
