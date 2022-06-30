"""Tests for local_radio components."""
import unittest

from parameterized import parameterized
from typing import Callable, List

import local_radio

class TrackSeekerTest(unittest.TestCase):

    @parameterized.expand(
        [
            ("Single Track", [100], lambda: 10, 0, 10),
            ("Seek First", [100, 300, 200], lambda: 10, 0, 10),
            ("Seek Second", [100, 300, 200], lambda: 110, 1, 10),
            ("Seek Third", [100, 300, 200], lambda: 520, 2, 120),
            ("Seek Boundary", [100, 300, 200], lambda: 400, 2, 0),
            ("Seek Large Time", [100, 300, 200], lambda: 1120, 2, 120),
            ("Seek Large Time Boundary", [100, 300, 200], lambda: 600, 0, 0),
        ]
    )
    def test_seek(
            self, name, track_durations_ms: List[int], get_time_fn: Callable[[], int], expected_track_index: int, expected_track_start_time_ms: int
    ):
        track_index, track_start_time_ms = local_radio.TrackSeeker(track_durations_ms=track_durations_ms, get_time_fn=get_time_fn).seek()
        self.assertEqual(track_index, expected_track_index)
        self.assertEqual(track_start_time_ms, expected_track_start_time_ms)

        
if __name__ == "__main__":
    unittest.main()

