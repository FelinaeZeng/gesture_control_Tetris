from tkinter import Canvas,Tk,Button,Label,DISABLED,messagebox
from time import sleep
from random import randrange
from numpy import array
import cv2
from keras.models import load_model


class cubegame:
    def __init__(self):
        self.my_model = load_model('my_model.h5')
        self.cap = cv2.VideoCapture(0)
        self.color = ['red', 'orange', 'yellow', 'purple', 'blue', 'green', 'pink']
        self.shapeDict = {1: [(0, 0), (0, -1), (0, -2), (0, 1)],  # shape I
                          2: [(0, 0), (0, -1), (1, -1), (1, 0)],  # shape O
                          3: [(0, 0), (-1, 0), (0, -1), (1, 0)],  # shape T
                          4: [(0, 0), (0, -1), (1, 0), (2, 0)],  # shape J
                          5: [(0, 0), (0, -1), (-1, 0), (-2, 0)],  # shape L
                          6: [(0, 0), (0, -1), (-1, -1), (1, 0)],  # shape Z
                          7: [(0, 0), (-1, 0), (0, -1), (1, -1)]}  # shape S

        self.rotateDict = {(0, 0): (0, 0), (0, 1): (-1, 0), (0, 2): (-2, 0), (0, -1): (1, 0),
                           (0, -2): (2, 0), (1, 0): (0, 1), (2, 0): (0, 2), (-1, 0): (0, -1),
                           (-2, 0): (0, -2), (1, 1): (-1, 1), (-1, 1): (-1, -1),
                           (-1, -1): (1, -1), (1, -1): (1, 1)}

        self.coreLocation = [4, -2]
        self.height, self.width = 20, 10
        self.size = 32

        self.map = {}
        # set0
        for i in range(self.width):
            for j in range(-4, self.height):
                self.map[(i, j)] = 0
        # boundary
        for i in range(-4, self.width + 4):
            self.map[(i, self.height)] = 1
        for j in range(-4, self.height + 4):
            for i in range(-4, 0):
                self.map[(i, j)] = 1
        for j in range(-4, self.height + 4):
            for i in range(self.width, self.width + 4):
                self.map[(i, j)] = 1

        # score0
        self.score = 0
        self.isFaster = False
        # GUI
        self.root = Tk()
        self.root.title("game")
        self.root.geometry("500x645")
        self.area = Canvas(self.root, width=320, height=640, bg='white')
        self.area.grid(row=2)
        self.pauseBut = Button(self.root, text="Pause", height=2, width=13, font=(18), command=self.isPause)
        self.pauseBut.place(x=340, y=100)
        self.startBut = Button(self.root, text="Start", height=2, width=13, font=(18), command=self.play)
        self.startBut.place(x=340, y=20)
        self.restartBut = Button(self.root, text="Restart", height=2, width=13, font=(18), command=self.isRestart)
        self.restartBut.place(x=340, y=180)
        self.quitBut = Button(self.root, text="Quit", height=2, width=13, font=(18), command=self.isQuit)
        self.quitBut.place(x=340, y=260)
        self.scoreLabel1 = Label(self.root, text="Score:", font=(24))
        self.scoreLabel1.place(x=340, y=600)
        self.scoreLabel2 = Label(self.root, text="0", fg='red', font=(24))
        self.scoreLabel2.place(x=410, y=600)

        self.area.focus_set()

    def capture(self):
        avg = 0
        for i in range(5):
            ret, frame = self.cap.read()
            x0 = 400
            y0 = 200
            height = 200
            width = 200
            skinkernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (640, 480))

            low_range = array([0, 50, 80])
            upper_range = array([30, 200, 255])

            cv2.rectangle(frame, (x0, y0), (x0 + width, y0 + height), (0, 255, 0), 1)
            roi = frame[y0:y0 + height, x0:x0 + width]

            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

            # Apply skin color range
            mask = cv2.inRange(hsv, low_range, upper_range)

            # erase edge and noise
            mask = cv2.erode(mask, skinkernel, iterations=1)
            mask = cv2.dilate(mask, skinkernel, iterations=1)

            # blur
            mask = cv2.GaussianBlur(mask, (15, 15), 1)

            # bitwise and mask original frame
            res = cv2.bitwise_and(roi, roi, mask=mask)
            cv2.imshow("result", res)
            cv2.waitKey(10)

            # reshape picture

            img = cv2.resize(res, (140, 140))
            image = array(img).flatten()
            image = image.reshape(140, 140, 3)
            image = image.astype('float32')
            image = image / 255
            rimage = image.reshape(1, 140, 140, 3)

            y = self.my_model.predict_classes(rimage)

            avg += y[0]

        return (avg//5)

    def getLocation(self):
        map[(core[0], core[1])] = 1
        for i in range(4):
            map[((core[0] + getNew[i][0]),
                 (core[1] + getNew[i][1]))] = 1

    def canMove(self):
        for i in range(4):
            if map[(core[0] + getNew[i][0]), (core[1] + 1 + getNew[i][1])] == 1:
                return False
        return True


    def drawNew(self):
        global next
        global getNew
        global core
        next = randrange(1, 8)
        self.getNew = self.shapeDict[next]
        getNew = self.getNew
        core = [4, -2]
        time = 0.5
        while self.canMove():
            if isPause:
                core[1] += 1
                self.drawSquare()
                if self.isFaster:
                    sleep(time - 0.15)
                else:
                    sleep(time + 0.22)
                self.isFaster = False
            else:
                self.drawSquare()
                sleep(time)
        self.getLocation()

    def drawSquare(self):
        self.area.delete("new")
        self.calcu()
        for i in range(4):
            self.area.create_rectangle((core[0] + self.getNew[i][0]) * self.size,
                                       (core[1] + self.getNew[i][1]) * self.size,
                                       (core[0] + self.getNew[i][0] + 1) * self.size,
                                       (core[1] + self.getNew[i][1] + 1) * self.size,
                                       fill=self.color[next - 1], tags="new")
        self.area.update()

    def drawSquarenew(self):
        self.area.delete("new")

        for i in range(4):
            self.area.create_rectangle((core[0] + self.getNew[i][0]) * self.size,
                                       (core[1] + self.getNew[i][1]) * self.size,
                                       (core[0] + self.getNew[i][0] + 1) * self.size,
                                       (core[1] + self.getNew[i][1] + 1) * self.size,
                                       fill=self.color[next - 1], tags="new")
        self.area.update()

    def drawBottom(self):
        for j in range(self.height):
            self.area.delete('bottom' + str(j))
            for i in range(self.width):
                if map[(i, j)] == 1:
                    self.area.create_rectangle(self.size * i, self.size * j, self.size * (i + 1),
                                               self.size * (j + 1), fill='grey', tags='bottom' + str(j))
            self.area.update()

    def isFill(self):
        for j in range(self.height):
            t = 0
            for i in range(self.width):
                if map[(i, j)] == 1:
                    t = t + 1
            if t == self.width:
                self.getScore()
                self.deleteLine(j)

    # add
    def getScore(self):
        scoreValue = eval(self.scoreLabel2['text'])
        scoreValue += 10
        self.scoreLabel2.config(text=str(scoreValue))

    # cancel
    def deleteLine(self, j):
        for t in range(j, 2, -1):
            for i in range(self.width):
                map[(i, t)] = map[(i, t - 1)]
        for i in range(self.width):
            map[(i, 0)] = 0
        self.drawBottom()

    def isOver(self):
        t = 0
        for j in range(self.height):
            for i in range(self.width):
                if self.map[(i, j)] == 1:
                    t += 1
                    break
        if t >= self.height:
            return False
        else:
            return True


    def canRotate(self):
        for i in range(4):
            map[((core[0] + getNew[i][0]),
                 (core[1] + getNew[i][1]))] = 0
        for i in range(4):
            if map[((core[0] + self.rotateDict[getNew[i]][0]),
                    (core[1] + self.rotateDict[getNew[i]][1]))] == 1:
                return False
        return True

    # rotate
    def rotate(self):
        if next != 2:
            if self.canRotate():
                for i in range(4):
                    getNew[i] = self.rotateDict[getNew[i]]
                self.drawSquarenew()
        if not self.canMove():
            for i in range(4):
                map[((core[0] + getNew[i][0]), (core[1] + getNew[i][1]))] = 1


    def canLeft(self):
        coreNow = core
        for i in range(4):
            map[((coreNow[0] + getNew[i][0]), (coreNow[1] + getNew[i][1]))] = 0
        for i in range(4):
            if map[((coreNow[0] + getNew[i][0] - 1), (coreNow[1] + getNew[i][1]))] == 1:
                return False
        return True

    def moveLeft(self):
        if self.canLeft():
            core[0] -= 1
            self.drawSquarenew()
            self.drawBottom()
        if not self.canMove():
            for i in range(4):
                map[((core[0] + getNew[i][0]), (core[1] + getNew[i][1]))] = 1

    def canRight(self):
        for i in range(4):
            map[((core[0] + getNew[i][0]), (core[1] + getNew[i][1]))] = 0
        for i in range(4):
            if map[((core[0] + getNew[i][0] + 1), (core[1] + getNew[i][1]))] == 1:
                return False
        return True

    def moveRight(self):
        if self.canRight():
            core[0] += 1
            self.drawSquarenew()
            self.drawBottom()
        if not self.canMove():
            for i in range(4):
                map[((core[0] + getNew[i][0]), (core[1] + getNew[i][1]))] = 1

    def moveFaster(self):
        self.isFaster = True
        if not self.canMove():
            for i in range(4):
                map[((core[0] + getNew[i][0]), (core[1] + getNew[i][1]))] = 1


    def run(self):
        self.isFill()
        self.drawNew()
        self.drawBottom()
    def calcu(self):
        move = self.capture()
        if move == 1:
            self.moveLeft()
        elif move == 2:
            self.moveRight()
        elif move == 3:
            self.rotate()
        elif move == 4:
            self.moveFaster()

    def play(self):
        self.startBut.config(state=DISABLED)
        global isPause
        isPause = True
        global map
        map = self.map
        while True:
            if self.isOver():
                self.run()
            else:
                break
        self.over()

    def restart(self):
        self.core = [4, -2]
        self.map = {}
        for i in range(self.width):
            for j in range(-4, self.height):
                self.map[(i, j)] = 0
        for i in range(-1, self.width):
            self.map[(i, self.height)] = 1
        for j in range(-4, self.height + 1):
            self.map[(-1, j)] = 1
            self.map[(self.width, j)] = 1
        self.score = 0
        self.t = 0.07
        for j in range(self.height):
            self.area.delete('bottom' + str(j))
        self.play()

    def over(self):
        feedback = messagebox.askquestion("game over","Do you want to restart?")
        if feedback == 'yes':
            self.restart()
        else:
            self.root.destroy()

    def isQuit(self):
        askQuit = messagebox.askquestion("Quit", "Are you sure to quit?")
        if askQuit == 'yes':
            self.root.destroy()
            exit()

    def isRestart(self):
        askRestart = messagebox.askquestion("Restart", "Are you sure to restart?")
        if askRestart == 'yes':
            self.restart()
        else:
            return

    def isPause(self):
        global isPause
        isPause = not isPause
        if not isPause:
            self.pauseBut["text"] = "Resume"
        else:
            self.pauseBut["text"] = "Pause"



    def mainloop(self):
        self.root.mainloop()




if __name__ == '__main__':

    cube = cubegame()
    cube.mainloop()




