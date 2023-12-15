import heapq

from queue import Queue

import numpy as np

from src.app.common import signalBus
from src.app.common.client import WebSocketThread
from src.app.time_tracker import time_tracker
from src.app.types import Embedding, Bbox, Kps, MatchInfo
from .common import Face, ImageFaces
from .sort_plus import associate_detections_to_trackers, KalmanBoxTracker


class Target:
    """
    :param face: Face
    :ivar _hit_streak: frames of keeping existing in screen
    :ivar _frames_since_update: frames of keeping missing in screen
    :ivar face: Face
    :ivar _frames_since_identified: frames since reced
    :ivar _tracker: KalmanBoxTracker
    :ivar normed_embedding: Embedding
    """

    def __init__(self, face: Face):

        self._hit_streak = 0  # frames of keeping existing in screen
        self._frames_since_update = 0  # frames of keeping missing in screen
        self._frames_since_identified = 0
        self.face: Face = face
        self._tracker: KalmanBoxTracker = KalmanBoxTracker(face.bbox)
        self.normed_embedding: Embedding = np.zeros(512)

    @property
    def rec_satified(self) -> bool:
        if self._scale_satisfied and not self._if_matched and self.in_screen:
            return True
        elif self._if_matched and self._scale_satisfied and self._time_satisfied and self.in_screen:
            return True
        else:
            return False

    @property
    def colors(self):
        """
        state color
        :return:
        """
        red = (0, 0, 255)
        yellow = (50, 205, 255)
        green = (152, 251, 152)
        if self._if_matched:
            # 有匹配对象
            if self.face.match_info.score > 0.4:
                bbox_color = green
                name_color = green
            else:
                # 有匹配对象，但是匹配分数不够，定义为匹配失败的红色
                bbox_color = red
                name_color = red
        else:  # 还没有匹配到对象
            bbox_color = yellow
            name_color = yellow
        return bbox_color, name_color

    def update_pos(self, bbox: Bbox, kps: Kps, score: float):
        self.face.bbox = bbox
        self.face.kps = kps
        self.face.det_score = score

    def update_tracker(self, bbox: Bbox):
        """
        update tracker with bbox, and update state of continuation
        """
        self._frames_since_update = 0
        self._hit_streak += 1
        self._tracker.update(bbox)

    def unmatched(self):
        """
        update state of continuation
        :return:
        """
        self._frames_since_update += 1
        self._hit_streak = 0

    def old_enough(self, max_age: int) -> bool:
        """
        if the target is too old ,should be del
        """
        return self._frames_since_update > max_age

    @property
    def in_screen(self) -> bool:
        """
        if the target is in screen should be satisfied min_hits,forbid the shiver
        """
        min_hits = 3  # almost 0.1s if fps=30
        return self._hit_streak >= min_hits

    @property
    def get_predicted_tar(self) -> Face:
        """
        get predicted Face by tracker
        :return:
        """
        # get predicted bounding box from Kalman Filter
        bbox = self._tracker.predict()[0]
        predicted_face: Face = Face(
            bbox,
            self.face.kps,
            self.face.det_score,
            face_id=self.face.id,
            scene_scale=self.face.scene_scale)
        return predicted_face

    @property
    def name(self) -> str:
        return f'target[{self.face.id}]'

    @property
    def _time_satisfied(self) -> bool:
        """
        Checks if the time(frames) elapsed since the target was last identified exceeds a predefined threshold.
        """
        frames_threshold = 100  # almost 3 sec if fps=30
        if not self._if_matched:
            return False
        elif self._frames_since_identified < frames_threshold:
            self._frames_since_identified += 1
            return False
        else:
            self._frames_since_identified = 0
            return True

    @property
    def _scale_satisfied(self) -> bool:
        """
        if the scale of target is satisfied
        """
        scale_threshold = 0.03
        target_area = (self.face.bbox[2] - self.face.bbox[0]) * \
                      (self.face.bbox[3] - self.face.bbox[1])
        screen_area = (self.face.scene_scale[3] - self.face.scene_scale[1]) * (
                self.face.scene_scale[2] - self.face.scene_scale[0])
        return (target_area / screen_area) > scale_threshold

    @property
    def _if_matched(self) -> bool:
        return self.face.match_info.uid is not None


