from .pykociemba.coordcube import CoordCube, getPruning
from .pykociemba.cubiecube import CubieCube
from .. import TurnSequence

from random import randrange, shuffle
from threading import Thread
from time import time

ax_to_s = ["U", "R", "F", "D", "L", "B"]
po_to_s = [None, " ", "2 ", "' "]

def scramble(maxDepth = 24, timeOut = 1000, useSeparator = False):
    return TurnSequence(_attemptScramble()).inverse()

def _attemptScramble(maxDepth = 24, timeOut = 1000, useSeparator = False):
    cp = list(range(8))
    shuffle(cp)
    co = [randrange(3) for i in range(7)]
    co.append((3 - sum(co) % 3) % 3)

    ep = list(range(12))
    shuffle(ep)
    eo = [randrange(2) for i in range(11)]
    eo.append(1 - (sum(eo) & 1))

    c = CubieCube(cp=cp, co=co, ep=ep, eo=eo)
    if c.edgeParity() != c.cornerParity():
        c.ep[-1], c.ep[-2] = c.ep[-2], c.ep[-1]

    flip            = [c.getFlip()] + [0] * 30  # phase1 coordinates
    twist           = [c.getTwist()] + [0] * 30
    parity          = [c.cornerParity()] + [0] * 30  # phase2 coordinates
    URFtoDLF        = [c.getURFtoDLF()] + [0] * 30
    FRtoBR          = [c.getFRtoBR()] + [0] * 30
    URtoUL          = [c.getURtoUL()] + [0] * 30
    UBtoDF          = [c.getUBtoDF()] + [0] * 30
    slice           = [FRtoBR[0] // 24] + [0] * 30

    ax              = [0] * 31  # The axis of the move
    po              = [0] * 31  # The power of the move
    URtoDF          = [0] * 31
    minDistPhase1   = [0, 1] + [0] * 29  # IDA* distance do goal estimations
    minDistPhase2   = [0] * 31

    mv = 0
    n = 0
    busy = False
    depthPhase1 = 1
    tStart = time()

    #~ print("twist %d flip %d parity %d FRtoBR %d URFtoDLF %d URtoUL %d UBtoDF %d" %\
        #~ (twist[0], flip[0], parity[0], FRtoBR[0], URFtoDLF[0], URtoUL[0], UBtoDF[0]), end='')

    # ++++++++++++++++++++ Define string thingy ++++++++++++++++++++++++++++++


    def solutionToString(length, depthPhase1=None):
        """generate the solution string from the array data"""
        s = ""
        for i in range(length):
            s += ax_to_s[ax[i]]
            s += po_to_s[po[i]]
            if depthPhase1 is not None and i == depthPhase1 - 1:
                s += ". "
        return s


    # ++++++++++++++++++++ Define phase two ++++++++++++++++++++++++++++++++++

    def totalDepth(depthPhase1, maxDepth):
        """
        Apply phase2 of algorithm and return the combined phase1 and phase2 depth. In phase2, only the moves
        U,D,R2,F2,L2 and B2 are allowed.
        """

        mv = 0
        d1 = 0
        d2 = 0
        maxDepthPhase2 = min(10, maxDepth - depthPhase1)    # Allow only max 10 moves in phase2
        for i in range(depthPhase1):
            mv = 3 * ax[i] + po[i] - 1
            URFtoDLF[i + 1] = CoordCube.URFtoDLF_Move[URFtoDLF[i]][mv]
            FRtoBR[i + 1] = CoordCube.FRtoBR_Move[FRtoBR[i]][mv]
            parity[i + 1] = CoordCube.parityMove[parity[i]][mv]

        d1 = getPruning(
            CoordCube.Slice_URFtoDLF_Parity_Prun,
            (CoordCube.N_SLICE2 * URFtoDLF[depthPhase1] + FRtoBR[depthPhase1]) * 2 + parity[depthPhase1]
        )
        if d1 > maxDepthPhase2:
            return -1

        for i in range(depthPhase1):
            mv = 3 * ax[i] + po[i] - 1
            URtoUL[i + 1] = CoordCube.URtoUL_Move[URtoUL[i]][mv]
            UBtoDF[i + 1] = CoordCube.UBtoDF_Move[UBtoDF[i]][mv]

        URtoDF[depthPhase1] = CoordCube.MergeURtoULandUBtoDF[URtoUL[depthPhase1]][UBtoDF[depthPhase1]]

        d2 = getPruning(
            CoordCube.Slice_URtoDF_Parity_Prun,
            (CoordCube.N_SLICE2 * URtoDF[depthPhase1] + FRtoBR[depthPhase1]) * 2 + parity[depthPhase1]
        )
        if d2 > maxDepthPhase2:
            return -1

        minDistPhase2[depthPhase1] = max(d1, d2)
        if minDistPhase2[depthPhase1] == 0:    # already solved
            return depthPhase1

        # now set up search

        depthPhase2 = 1
        n = depthPhase1
        busy = False
        po[depthPhase1] = 0
        ax[depthPhase1] = 0
        minDistPhase2[n + 1] = 1   # else failure for depthPhase2=1, n=0
        # +++++++++++++++++++ end initialization +++++++++++++++++++++++++++++++++

        while True:
            while True:
                if depthPhase1 + depthPhase2 - n > minDistPhase2[n + 1] and not busy:

                    if ax[n] == 0 or ax[n] == 3:    # Initialize next move
                        n += 1
                        ax[n] = 1
                        po[n] = 2
                    else:
                        n += 1
                        ax[n] = 0
                        po[n] = 1
                else:
                    if ax[n] == 0 or ax[n] == 3:
                        po[n] += 1
                        _ = (po[n] > 3)
                    else:
                        po[n] += 2
                        _ = (po[n] > 3)
                    if _:
                        while True:
                            # increment axis
                            ax[n] += 1
                            if ax[n] > 5:
                                if n == depthPhase1:
                                    if depthPhase2 >= maxDepthPhase2:
                                        return -1
                                    else:
                                        depthPhase2 += 1
                                        ax[n] = 0
                                        po[n] = 1
                                        busy = False
                                        break
                                else:
                                    n -= 1
                                    busy = True
                                    break
                            else:
                                if ax[n] == 0 or ax[n] == 3:
                                    po[n] = 1
                                else:
                                    po[n] = 2
                                busy = False

                            if not (n != depthPhase1 and (ax[n - 1] == ax[n] or ax[n - 1] - 3 == ax[n])):
                                break

                    else:
                        busy = False

                if not busy:
                    break

            # +++++++++++++ compute new coordinates and new minDist ++++++++++
            mv = 3 * ax[n] + po[n] - 1

            URFtoDLF[n + 1] = CoordCube.URFtoDLF_Move[URFtoDLF[n]][mv]
            FRtoBR[n + 1] = CoordCube.FRtoBR_Move[FRtoBR[n]][mv]
            parity[n + 1] = CoordCube.parityMove[parity[n]][mv]
            URtoDF[n + 1] = CoordCube.URtoDF_Move[URtoDF[n]][mv]

            minDistPhase2[n + 1] = max(
                getPruning(
                    CoordCube.Slice_URtoDF_Parity_Prun,
                    (CoordCube.N_SLICE2 * URtoDF[n + 1] + FRtoBR[n + 1]) * 2 + parity[n + 1]
                ),
                getPruning(
                    CoordCube.Slice_URFtoDLF_Parity_Prun,
                    (CoordCube.N_SLICE2 * URFtoDLF[n + 1] + FRtoBR[n + 1]) * 2 + parity[n + 1]
                )
            )
            # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

            if minDistPhase2[n + 1] == 0:
                break

        return depthPhase1 + depthPhase2



    # +++++++++++++++++++ Main loop ++++++++++++++++++++++++++++++++++++++++++
    while True:
        while True:
            if depthPhase1 - n > minDistPhase1[n + 1] and not busy:
                if ax[n] == 0 or ax[n] == 3:   # Initialize next move
                    n += 1
                    ax[n] = 1
                else:
                    n += 1
                    ax[n] = 0
                po[n] = 1
            else:
                po[n] += 1
                if po[n] > 3:
                    while True:
                        # increment axis
                        ax[n] += 1
                        if ax[n] > 5:

                            if timeOut > 0 and time() - tStart > timeOut:
                                return "Error 8"

                            if n == 0:
                                if depthPhase1 >= maxDepth:
                                    return "Error 7"
                                else:
                                    depthPhase1 += 1
                                    ax[n] = 0
                                    po[n] = 1
                                    busy = False
                                    break
                            else:
                                n -= 1
                                busy = True
                                break

                        else:
                            po[n] = 1
                            busy = False

                        if not (n != 0 and (ax[n - 1] == ax[n] or ax[n - 1] - 3 == ax[n])):
                            break
                else:
                    busy = False
            if not busy:
                break

        # +++++++++++++ compute new coordinates and new minDistPhase1 ++++++++++
        # if minDistPhase1 =0, the H subgroup is reached
        mv = 3 * ax[n] + po[n] - 1
        flip[n + 1] = CoordCube.flipMove[flip[n]][mv]
        twist[n + 1] = CoordCube.twistMove[twist[n]][mv]
        slice[n + 1] = CoordCube.FRtoBR_Move[slice[n] * 24][mv] // 24
        minDistPhase1[n + 1] = max(
            getPruning(
                CoordCube.Slice_Flip_Prun,
                CoordCube.N_SLICE1 * flip[n + 1] + slice[n + 1]
            ),
            getPruning(
                CoordCube.Slice_Twist_Prun,
                CoordCube.N_SLICE1 * twist[n + 1] + slice[n + 1]
            )
        )
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        if minDistPhase1[n + 1] == 0 and n >= depthPhase1 - 5:
            minDistPhase1[n + 1] = 10  # instead of 10 any value >5 is possible
            if n == depthPhase1 - 1:
                s = totalDepth(depthPhase1, maxDepth)
                if s >= 0:
                    if (s == depthPhase1
                        or (
                            ax[depthPhase1 - 1] != ax[depthPhase1]
                            and ax[depthPhase1 - 1] != ax[depthPhase1] + 3)):
                        return solutionToString(s, depthPhase1) if useSeparator else solutionToString(s)


def scrambleTime():
    from time import time
    mean = lambda arr : sum(arr)/len(arr)
    q = []
    while True:
        t = time()
        scramble()
        q.append(time()-t)
        print(q[-1])
