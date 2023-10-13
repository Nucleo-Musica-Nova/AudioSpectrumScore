import os
import numpy as np

import loristrck # Partial tracking

from neoscore.common import neoscore
from neoscore.core.units import ZERO, Mm
from neoscore.western.chordrest import Chordrest
from neoscore.western.clef import Clef
from neoscore.western.staff import Staff
from neoscore.western.chordrest import NoteheadTable

import music21

# make dir pictures
if not os.path.exists("pictures"):
    os.makedirs("pictures")


np.set_printoptions(suppress=True,
   formatter={'float_kind':'{:f}'.format})

NOTEHEADMINOR = NoteheadTable(
        "noteheadBlackSmall",
        "noteheadBlackSmall",
        "noteheadBlackSmall",
        "noteheadBlackSmall")

NOTEHEADBIGGER = NoteheadTable(
        "noteheadRoundBlackLarge",
        "noteheadRoundBlackLarge",
        "noteheadRoundBlackLarge",
        "noteheadRoundBlackLarge")


class picturePartials:
    def __init__(self):
        self.partials = []
        self.ampHigherFreq = 0
        self.ampValue = 0
        self.index = 0

    def __repr__(self) -> str:
        return f"Partials: {self.index}"

class sound2score:
    def __init__(self, audiofile):
        self.audiofile = audiofile
        self.scoreWidth = 600
        self.approx = 100
        self.step = 100
        self.alteracaominima = 5
        self.pngfile = audiofile[:-4] + ".png"
        pictureFile = os.path.join("pictures", self.pngfile)
        if os.path.exists(pictureFile):
            return
        self.partialtracking()
        self.generateScoreInTime()

    def partialtracking(self):
        samples, sr = loristrck.util.sndreadmono(self.audiofile)
        partials = loristrck.analyze(samples, sr, resolution=60)
        selected, _ = loristrck.util.select(partials, mindur=0.02, minamp=-40)
        self.partials = selected
        self.audioLength = len(samples) / sr

    def generateScoreInTime(self):
        neoscore.setup()
        POSITION = (Mm(0), Mm(0))
        staff = Staff(POSITION, None, Mm(self.scoreWidth))
        staff.unit(7)
        Clef(ZERO, staff, 'treble')
        total = len(self.partials)
        onsets = list(range(0, int(self.audioLength * 1000), self.step))
        allPartials = []
        for partial in self.partials:
            total -= 1
            alreadyAdded = []
            for onset in enumerate(onsets):
                # allPartials is a list of picturePartials, find the picturePartials that has the same index as the current onset
                partialPictures = next((x for x in allPartials if x.index == onset[0]), None)
                closestPartial = min(partial, key=lambda sublist: abs((sublist[0] * 1000) - onset[1]))
                distance = (closestPartial[0] * 1000) - onset[1]
                if distance < 30 and distance > 0 and onset not in alreadyAdded:
                    if partialPictures is None:
                        partialPictures = picturePartials()
                        partialPictures.index = onset[0]
                        allPartials.append(partialPictures)
                    partialPictures.partials.append(closestPartial.tolist())
                    alreadyAdded.append(onset[1])
                    if partialPictures.ampValue < closestPartial[2]:
                        partialPictures.ampValue = closestPartial[2]
                        partialPictures.ampHigherFreq = closestPartial[1]
                    
        first = False
        for partial in allPartials:
            highestFreq = partial.ampHigherFreq
            for picture in partial.partials:
                midiTemp = self.f2mc(picture[1])
                position = int(((picture[0] / self.audioLength) * (self.scoreWidth - 20)) + 10)
                mynote = [self.getPitch(midiTemp)]
                if midiTemp > 8400:
                    rightStaff = staff
                else:
                    rightStaff = staff

                if picture[1] == highestFreq and not first:
                    Chordrest(Mm(position), rightStaff, mynote, 
                              (int(1), int(1)), table=NOTEHEADBIGGER)
                    first = True
                else:
                    Chordrest(Mm(position), rightStaff, mynote, 
                              (int(1), int(1)), table=NOTEHEADMINOR)
        
        pictureFile = os.path.join("pictures", self.pngfile)
        if not os.path.exists(os.path.dirname(pictureFile)):
            os.makedirs(os.path.dirname(pictureFile))

        neoscore.render_image(
            rect=None,
            dest=pictureFile,
            wait=True,
            dpi=600)

        neoscore.shutdown()


    def getPitch(self, midi):
        midi = round(midi)
        cents = str(midi)[-2:]
        midinote = str(midi)[:-2]
        midiTempClass = music21.pitch.Pitch((int(midinote) % 12) + 60).pitchClass
        pitch = music21.pitch.Pitch(int(midinote))
        octave = pitch.octave
        noSharpNote = music21.pitch.Pitch(pitch.nameWithOctave[0].lower() + '4').midi
        majorAcc = ((midiTempClass + 60) - noSharpNote) * 100
        finalnote = music21.pitch.Pitch(midiTempClass + 60)
        if '-' in finalnote.name:
            finalnote = finalnote.getEnharmonic()
            if finalnote is not None:
                majorAcc = abs(majorAcc)
        
        totalAcc = majorAcc + int(cents)

        if totalAcc >= 0 and totalAcc < 12.5:
            accidental = ''
        elif totalAcc >= 12.5 and totalAcc < 37.5:
            accidental = 'accidentalArrowUp'
        elif totalAcc >= 37.5 and totalAcc < 62.5:
            accidental = 'accidentalQuarterToneSharpStein'
        elif totalAcc >= 62.5 and totalAcc < 87.5:
            accidental = 'accidentalHalfSharpArrowUp'
        elif totalAcc >= 87.5 and totalAcc < 112.5:
            accidental = 'accidentalSharp'
        elif totalAcc >= 112.5 and totalAcc < 137.5:
            accidental = 'accidentalThreeQuarterTonesSharpArrowUp'
        elif totalAcc >= 137.5 and totalAcc < 162.5:
            accidental = 'accidentalThreeQuarterTonesSharpStein'
        elif totalAcc >= 162.5 and totalAcc < 187.5:
            accidental = 'accidentalOneAndAHalfSharpsArrowUp'
        elif totalAcc >= 187.5 and totalAcc < 200:
            accidental = ''
            finalnote = music21.pitch.Pitch(midiTempClass + 2 + 60)
            if '-' in finalnote.name:
                finalnote = finalnote.getEnharmonic()
                if finalnote is not None:
                    majorAcc = abs(majorAcc)
        elif totalAcc >= 200 and totalAcc < 225:
            print("Error: MajorAcc is too high")
            exit()
        else:
            print("Error: MajorAcc is too high")
            exit()

        pitchName = finalnote.name[0]
        note = [pitchName.lower(), accidental, octave]
        return tuple(note)

            
    def f2mc(self, freq):
        ref_pitch = 440 
        diferenca_com_A4 =  6900 + (np.log(abs(freq / ref_pitch)) / np.log(2)) * 1200
        return round(diferenca_com_A4, 2)


def process_file(file_path):
    print(f"\033[92mProcessing file: {file_path}\033[0m")
    sound2score(file_path)



if __name__ == '__main__':
    wav_file_paths = []
    for root, dirs, files in os.walk("."):
        for filename in files:
            if filename.endswith(".wav") or filename.endswith(".aif") or filename.endswith(".aiff"):
                completepath = os.path.join(root, filename)
                process_file(completepath)



