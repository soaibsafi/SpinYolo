import time
import glob
import cv2
import numpy as np

CONFIDENCE_THRESHOLD = 0.5
NMS_THRESHOLD = 0.4

weights = glob.glob("data/*.weights")[0]
labels = glob.glob("data/*.txt")[0]
cfg = glob.glob("data/*.cfg")[0]


lbls = list()
with open(labels, "r") as f:
	lbls = [c.strip() for c in f.readlines()]

COLORS = np.random.randint(0, 255, size=(len(lbls), 3), dtype="uint8")

net = cv2.dnn.readNetFromDarknet(cfg, weights)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

layer = net.getLayerNames()
layer = [layer[i[0] - 1] for i in net.getUnconnectedOutLayers()]

print("Using {} weights ,{} configs and {} labels.".format(weights, cfg, labels))


def detect(img):
	image = img.GetNDArray()
	(H, W) = image.shape[:2]

	blob = cv2.dnn.blobFromImage(image, 1/255, (416, 416), swapRB=True, crop=False)
	net.setInput(blob)
	start_time = time.time()
	layer_outs = net.forward(layer)
	end_time = time.time()

	boxes = list()
	confidences = list()
	class_ids = list()

	for output in layer_outs:
		for detection in output:
			scores = detection[5:]
			class_id = np.argmax(scores)
			confidence = scores[class_id]

			if confidence > CONFIDENCE_THRESHOLD:
				box = detection[0:4] * np.array([W, H, W, H])
				(center_x, center_y, width, height) = box.astype("int")

				x = int(center_x - (width / 2))
				y = int(center_y - (height / 2))

				boxes.append([x, y, int(width), int(height)])
				confidences.append(float(confidence))
				class_ids.append(class_id)
				print('%s: %s'%(class_id, confidence))

	idxs = cv2.dnn.NMSBoxes(boxes, confidences, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)
	if len(idxs) > 0:
		for i in idxs.flatten():
			(x, y) = (boxes[i][0], boxes[i][1])
			(w, h) = (boxes[i][2], boxes[i][3])

			color = [int(c) for c in COLORS[class_ids[i]]]
			cv2.rectangle(image, (x, y), (x+w, y+h), color, 2)
			text = "{}: {:.4f}".format(lbls[class_ids[i]], confidences[i])
			cv2.putText(image, text, (x, y -5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
			label = "Inference Time: {:.2f} ms".format(end_time - start_time)
			cv2.putText(image, label, (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)

	cv2.imshow("image", image)
	#cv2.waitKey(0)