
# from kivy.app import App
# from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.button import Button
# from kivy.uix.camera import Camera
# from kivy.uix.label import Label
# from kivy.clock import Clock
# from kivy.graphics.texture import Texture

# from datetime import datetime
# import os
# import numpy as np
# from PIL import Image, ImageDraw
# import tflite_runtime.interpreter as tflite
# from android.permissions import request_permissions, Permission
# from kivy.utils import platform
# from kivy.graphics import PushMatrix, PopMatrix, Rotate
# # import tensorflow as tf
# import io

# class RotatedCamera(Camera):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         with self.canvas.before:
#             PushMatrix()
#             self.rotation = Rotate(angle=90,origin=self.center)
#         with self.canvas.after:
#             PopMatrix()
#         self.bind(size=self.update_origin, pos=self.update_origin)

#     def update_origin(self, *args):
#         self.rotation.origin = self.center


# class FaceDetectApp(App):
#     def build(self):
        
#         if platform == 'android':
#             request_permissions([
#                 Permission.CAMERA,
#                 Permission.WRITE_EXTERNAL_STORAGE,
#                 Permission.READ_EXTERNAL_STORAGE
#             ])
        
#         self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

#         # self.camera = Camera(play=False)
#         # self.camera.index = 0  # 0 = rear, 1 = front camera
#         # self.camera.resolution = (640, 480)
#         self.camera = RotatedCamera(play=False, index=1)
#         self.camera.resolution = (640, 480)

#         self.start_btn = Button(text='▶️ Start Camera', size_hint=(1, 0.15))
#         self.start_btn.bind(on_press=self.start_camera)

#         self.stop_btn = Button(text='⏹ Stop Camera', size_hint=(1, 0.15))
#         self.stop_btn.bind(on_press=self.stop_camera)
#         self.stop_btn.disabled = True

#         self.capture_btn = Button(text='📸 Capture Frame', size_hint=(1, 0.15))
#         self.capture_btn.bind(on_press=self.capture_frame)
#         self.capture_btn.disabled = True

#         self.status_label = Label(text='Status: Ready', size_hint=(1, 0.15))

#         self.layout.add_widget(self.camera)
#         self.layout.add_widget(self.start_btn)
#         self.layout.add_widget(self.stop_btn)
#         self.layout.add_widget(self.capture_btn)
#         self.layout.add_widget(self.status_label)

#         self.interpreter = tflite.Interpreter(model_path="yolov8n-face_float16.tflite")
#         self.interpreter.allocate_tensors()
#         self.input_details = self.interpreter.get_input_details()
#         self.output_details = self.interpreter.get_output_details()

#         return self.layout

#     def start_camera(self, instance):
#         self.camera.play = True
#         self.start_btn.disabled = True
#         self.stop_btn.disabled = False
#         self.capture_btn.disabled = False
#         self.status_label.text = "Status: Camera Started"
#         Clock.schedule_interval(self.detect_face_live, 1.0)

#     def stop_camera(self, instance):
#         self.camera.play = False
#         self.start_btn.disabled = False
#         self.stop_btn.disabled = True
#         self.capture_btn.disabled = True
#         self.status_label.text = "Status: Camera Stopped"
#         Clock.unschedule(self.detect_face_live)

#     def capture_frame(self, instance):
#         self.detect_face_and_save()

#     def detect_face_live(self, dt):
#         self.detect_face_and_save(live_preview=True)

#     def detect_face_and_save(self, live_preview=False):
#         if not self.camera.texture:
#             return

#         texture = self.camera.texture
#         size = texture.size
#         pixels = np.frombuffer(texture.pixels, np.uint8).reshape(size[1], size[0], 4)
#         frame = Image.fromarray(pixels[..., :3], 'RGB')
#         # Resize as usual
#         img_resized = frame.resize((self.input_details[0]['shape'][2], self.input_details[0]['shape'][1]))

#         # Convert to float32 and normalize
#         input_data = np.expand_dims(img_resized, axis=0).astype(np.float32)
#         input_data = input_data / 255.0  # Normalize pixel values

#         # Set tensor
#         self.interpreter.set_tensor(self.input_details[0]['index'], input_data)

#         self.interpreter.invoke()
#         output_raw = self.interpreter.get_tensor(self.output_details[0]['index'])[0] 
#         # output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
#         output = output_raw.T  # now should be (8400, 5)

#         detections = output
#         faces_found = False

#         draw = ImageDraw.Draw(frame)
        
#         for det in detections:
#             if det[4] > 0.1:  # confidence threshold
#                 faces_found = True
#                 x, y, w, h = det[0:4]

