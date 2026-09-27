import cv2


class PersonDetector:
    def __init__(self):
        self.camera = None
        self.face_detector = None
        self.available = False


    # ========================================================
    # START CAMERA
    # ========================================================

    def start(self):
        try:
            self.camera = cv2.VideoCapture(
                0,
                cv2.CAP_DSHOW
            )

            if not self.camera.isOpened():
                print(
                    "Camera unavailable."
                )

                self.available = False
                return False


            self.face_detector = cv2.CascadeClassifier(
                cv2.data.haarcascades
                + "haarcascade_frontalface_default.xml"
            )


            if self.face_detector.empty():
                print(
                    "Face detector could not load."
                )

                self.camera.release()
                self.camera = None

                self.available = False
                return False


            self.available = True

            print(
                "Camera protection active."
            )

            return True


        except Exception as error:
            print(
                f"Camera unavailable: {error}"
            )

            self.available = False

            return False


    # ========================================================
    # COUNT FACES
    # ========================================================

    def get_face_count(self):
        if not self.available:
            return 0


        if self.camera is None:
            return 0


        success, frame = self.camera.read()


        if not success:
            return 0


        small = cv2.resize(
            frame,
            None,
            fx=0.5,
            fy=0.5
        )


        gray = cv2.cvtColor(
            small,
            cv2.COLOR_BGR2GRAY
        )


        faces = self.face_detector.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(50, 50)
        )


        return len(faces)


    # ========================================================
    # STOP CAMERA
    # ========================================================

    def stop(self):
        if self.camera is not None:
            try:
                self.camera.release()

            except Exception:
                pass


        self.camera = None

        self.available = False