class Tracker:
    """
    tracker for a single target
    :param max_age: del as frames not matched
    :param min_hits: be treated normal
    :param iou_threshold: for Hungarian algorithm
    """

    def __init__(
            self,
            max_age=10,
            min_hits=1,
            iou_threshold=0.3
    ):
        super().__init__()

        # TODO: change dict to list
        self._targets: dict[int, Target] = {}
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self._recycled_ids = []

    def _update(self, image2update: ImageFaces):
        """
        according to the "memory" in Kalman tracker update former targets info by Hungarian algorithm
        :param image2update:
        """
        detected_tars: list[Face] = image2update.faces

        if self._targets:
            predicted_tars: list[Face] = self._clean_dying()
            # match predicted and detected
            matched, unmatched_det_tars, unmatched_pred_tars = associate_detections_to_trackers(
                detected_tars, predicted_tars, self.iou_threshold)

            # update pred_tar with matched detected tar
            for pred_tar, detected_tar in matched:
                self._targets[pred_tar.id].update_pos(
                    detected_tar.bbox, detected_tar.kps, detected_tar.det_score)

                self._targets[pred_tar.id].update_tracker(detected_tar.bbox)

            # update  state of continuation of  unmatched_pred_tars
            for unmatched_tar in unmatched_pred_tars:
                self._targets[unmatched_tar.id].unmatched()

        else:
            unmatched_det_tars: list[Face] = detected_tars

        # add new targets
        for detected_tar in unmatched_det_tars:
            new_id = self._generate_id()
            assert new_id not in self._targets, f'{new_id} is already in self._targets'
            detected_tar.id = new_id
            self._targets[new_id] = Target(face=detected_tar)

            # dev only
            self._targets[new_id].face.match_info = MatchInfo(
                uid=self._targets[new_id].name, score=0.0)

        self._clear_dead()

    def _clean_dying(self) -> list[Face]:
        """
        clean dying targets from tracker prediction
        :return tracker predictions
        """
        predicted_tars: list[Face] = []
        to_del: list[int] = []
        for tar in self._targets.values():
            raw_tar: Face = tar.get_predicted_tar
            # store key in self.self._targets.values()
            pos = raw_tar.bbox
            if np.any(np.isnan(pos)):
                to_del.append(raw_tar.id)
            # got new predict tars
            predicted_tars.append(raw_tar)

        #  del dying tars
        for k in to_del:
            assert k in self._targets, f'k = {k} not in self._targets'
            assert isinstance(k, int), "k in to_del,should be int"
            heapq.heappush(self._recycled_ids, k)
            del self._targets[k]
        return predicted_tars

    def _clear_dead(self):
        """
        clear dead targets
        """
        keys = []
        for tar in self._targets.values():
            # remove dead targets
            if tar.old_enough(self.max_age):
                keys.append(tar.face.id)
        for k in keys:
            try:
                del self._targets[k]
            except KeyError:
                print(f'KeyError: tar.id = {k}')
            else:
                heapq.heappush(self._recycled_ids, k)

    def _generate_id(self) -> int:
        """
        generate id as small as possible
        """
        try:
            return heapq.heappop(self._recycled_ids)
        except IndexError:
            return len(self._targets)


class IdentifyClient(WebSocketThread):
    """ Result widget model"""
    running_signal = signalBus.is_identify_running

    def __init__(self):
        super().__init__(ws_type="identify")
        self.result_queue = Queue()
        self.start()

    def receive(self, data: dict | str):
        """send to signalBus to results table"""
        import json
        if not isinstance(data, dict):
            data = json.loads(data)
        new_data = [data["id"], data["name"], data["time"]]
        self.result_queue.put(new_data)
        signalBus.identify_results.emit(new_data)


class Identifier(Tracker, IdentifyClient):
    def __init__(self):
        super().__init__()

    def identify(self, image2identify: ImageFaces) -> ImageFaces:
        """
        fill image2identify.faces with match info or return MatchInfo directly
        :param image2identify:
        :return: get image2identify match info
        """
        self._update(image2identify)
        self._search(image2identify)
        # [tar.face.match_info for tar in self._targets.values()]
        return ImageFaces(
            image2identify.nd_arr, [
                tar.face for tar in self._targets.values() if tar.in_screen])

    def _search(self, image2identify: ImageFaces):
        """
        search in a process and then update face.match_info
        :param image2identify:
        """
        for tar in self._targets.values():
            if tar.rec_satified:
                # TODO: to slow
                with time_tracker.track("Identifier.search"):
                    self.send(tar.face.face_image(image2identify.nd_arr))
                    res = self.result_queue.get()
                    if res[0]:
                        tar.face.match_info = MatchInfo(0.99, res[0])
