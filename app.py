
# import the necessary packages
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import imutils
import cv2
import tkinter
import time
 

def midpoint(ptA, ptB):
	return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)


webcam = cv2.VideoCapture(0)
webcam.set(3, 1280)
webcam.set(4, 720)

#webcam = cv2.VideoCapture('rtsp://192.168.1.226:554/profile2/media.smp')


while(True):
        check, frame = webcam.read()
        # cv2.imwrite(filename='capture.jpg', img=frame)
        # cv2.imwrite(filename="capture.jpg")
        #webcam.release()
        image = cv2.imread('capture.jpg')




        # load the image, convert it to grayscale, and blur it slightly
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)

        # perform edge detection, then perform a dilation + erosion to
        # close gaps in between object edges
        edged = cv2.Canny(gray, 50, 100)
        edged = cv2.dilate(edged, None, iterations=1)
        edged = cv2.erode(edged, None, iterations=1)

        # find contours in the edge map
        cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        # sort the contours from left-to-right and initialize the
        # 'pixels per metric' calibration variable
        (cnts, _) = contours.sort_contours(cnts)
        pixelsPerMetric = None

        # loop over the contours individually
        for c in cnts:
                # if the contour is not sufficiently large, ignore it
                if cv2.contourArea(c) < 100:
                        continue

                # compute the rotated bounding box of the contour
                orig = image.copy()
                box = cv2.minAreaRect(c)
                box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
                box = np.array(box, dtype="int")

                # order the points in the contour such that they appear
                # in top-left, top-right, bottom-right, and bottom-left
                # order, then draw the outline of the rotated bounding
                # box
                box = perspective.order_points(box)
                cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)

                # loop over the original points and draw them
                for (x, y) in box:
                        cv2.circle(orig, (int(x), int(y)), 5, (0, 0, 255), -1)

                # unpack the ordered bounding box, then compute the midpoint
                # between the top-left and top-right coordinates, followed by
                # the midpoint between bottom-left and bottom-right coordinates
                (tl, tr, br, bl) = box
                (tltrX, tltrY) = midpoint(tl, tr)
                (blbrX, blbrY) = midpoint(bl, br)

                # compute the midpoint between the top-left and top-right points,
                # followed by the midpoint between the top-righ and bottom-right
                (tlblX, tlblY) = midpoint(tl, bl)
                (trbrX, trbrY) = midpoint(tr, br)

                # draw the midpoints on the image
                cv2.circle(orig, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
                cv2.circle(orig, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
                cv2.circle(orig, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
                cv2.circle(orig, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)

                # draw lines between the midpoints
                cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
                	(255, 0, 255), 2)
                cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),
                	(255, 0, 255), 2)

                # compute the Euclidean distance between the midpoints
                dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
                dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))

                # if the pixels per metric has not been initialized, then
                # compute it as the ratio of pixels to supplied metric
                
                if pixelsPerMetric is None:
                	pixelsPerMetric = dB / 7 # <<<<<<< SET WIDTH OF FIRST LEFT OBJECT <<<<<<<<

                # compute the size of the object
                dimA = round(dA / pixelsPerMetric, 1)
                dimB = round(dB / pixelsPerMetric, 1)
 
                # draw the object sizes on the image
                cv2.putText(orig, "{:.1f}cm".format(dimA),
                        (int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX,
                        0.65, (255, 255, 255), 2)
                cv2.putText(orig, "{:.1f}cm".format(dimB),
                        (int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX,
                        0.65, (255, 255, 255), 2)

                # show the output image
                #cv2.namedWindow("Kamera", cv2.WND_PROP_FULLSCREEN)          
                #cv2.setWindowProperty("Kamera", cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
                cv2.imshow("Cam", orig)
                key = cv2.waitKey(0)
                #if key == ord('r'):
                if key == 27:
                        break
                elif key == 13:

                        # Create a canvas windows
                        root = tkinter.Tk()
                        root.title("Dimensions")

                        canvas = tkinter.Canvas(root, width = 500, height = 200)
                        canvas.pack()
                        entry1 = tkinter.Entry (root)
                        entry1.insert(0, dimA)
                        canvas.create_window(150, 80, window=entry1)
                        entry2 = tkinter.Entry (root)
                        entry2.insert(0, dimB)
                        canvas.create_window(150, 110, window=entry2)
                        entry3 = tkinter.Entry (root)
                        canvas.create_window(150, 140, window=entry3)
                        entry3.focus_force()

                        prompt = 'Input number and hit ENTER.'
                        label1 = tkinter.Label(root, text=prompt, width=len(prompt), bg='yellow')
                        label1.pack()

                        def key(event):
                                if 'Return' == event.keysym:
                                        if entry3.get() == '':
                                                msg = 'Missing number!'
                                                label1.config(text=msg, bg='red')
                                        else:
                                                with open("output.txt", "a") as text_file:
                                                        print(entry3.get() + ';' + entry1.get() + ';' + entry2.get(), file=text_file)    
                                                print('Saved: ' + entry3.get() + ';' + entry1.get() + ';' + entry2.get())
                                                root.destroy()
                                                
                                elif 'Escape' == event.keysym:
                                        print('Canceled')
                                        root.destroy()
                                        
                        root.bind_all('<Key>', key)
                        # Run the window loop
                        root.mainloop()
                                                
                        cv2.waitKey(0)
                        


