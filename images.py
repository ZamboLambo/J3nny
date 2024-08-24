from base64 import b64decode
from PIL import Image
from io import BytesIO
from os import remove
from tkinter import PhotoImage
     #b64 stupid hack needed to make a onefile with images all in it

def startIcon():
    filename = "start.png"
    temp = Image.open(BytesIO(b64decode("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"
        )))
    temp.thumbnail((30,30),Image.Resampling.LANCZOS)
    temp.save(filename)
    startIco = PhotoImage(file=filename)
    remove(filename)
    return startIco

def pauseIcon():
    filename = "stop.png"
    temp = Image.open(BytesIO(b64decode("iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAABbmlDQ1BpY2MAACiRdZHPKwRhGMc/Bq1YOZCEw6ZdOVCi5Mg67GWTFmVx2R0zu2p3dprZTZurcnHYchAXvw7+A67KlVKKlOTo7NdFGs9r1Uq77/TO8+n7vt+nZ74DWjSjZ92GCchaeScWCQcW4osB3zMaPXQSoi+hu/bkzEyUmuvjljpVb4ZUr9r3qq6WFcPVoa5JeEy3nbywTEN0LW8r3hLu0NOJFeED4UFHBhS+VHqyzE+KU2V+U+zMxaZAUz0DqT+c/MN62skKDwgHs5mC/juP+hK/Yc3PSu2W3YtLjAhhAiQpsEqGPENSLcmsum/4xzdNTjy6vG2KOOJIkRbvoKgF6WpINUU35MlQVLn/z9M1R0fK3f1haHz0vNcQ+Lbhq+R5n4ee93UE9Q9wblX8Oclp/F30UkUL7kPbBpxeVLTkDpxtQte9nXASP1K9bM004eUEWuPQfg3NS+Wsfs85voO5dflFV7C7B/1yv235Gz5SaCYC2B3kAAAACXBIWXMAAA7DAAAOwwHHb6hkAAAB8UlEQVR4Xu3cvy4EYRSG8eNPrUAjCkSp0KjdgrgHiU4icQUacRsiUSs0GpVEQUMhKo2OBBVBcE7WZuXbsDv7zcg79vklbzObWbMeq/zMAAAAAAAAAAAAAAB9Yti34bvyvfreC+zOt+ebsXwDvlXfhe/F2n/Wb7v37fvm7B/Y9H18Lf2gnda879w3bnnWrPV+RZ+lec+1b8pq7tGK/wLSxf3r1rtR342V8xzbVrHB9ELJRqzxQXItpBcKmPZNWP5zxP0r6cWyVR2kLEPphQLK/IzxbatUmQ/bD3K/ZR0RRAxBxBBEDEHEEEQMQcQQRAxBxBBEDEHEEEQMQcQQRAxBxBBEDEHEEEQMQcQQRAxBxBBEDEHEEEQMQcQQRAxBxBBEDEHEEEQMQcQQRAxBxBBEDEHEEEQMQcQQRAxBxBBEDEHEEEQMQcQQRAxBxBBEDEHEEEQMQcQQRAxBxNQlSJy726u4N+f+78p6nx9VHaSsMwpv0wsFPPieLf+XGfcfpRfr5sTyzsuNe998i9a7ONH0wPKfI7ZkNTfvu7TWByq6J2scVZ5r1ndq7e/f7eKY9C2r/j9K9te4G3FM+LI1zl4fs8ZfXCfxXHHe+q7vLHmtV3Goc/yFx3NMWnfPEQEOfTu+4+Q1AAAAAAAAAAAAAADwhz4B9aO7n4H551UAAAAASUVORK5CYII="       
    )))
    temp.thumbnail((30,30),Image.Resampling.LANCZOS)
    temp.save(filename)
    stopIco = PhotoImage(file=filename)
    remove(filename)
    return stopIco

def j3nnySleepIcon():
    filename = "jsleep.png"
    temp = Image.open(BytesIO(b64decode(""       
    )))
    temp.thumbnail((30,30),Image.Resampling.LANCZOS)
    temp.save(filename)
    Ico = PhotoImage(file=filename)
    remove(filename)
    return Ico

def j3nnyStoppIcon():
    filename = "jstop.png"
    temp = Image.open(BytesIO(b64decode(""       
    )))
    temp.thumbnail((30,30),Image.Resampling.LANCZOS)
    temp.save(filename)
    Ico = PhotoImage(file=filename)
    remove(filename)
    return Ico

def j3nnyActiveIcon():
    filename = "jactive.png"
    temp = Image.open(BytesIO(b64decode(""       
    )))
    temp.thumbnail((30,30),Image.Resampling.LANCZOS)
    temp.save(filename)
    Ico = PhotoImage(file=filename)
    remove(filename)
    return Ico