#                 # Scale to original image size
#                 x *= frame.width
#                 y *= frame.height
#                 w *= frame.width
#                 h *= frame.height

#                 # Calculate bounding box coordinates
#                 x1 = int(x - w / 2)
#                 y1 = int(y - h / 2)
#                 x2 = int(x + w / 2)
#                 y2 = int(y + h / 2)

#                 # Ensure box is within bounds
#                 x1, y1 = max(0, x1), max(0, y1)
#                 x2, y2 = min(frame.width, x2), min(frame.height, y2)

#                 # Draw the bounding box
#                 draw.rectangle([x1, y1, x2, y2], outline="green", width=3)

#         # for det in detections:
#         #     if det[4] > 0.3:  # confidence
#         #         faces_found = True
#         #         x, y, w, h = det[0:4]
#         #         x1 = int(x - w / 2)
#         #         y1 = int(y - h / 2)
#         #         x2 = int(x + w / 2)
#         #         y2 = int(y + h / 2)
#         #         draw.rectangle([x1, y1, x2, y2], outline="green", width=3)
#         if faces_found:
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             filename = f"kivy_photo_{timestamp}.jpg"
#             filepath = f"/storage/emulated/0/DCIM/Camera/{filename}"

#             try:
#                 rotated = frame.rotate(90, expand=True).convert("RGB")
#                 os.makedirs(os.path.dirname(filepath), exist_ok=True)
#                 rotated.save(filepath, format='JPEG', quality=95)
#                 self.status_label.text = f"✅ Saved with face to:\n{filepath}"
#             except Exception as e:
#                 self.status_label.text = f"❌ Save failed: {str(e)}"

#                     # frame.save(filepath)

#         else:
#             if not live_preview:
#                 self.status_label.text = "❌ No face found."

# if __name__ == '__main__':
#     FaceDetectApp().run()


from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.camera import Camera
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.utils import platform
from kivy.graphics import PushMatrix, PopMatrix, Rotate
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line

from datetime import datetime
import os
import numpy as np
from PIL import Image, ImageDraw
import tflite_runtime.interpreter as tflite
# import tensorflow as tf
from android.permissions import request_permissions, Permission
from kivy.graphics import Color, Line, Rectangle
from kivy.core.image import Image as CoreImage
from kivy.graphics.texture import Texture


# class BoxOverlay(Widget):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.boxes = []

#     def update_boxes(self, boxes,plot_frame):
#         self.canvas.clear()
#         with self.canvas:
#             Color(0, 1, 0)
#             for box in boxes:
#                 x1, y1, x2, y2 = box
#                 Line(rectangle=(x1, y1, x2 - x1, y2 - y1), width=2)

