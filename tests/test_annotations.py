import unittest
from otter import common
from otter import annotations

class TestApp(unittest.TestCase):

    def test_text_annotation(self):
        common.t = 2
        src = {
            'font-size': 20,
            'halign': 'center',
            'valign': 'middle',
            'color': [0.1, 0.2, 0.3],
            'opacity': 0.5,
            'shadow': False,
            'text': 'Text'
        }
        ann = annotations.AnnotationText(src)
        ann.result()._setInitialOptions()


        opts = ann.result().options()
        self.assertEqual(opts['font_size'], 20)
        self.assertEqual(opts['justification'], 'center')
        self.assertEqual(opts['vertical_justification'], 'middle')
        self.assertEqual(opts['text_color'], [0.1, 0.2, 0.3])
        self.assertEqual(opts['text_opacity'], 0.5)
        self.assertEqual(opts['text_shadow'], False)
        self.assertEqual(opts['text'], 'Text')

        ann.update(10.)

    def test_time_annotation(self):
        common.t = 2
        src = {
            'font-size': 20,
            'halign': 'center',
            'valign': 'middle',
            'color': [0.1, 0.2, 0.3],
            'opacity': 0.5,
            'shadow': False
        }
        ann = annotations.AnnotationTime(src)
        ann.result()._setInitialOptions()

        opts = ann.result().options()
        self.assertEqual(opts['font_size'], 20)
        self.assertEqual(opts['justification'], 'center')
        self.assertEqual(opts['vertical_justification'], 'middle')
        self.assertEqual(opts['text_color'], [0.1, 0.2, 0.3])
        self.assertEqual(opts['text_opacity'], 0.5)
        self.assertEqual(opts['text_shadow'], False)
        self.assertEqual(opts['text'], 'Time: 2.00 seconds')

        ann.update(10.)
        opts = ann.result().options()
        self.assertEqual(opts['text'], 'Time: 10.00 seconds')

    def test_image_annotation(self):
        common.t = 2
        src = {
            'halign': 'center',
            'valign': 'center',
            'file': 'a.png'
        }
        ann = annotations.AnnotationImage(src)
        ann.result()._setInitialOptions()

        opts = ann.result().options()
        self.assertEqual(opts['horizontal_alignment'], 'center')
        self.assertEqual(opts['vertical_alignment'], 'center')
        self.assertEqual(opts['filename'], 'a.png')

        ann.update(10.)

    def test_build_text(self):
        common.t = 2
        ann = [
            {
                'type': 'Text',
                'text': 'ASDF'
            }
        ]

        objs = annotations.process(ann)
        self.assertEqual(isinstance(objs[0], annotations.AnnotationText), True)

    def test_build_time(self):
        ann = [
            {
                'type': 'Time'
            }
        ]

        objs = annotations.process(ann)
        self.assertEqual(isinstance(objs[0], annotations.AnnotationTime), True)

    def test_build_image(self):
        ann = [
            {
                'type': 'Image',
                'file': 'a.png'
            }
        ]

        objs = annotations.process(ann)
        self.assertEqual(isinstance(objs[0], annotations.AnnotationImage), True)

    def test_build_unknown_type(self):
        ann = [
            {
                'type': 'ASDF'
            }
        ]

        objs = annotations.process(ann)
        self.assertEqual(objs, [])

    def test_missing_type(self):
        ann = [
            {
            }
        ]

        objs = annotations.process(ann)
        self.assertEqual(objs, [])


if __name__ == '__main__':
    unittest.main()
