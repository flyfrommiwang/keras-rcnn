import keras.backend
import numpy
import tensorflow

import keras_rcnn.backend


def test_label():
    stride = 16
    feat_h, feat_w = (14, 14)
    img_info = (224, 224, 1)

    gt_boxes = numpy.zeros((91, 4))
    vgt_boxes = tensorflow.convert_to_tensor(gt_boxes,
                                             dtype=tensorflow.float32)  # keras.backend.variable(gt_boxes)

    all_bbox = keras_rcnn.backend.shift((feat_h, feat_w), stride)

    inds_inside, all_inside_bbox = keras_rcnn.backend.inside_image(all_bbox,
                                                                   img_info)

    argmax_overlaps_inds, bbox_labels = keras_rcnn.backend.label(vgt_boxes,
                                                                 all_inside_bbox,
                                                                 inds_inside)

    result1 = keras.backend.eval(argmax_overlaps_inds)
    result2 = keras.backend.eval(bbox_labels)

    assert result1.shape == (84,)

    assert result2.shape == (84,)


def test_propose():
    anchors = 9
    features = (14, 14)
    boxes = numpy.zeros((1, features[0], features[1], 4 * anchors))
    scores = numpy.random.rand(1, features[0], features[1], anchors)
    threshold = 0.5
    maximum = 100
    boxes = keras.backend.variable(boxes)
    scores = keras.backend.variable(scores)
    proposals = keras_rcnn.backend.propose(boxes, scores, maximum)
    assert keras.backend.eval(proposals).shape == (1, maximum, 4)


def test_non_max_suppression():
    boxes = numpy.zeros((1764, 4))
    scores = numpy.random.rand(14 * 14, 9).flatten()
    threshold = 0.5
    maximum = 100
    nms = tensorflow.image.non_max_suppression(boxes=boxes,
                                               iou_threshold=threshold,
                                               max_output_size=maximum,
                                               scores=scores)
    assert keras.backend.eval(nms).shape == (maximum,)


def test_filter_boxes():
    proposals = numpy.array([[0, 2, 3, 10], [-1, -5, 4, 8], [0, 0, 1, 1]])
    minimum = 3
    results = keras_rcnn.backend.filter_boxes(proposals, minimum)
    numpy.testing.assert_array_equal(keras.backend.eval(results),
                                     numpy.array([0, 1]))


def test_bbox_transform_inv():
    anchors = 9
    features = (14, 14)
    shifted = keras_rcnn.backend.shift(features, 16)
    boxes = numpy.zeros((features[0] * features[1] * anchors, 4))
    boxes = keras.backend.variable(boxes)
    pred_boxes = keras_rcnn.backend.bbox_transform_inv(shifted, boxes)
    assert keras.backend.eval(pred_boxes).shape == (1764, 4)


def test_resize_images():
    im = numpy.zeros((1, 1200, 1600, 3))
    shape = (256, 256)
    im = keras.backend.variable(im)
    resize = keras_rcnn.backend.resize_images(im, shape)
    assert keras.backend.eval(resize).shape == (1, 256, 256, 3)


def test_subsample_positive_labels():
    x = keras.backend.ones((10,))

    y = keras_rcnn.backend.subsample_positive_labels(x)

    numpy.testing.assert_array_equal(
        keras.backend.eval(x),
        keras.backend.eval(y)
    )

    x = keras.backend.ones((1000,))

    y = keras_rcnn.backend.subsample_positive_labels(x)

    assert keras.backend.eval(keras.backend.sum(y) < keras.backend.sum(x))


def test_subsample_negative_labels():
    x = keras.backend.zeros((10,))

    y = keras_rcnn.backend.subsample_negative_labels(x)

    numpy.testing.assert_array_equal(
        keras.backend.eval(x),
        keras.backend.eval(y)
    )

    x = keras.backend.zeros((1000,))

    y = keras_rcnn.backend.subsample_negative_labels(x)

    assert keras.backend.eval(keras.backend.sum(y) < keras.backend.sum(x))


def test_balance():
    x = keras.backend.zeros((91,))

    y = keras_rcnn.backend.balance(x)

    numpy.testing.assert_array_equal(
        keras.backend.eval(x),
        keras.backend.eval(y)
    )

    x = keras.backend.ones((91,))

    y = keras_rcnn.backend.balance(x)

    numpy.testing.assert_array_equal(
        keras.backend.eval(x),
        keras.backend.eval(y)
    )

    x = keras.backend.ones((1000,))

    y = keras_rcnn.backend.balance(x)

    assert keras.backend.eval(keras.backend.sum(y) < keras.backend.sum(x))


def test_crop_and_resize():
    image = keras.backend.variable(numpy.ones((1, 28, 28, 3)))

    boxes = keras.backend.variable(
        numpy.array([[[0.1, 0.1, 0.2, 0.2], [0.5, 0.5, 0.8, 0.8]]]))

    size = [7, 7]

    slices = keras_rcnn.backend.crop_and_resize(image, boxes, size)

    assert keras.backend.eval(slices).shape == (2, 7, 7, 3)


def test_inside_image():
    stride = 16
    features = (14, 14)

    all_anchors = keras_rcnn.backend.shift(features, stride)

    img_info = (224, 224, 1)

    inds_inside, all_inside_anchors = keras_rcnn.backend.inside_image(
        all_anchors, img_info)

    inds_inside = keras.backend.eval(inds_inside)

    assert inds_inside.shape == (84,)

    all_inside_anchors = keras.backend.eval(all_inside_anchors)

    assert all_inside_anchors.shape == (84, 4)


def test_overlap():
    x = numpy.asarray([
        [0, 10, 0, 10],
        [0, 20, 0, 20],
        [0, 30, 0, 30],
        [0, 40, 0, 40],
        [0, 50, 0, 50],
        [0, 60, 0, 60],
        [0, 70, 0, 70],
        [0, 80, 0, 80],
        [0, 90, 0, 90]
    ])
    x = keras.backend.variable(x)
    y = numpy.asarray([
        [0, 20, 0, 20],
        [0, 40, 0, 40],
        [0, 60, 0, 60],
        [0, 80, 0, 80]
    ])
    y = keras.backend.variable(y)
    overlapping = keras_rcnn.backend.overlap(x, y)
    overlapping = keras.backend.eval(overlapping)
    expected = numpy.array([
        [0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0, 0.0]
    ])

    numpy.testing.assert_array_equal(overlapping, expected)


def test_overlapping():
    stride = 16
    features = (14, 14)
    img_info = (224, 224, 1)
    gt_boxes = numpy.zeros((91, 4))
    gt_boxes = keras.backend.variable(gt_boxes)

    all_anchors = keras_rcnn.backend.shift(features, stride)

    inds_inside, all_inside_anchors = keras_rcnn.backend.inside_image(
        all_anchors, img_info)

    argmax_overlaps_inds, max_overlaps, gt_argmax_overlaps_inds = keras_rcnn.backend.overlapping(
        gt_boxes, all_inside_anchors, inds_inside)

    argmax_overlaps_inds = keras.backend.eval(argmax_overlaps_inds)
    max_overlaps = keras.backend.eval(max_overlaps)
    gt_argmax_overlaps_inds = keras.backend.eval(gt_argmax_overlaps_inds)

    assert argmax_overlaps_inds.shape == (84,)

    assert max_overlaps.shape == (84,)

    assert gt_argmax_overlaps_inds.shape == (91,)