class BoxOverlay(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.boxes = []
        self.frame_texture = None  # This will hold the latest image

    # def update_frame(self, frame):
    #     """Update the current frame image as a texture (PIL.Image expected)"""
    #     data = frame.tobytes()
    #     tex = Texture.create(size=frame.size, colorfmt='rgb')
    #     tex.blit_buffer(data, colorfmt='rgb', bufferfmt='ubyte')
    #     # tex.flip_vertical()
    #     self.frame_texture = tex

    def update_boxes(self, boxes,frame,cos_sim):
        """Draw boxes and optionally image inside them."""
        self.canvas.clear()
        self.boxes = boxes
        with self.canvas:
            for box in boxes:
                x1, y1, x2, y2 = box
                

                frame = frame.crop(box).rotate(270, expand=True).convert("RGB")
                data = frame.tobytes()
                tex = Texture.create(size=frame.size, colorfmt='rgb')
                tex.blit_buffer(data, colorfmt='rgb', bufferfmt='ubyte')
                # tex.flip_vertical()
                self.frame_texture = tex

                # Optionally draw the cropped image as background inside the box
                if self.frame_texture:
                    Rectangle(texture=self.frame_texture, pos=(x1, y1), size=(x2 - x1, y2 - y1))
                if cos_sim>0.75:
                    r=0
                    g=1
                else:
                    r=1
                    g=0
                Color(r, g, 0, 0.5)
                Line(rectangle=(x1, y1, x2 - x1, y2 - y1), width=2)

class RotatedCamera(Camera):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            PushMatrix()
            self.rotation = Rotate(angle=90, origin=self.center)
        with self.canvas.after:
            PopMatrix()
        self.bind(size=self.update_origin, pos=self.update_origin)

    def update_origin(self, *args):
        self.rotation.origin = self.center


class FaceDetectApp(App):
    def build(self):
        if platform == 'android':
            request_permissions([
                Permission.CAMERA,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE
            ])
        self.known_embedding = None
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        self.camera = RotatedCamera(play=False, index=1)
        self.camera.resolution = (640, 480)

        self.start_btn = Button(text='▶️ Start Camera', size_hint=(1, 0.15))
        self.start_btn.bind(on_press=self.start_camera)

        self.stop_btn = Button(text='⏹ Stop Camera', size_hint=(1, 0.15))
        self.stop_btn.bind(on_press=self.stop_camera)
        self.stop_btn.disabled = True

        self.capture_btn = Button(text='📸 Save to Database', size_hint=(1, 0.15))
        self.capture_btn.bind(on_press=self.capture_frame)
        self.capture_btn.disabled = True

        self.status_label = Label(text='Status: Ready', size_hint=(1, 0.15))
        
        

        self.layout.add_widget(self.camera)
        
        self.layout.add_widget(self.start_btn)
        self.layout.add_widget(self.stop_btn)
        self.layout.add_widget(self.capture_btn)
        self.layout.add_widget(self.status_label)
        self.overlay = BoxOverlay()
        self.layout.add_widget(self.overlay)

        

        self.interpreter = tflite.Interpreter(model_path="yolov8n-face_float16.tflite")
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        self.recog_interpreter = tflite.Interpreter(model_path="facenet_512.tflite")
        self.recog_interpreter.allocate_tensors()
        self.recog_input = self.recog_interpreter.get_input_details()
        self.recog_output = self.recog_interpreter.get_output_details()

        return self.layout
    
    def preprocess_face(self, face_img):
        face = face_img.resize((160, 160)).convert("RGB")
        img_array = np.asarray(np.array(face).astype('float32'))#np.expand_dims(np.array(img_resized).astype(np.float32) / 255.0, axis=0)
        # Flatten to (H*W*C,) and standardize
        # pixels = img_array.flatten()
        # mean = pixels.mean()
        # std = pixels.std()
        # std = max(std, 1.0 / np.sqrt(pixels.size))  # Avoid division by zero
        # pixels = (pixels - mean) / std

        # # Reshape back to (H, W, C)
        # img_array = pixels.reshape((160,160, 3))
        img_array = (img_array - 127.5) / 128.0  # Scale to [-1,1]
        input_data = np.expand_dims(img_array, axis=0)  # (1,160,160,3)
        # input_data=np.expand_dims(img_array, axis=0)
        # face_array = np.asarray(face).astype("float32") / 255.0
        # face_array = (face_array - 0.5) / 0.5  # Normalize
        # face_array = np.expand_dims(face_array, axis=0)
        return input_data
    
    def get_embedding(self, face_img):
        face_input = self.preprocess_face(face_img)
        self.recog_interpreter.set_tensor(self.recog_input[0]['index'], face_input)
        self.recog_interpreter.invoke()
        embedding = self.recog_interpreter.get_tensor(self.recog_output[0]['index'])
        norm = np.linalg.norm(embedding, ord=2, axis=1, keepdims=True)
        embedding = embedding/norm
        return embedding[0]

    def non_max_suppression_numpy(self, boxes, scores, iou_threshold=0.5):
        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]

        areas = (x2 - x1) * (y2 - y1)
        order = scores.argsort()[::-1]

        keep = []
        while order.size > 0:
            i = order[0]
            keep.append(i)

            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])

            w = np.maximum(0.0, xx2 - xx1)
            h = np.maximum(0.0, yy2 - yy1)
            inter = w * h

            iou = inter / (areas[i] + areas[order[1:]] - inter)
            inds = np.where(iou <= iou_threshold)[0]
            order = order[inds + 1]

        return keep

    def start_camera(self, instance):
        self.camera.play = True
        self.start_btn.disabled = True
        self.stop_btn.disabled = False
        self.capture_btn.disabled = False
        self.status_label.text = "Status: Camera Started"
        Clock.schedule_interval(self.detect_face_live, 1.0)

    def stop_camera(self, instance):
        self.camera.play = False
        self.start_btn.disabled = False
        self.stop_btn.disabled = True
        self.capture_btn.disabled = True
        self.status_label.text = "Status: Camera Stopped"
        Clock.unschedule(self.detect_face_live)

    def capture_frame(self, instance):
        if hasattr(self, 'last_frame_with_boxes') and self.last_boxes:
            try:
                # draw = ImageDraw.Draw(self.last_frame_with_boxes)
                for box in self.last_boxes:
                    # draw.rectangle(box, outline="green", width=3)

                    # rotated = self.last_frame_with_boxes.crop(box).rotate(90, expand=True).convert("RGB")
                    # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    # filepath = f"/storage/emulated/0/DCIM/my_app/kivy_photo_{timestamp}.jpg"

                    # os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    # rotated.save(filepath, format='JPEG', quality=95)

                    # self.status_label.text = f"✅ Saved to:\n{filepath}"
                    
                    face_img = self.last_frame_with_boxes.crop(box).rotate(270, expand=True).convert("RGB")
                    embedding = self.get_embedding(face_img)

                    # Save embedding as known person
                    self.known_embedding = embedding  # Save the latest embedding
                    self.status_label.text = "✅ Face saved as known person."
            except Exception as e:
                self.status_label.text = f"❌ Save failed: {str(e)}"
        else:
            self.status_label.text = "⚠️ No face to save!"

    def detect_face_live(self, dt):
        self.detect_face_and_save(live_preview=True)

    def detect_face_and_save(self, live_preview=False):
        if not self.camera.texture:
            return

        texture = self.camera.texture
        size = texture.size
        pixels = np.frombuffer(texture.pixels, np.uint8).reshape(size[1], size[0], 4)

        # Get frame in original landscape orientation
        frame = Image.fromarray(pixels[..., :3], 'RGB')
        plot_frame = frame.copy()
        # Resize for the model
        # input_height, input_width = self.input_details[0]['shape'][1:3]
        # img_resized = frame.resize((input_width, input_height))
        img_resized = frame.resize((640, 640))
        input_data = np.expand_dims(np.array(img_resized).astype(np.float32) / 255.0, axis=0)
        print(input_data.shape)
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()

        # output = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
        output_raw = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
        output = output_raw.T  # now should be (8400, 5)
        print("Output shape:", output.shape)
        conf_mask = output[:, 4] > 0.2
        filtered_boxes = output[conf_mask]

        if filtered_boxes.shape[0] == 0:
            if not live_preview:
                self.status_label.text = "❌ No face found."
            return

        # Convert to x1, y1, x2, y2 for NMS
        x, y, w, h = filtered_boxes[:, 0], filtered_boxes[:, 1], filtered_boxes[:, 2], filtered_boxes[:, 3]
        x1 = x - w / 2
        y1 = y - h / 2
        x2 = x + w / 2
        y2 = y + h / 2
        boxes = np.stack([x1, y1, x2, y2], axis=1)
        scores = filtered_boxes[:, 4]

        # Run NumPy NMS
        keep_indices = self.non_max_suppression_numpy(boxes, scores, iou_threshold=0.5)

        selected_boxes = filtered_boxes[keep_indices]
        print("Selected boxes shape:", selected_boxes.shape)
        faces_found = False
        draw_boxes = []
        cos_sim=0
        for det in selected_boxes:
            x, y, w, h = det[0:4]
            x *= frame.width
            y *= frame.height
            w *= frame.width
            h *= frame.height

            x1 = int(max(0, x - w / 2))
            y1 = int(max(0, y - h / 2))
            x2 = int(min(frame.width, x + w / 2))
            y2 = int(min(frame.height, y + h / 2))

            draw_boxes.append((x1, y1, x2, y2))
            faces_found = True

            if self.known_embedding is not None:
                detected_face = frame.crop((x1, y1, x2, y2)).rotate(270, expand=True).convert("RGB")
                detected_embedding = self.get_embedding(detected_face)

                # distance = np.linalg.norm(detected_embedding - self.known_embedding)
                # print("Distance:", distance)
                cos_sim = np.dot(detected_embedding, self.known_embedding) / (np.linalg.norm(detected_embedding) * np.linalg.norm(self.known_embedding))

                if cos_sim > 0.8:
                    self.status_label.text = f"Known. {cos_sim}"
                else:
                    self.status_label.text = f"Unknown. {cos_sim}"

        # self.overlay.update_boxes(draw_boxes)
        #self.overlay.update_frame(frame)  # Set the latest camera frame
        self.overlay.update_boxes(draw_boxes,frame,cos_sim)

        if faces_found:
            self.last_frame_with_boxes = frame.copy()
            self.last_boxes = draw_boxes
            if not live_preview:
                self.status_label.text = f"✅ Face(s) detected. Press 📸 to save."
        else:
            self.overlay.update_boxes([],frame,cos_sim)
            if not live_preview:
                self.status_label.text = "❌ No face found."


if __name__ == '__main__':
    FaceDetectApp().run()
