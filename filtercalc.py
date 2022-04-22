from math import *

print("please let me go to bed")

intxt = ""
while len(intxt) <= 0 or intxt[0] not in "hHlLbB":
    intxt = input("Filter type (H|L|B): ")

if intxt[0] in "hH":
    print("No, you don't want to do high pass")
elif intxt[0] in "bB":
    # Sallen key bandpass
    r1p = 0
    r2p = 0
    r3p = 0
    c1p = 0
    c2p = 0
    print("No, you don't want to do band pass")
elif intxt[0] in "lL":
    # Low pass sallen-key circuit
    # Assummes r1=r2
    b0 = 0.581
    b1 = sqrt(2)
    b2 = 1.932

    def calcLP(b, wct, zt):
        wc = 1 # rad/sc
        r = 1 # ohm
        c1 = 2/b
        c2 = 1/c1

        kf = wct / wc
        km = zt / r

        rp = km * r
        c1p = c1 / (km * kf)
        c2p = c2 / (km * kf)

        # print(f"c1:{c1}\tc2{c2}")
        print(f"c1':{c1p:.3e}\tc2'{c2p:.3e}\tr'{rp:.3e}")

    for b in [b0, b1, b2]:
        calcLP(b, 100, 100)

else:
    print("How did you even get here, that's not allowed")
