
**One-line purpose:** swift-yolo pre-processing and augmentation
**Short summary:** scale=0.5, blur and togray=0.01
**Agent:** timeline started with the dataset_vespa_2026-02. Needed for [[dataset_roboflow_augmentation]]


---

affine scale=0.5 (50%-150% of original size)
blur, medianblur, to gray, clahe (Contrast Limited Adaptive Histogram Equalization): 0.01 (very rarely)

---


affine_scale = 0.5
albu_train_transforms = [
    dict(p=0.01, type='Blur'),
    dict(p=0.01, type='MedianBlur'),
    dict(p=0.01, type='ToGray'),
    dict(p=0.01, type='CLAHE'),
]
anchors = [
    [
        (
            10,
            13,
        ),
        (
            16,
            30,
        ),
        (
            33,
            23,
        ),
    ],
    [
        (
            30,
            61,
        ),
        (
            62,
            45,
        ),
        (
            59,
            119,
        ),
    ],
    [
        (
            116,
            90,
        ),
        (
            156,
            198,
        ),
        (
            373,
            326,
        ),
    ],
]
batch = 512
batch_shapes_cfg = dict(
    batch_size=1,
    extra_pad_ratio=0.5,
    img_size=192,
    size_divisor=32,
    type='BatchShapePolicy')
custom_hooks = [
    dict(
        ema_type='ExpMomentumEMA',
        momentum=0.0001,
        priority=49,
        strict_load=False,
        type='EMAHook',
        update_buffers=True),
]
data_root = 'Swift-YOLO_192/dataset/'
dataset_type = 'sscma.CustomYOLOv5CocoDataset'
deepen_factor = 0.33
default_hooks = dict(
    checkpoint=dict(
        interval=5, max_keep_ckpts=3, save_best='auto', type='CheckpointHook'),
    logger=dict(interval=100, type='sscma.TextLoggerHook'),
    param_scheduler=dict(
        lr_factor=0.01,
        max_epochs=300,
        scheduler_type='linear',
        type='YOLOv5ParamSchedulerHook'),
    sampler_seed=dict(type='DistSamplerSeedHook'),
    timer=dict(type='IterTimerHook'),
    visualization=dict(type='mmdet.DetVisualizationHook'))
default_scope = 'sscma'
env_cfg = dict(
    cudnn_benchmark=True,
    dist_cfg=dict(backend='nccl'),
    mp_cfg=dict(mp_start_method='fork', opencv_num_threads=0))
epochs = 300
height = 192
imgsz = (
    192,
    192,
)
input_type = 'image'
launcher = 'none'
load_from = 'Swift-YOLO_192/pretrain.pth'
log_level = 'INFO'
log_processor = dict(by_epoch=True, type='LogProcessor', window_size=50)
loss_bbox_weight = 0.05
loss_cls_weight = 0.5
loss_obj_weight = 1.0
lr = 0.02
lr_factor = 0.01
max_keep_ckpts = 3
model = dict(
    backbone=dict(
        act_cfg=dict(inplace=True, type='ReLU'),
        deepen_factor=0.33,
        norm_cfg=dict(eps=0.001, momentum=0.03, type='BN'),
        type='YOLOv5CSPDarknet',
        widen_factor=0.15),
    bbox_head=dict(
        head_module=dict(
            featmap_strides=[
                8,
                16,
                32,
            ],
            in_channels=[
                256,
                512,
                1024,
            ],
            num_base_priors=3,
            num_classes=4,
            type='sscma.DetHead',
            widen_factor=0.15),
        loss_bbox=dict(
            bbox_format='xywh',
            eps=1e-07,
            iou_mode='ciou',
            loss_weight=0.05,
            reduction='mean',
            return_iou=True,
            type='IoULoss'),
        loss_cls=dict(
            loss_weight=0.025000000000000005,
            reduction='mean',
            type='mmdet.CrossEntropyLoss',
            use_sigmoid=True),
        loss_obj=dict(
            loss_weight=0.09000000000000001,
            reduction='mean',
            type='mmdet.CrossEntropyLoss',
            use_sigmoid=True),
        obj_level_weights=[
            4.0,
            1.0,
            0.4,
        ],
        prior_generator=dict(
            base_sizes=[
                [
                    (
                        10,
                        13,
                    ),
                    (
                        16,
                        30,
                    ),
                    (
                        33,
                        23,
                    ),
                ],
                [
                    (
                        30,
                        61,
                    ),
                    (
                        62,
                        45,
                    ),
                    (
                        59,
                        119,
                    ),
                ],
                [
                    (
                        116,
                        90,
                    ),
                    (
                        156,
                        198,
                    ),
                    (
                        373,
                        326,
                    ),
                ],
            ],
            strides=[
                8,
                16,
                32,
            ],
            type='mmdet.YOLOAnchorGenerator'),
        prior_match_thr=4.0,
        type='sscma.YOLOV5Head'),
    data_preprocessor=dict(
        bgr_to_rgb=True,
        mean=[
            0.0,
            0.0,
            0.0,
        ],
        std=[
            255.0,
            255.0,
            255.0,
        ],
        type='mmdet.DetDataPreprocessor'),
    neck=dict(
        act_cfg=dict(inplace=True, type='ReLU'),
        deepen_factor=0.33,
        in_channels=[
            256,
            512,
            1024,
        ],
        norm_cfg=dict(eps=0.001, momentum=0.03, type='BN'),
        num_csp_blocks=3,
        out_channels=[
            256,
            512,
            1024,
        ],
        type='YOLOv5PAFPN',
        widen_factor=0.15),
    test_cfg=dict(
        max_per_img=300,
        multi_label=True,
        nms=dict(iou_threshold=0.65, type='nms'),
        nms_pre=30000,
        score_thr=0.001),
    type='sscma.YOLODetector')
model_test_cfg = dict(
    max_per_img=300,
    multi_label=True,
    nms=dict(iou_threshold=0.65, type='nms'),
    nms_pre=30000,
    score_thr=0.001)
momentum = 0.937
norm_cfg = dict(eps=0.001, momentum=0.03, type='BN')
num_classes = 4
num_det_layers = 3
obj_level_weights = [
    4.0,
    1.0,
    0.4,
]
optim_wrapper = dict(
    constructor='YOLOv5OptimizerConstructor',
    optimizer=dict(
        batch_size_per_gpu=512,
        lr=0.02,
        momentum=0.937,
        nesterov=True,
        type='SGD',
        weight_decay=0.0005),
    type='OptimWrapper')
param_scheduler = None
persistent_workers = True
pre_transform = [
    dict(file_client_args=dict(backend='disk'), type='LoadImageFromFile'),
    dict(type='LoadAnnotations', with_bbox=True),
]
prior_match_thr = 4.0
resume = False
save_interval = 5
strides = [
    8,
    16,
    32,
]
test_cfg = dict(type='TestLoop')
test_dataloader = dict(
    batch_size=512,
    dataset=dict(
        ann_file='valid/_annotations.coco.json',
        batch_shapes_cfg=dict(
            batch_size=1,
            extra_pad_ratio=0.5,
            img_size=192,
            size_divisor=32,
            type='BatchShapePolicy'),
        data_prefix=dict(img='valid/'),
        data_root='Swift-YOLO_192/dataset/',
        pipeline=[
            dict(
                file_client_args=dict(backend='disk'),
                type='LoadImageFromFile'),
            dict(scale=(
                192,
                192,
            ), type='YOLOv5KeepRatioResize'),
            dict(
                allow_scale_up=False,
                pad_val=dict(img=114),
                scale=(
                    192,
                    192,
                ),
                type='sscma.LetterResize'),
            dict(type='LoadAnnotations', with_bbox=True),
            dict(
                meta_keys=(
                    'img_id',
                    'img_path',
                    'ori_shape',
                    'img_shape',
                    'scale_factor',
                    'pad_param',
                ),
                type='mmdet.PackDetInputs'),
        ],
        test_mode=True,
        type='sscma.CustomYOLOv5CocoDataset'),
    drop_last=False,
    num_workers=8,
    persistent_workers=True,
    pin_memory=True,
    sampler=dict(shuffle=False, type='DefaultSampler'))
test_evaluator = dict(
    ann_file='Swift-YOLO_192/dataset/valid/_annotations.coco.json',
    metric='bbox',
    proposal_nums=(
        100,
        1,
        10,
    ),
    type='mmdet.CocoMetric')
test_pipeline = [
    dict(file_client_args=dict(backend='disk'), type='LoadImageFromFile'),
    dict(scale=(
        192,
        192,
    ), type='YOLOv5KeepRatioResize'),
    dict(
        allow_scale_up=False,
        pad_val=dict(img=114),
        scale=(
            192,
            192,
        ),
        type='sscma.LetterResize'),
    dict(type='LoadAnnotations', with_bbox=True),
    dict(
        meta_keys=(
            'img_id',
            'img_path',
            'ori_shape',
            'img_shape',
            'scale_factor',
            'pad_param',
        ),
        type='mmdet.PackDetInputs'),
]
train_ann = 'train/_annotations.coco.json'
train_cfg = dict(max_epochs=300, type='EpochBasedTrainLoop', val_interval=5)
train_data = 'train/'
train_dataloader = dict(
    batch_size=512,
    dataset=dict(
        ann_file='train/_annotations.coco.json',
        data_prefix=dict(img='train/'),
        data_root='Swift-YOLO_192/dataset/',
        filter_cfg=dict(filter_empty_gt=False, min_size=32),
        pipeline=[
            dict(
                file_client_args=dict(backend='disk'),
                type='LoadImageFromFile'),
            dict(type='LoadAnnotations', with_bbox=True),
            dict(
                _scope_='sscma',
                img_scale=(
                    192,
                    192,
                ),
                pad_val=114.0,
                pre_transform=[
                    dict(
                        file_client_args=dict(backend='disk'),
                        type='LoadImageFromFile'),
                    dict(type='LoadAnnotations', with_bbox=True),
                ],
                type='Mosaic'),
            dict(
                border=(
                    -96,
                    -96,
                ),
                border_val=(
                    114,
                    114,
                    114,
                ),
                max_rotate_degree=0.0,
                max_shear_degree=0.0,
                scaling_ratio_range=(
                    0.5,
                    1.5,
                ),
                type='YOLOv5RandomAffine'),
            dict(
                bbox_params=dict(
                    format='pascal_voc',
                    label_fields=[
                        'gt_bboxes_labels',
                        'gt_ignore_flags',
                    ],
                    type='BboxParams'),
                keymap=dict(gt_bboxes='bboxes', img='image'),
                transforms=[
                    dict(p=0.01, type='Blur'),
                    dict(p=0.01, type='MedianBlur'),
                    dict(p=0.01, type='ToGray'),
                    dict(p=0.01, type='CLAHE'),
                ],
                type='mmdet.Albu'),
            dict(type='YOLOv5HSVRandomAug'),
            dict(prob=0.5, type='mmdet.RandomFlip'),
            dict(
                meta_keys=(
                    'img_id',
                    'img_path',
                    'ori_shape',
                    'img_shape',
                    'flip',
                    'flip_direction',
                ),
                type='mmdet.PackDetInputs'),
        ],
        type='sscma.CustomYOLOv5CocoDataset'),
    num_workers=8,
    persistent_workers=True,
    pin_memory=True,
    sampler=dict(shuffle=True, type='DefaultSampler'))
train_pipeline = [
    dict(file_client_args=dict(backend='disk'), type='LoadImageFromFile'),
    dict(type='LoadAnnotations', with_bbox=True),
    dict(
        _scope_='sscma',
        img_scale=(
            192,
            192,
        ),
        pad_val=114.0,
        pre_transform=[
            dict(
                file_client_args=dict(backend='disk'),
                type='LoadImageFromFile'),
            dict(type='LoadAnnotations', with_bbox=True),
        ],
        type='Mosaic'),
    dict(
        border=(
            -96,
            -96,
        ),
        border_val=(
            114,
            114,
            114,
        ),
        max_rotate_degree=0.0,
        max_shear_degree=0.0,
        scaling_ratio_range=(
            0.5,
            1.5,
        ),
        type='YOLOv5RandomAffine'),
    dict(
        bbox_params=dict(
            format='pascal_voc',
            label_fields=[
                'gt_bboxes_labels',
                'gt_ignore_flags',
            ],
            type='BboxParams'),
        keymap=dict(gt_bboxes='bboxes', img='image'),
        transforms=[
            dict(p=0.01, type='Blur'),
            dict(p=0.01, type='MedianBlur'),
            dict(p=0.01, type='ToGray'),
            dict(p=0.01, type='CLAHE'),
        ],
        type='mmdet.Albu'),
    dict(type='YOLOv5HSVRandomAug'),
    dict(prob=0.5, type='mmdet.RandomFlip'),
    dict(
        meta_keys=(
            'img_id',
            'img_path',
            'ori_shape',
            'img_shape',
            'flip',
            'flip_direction',
        ),
        type='mmdet.PackDetInputs'),
]
val_ann = 'valid/_annotations.coco.json'
val_batch = 512
val_cfg = dict(type='ValLoop')
val_data = 'valid/'
val_dataloader = dict(
    batch_size=512,
    dataset=dict(
        ann_file='valid/_annotations.coco.json',
        batch_shapes_cfg=dict(
            batch_size=1,
            extra_pad_ratio=0.5,
            img_size=192,
            size_divisor=32,
            type='BatchShapePolicy'),
        data_prefix=dict(img='valid/'),
        data_root='Swift-YOLO_192/dataset/',
        pipeline=[
            dict(
                file_client_args=dict(backend='disk'),
                type='LoadImageFromFile'),
            dict(scale=(
                192,
                192,
            ), type='YOLOv5KeepRatioResize'),
            dict(
                allow_scale_up=False,
                pad_val=dict(img=114),
                scale=(
                    192,
                    192,
                ),
                type='sscma.LetterResize'),
            dict(type='LoadAnnotations', with_bbox=True),
            dict(
                meta_keys=(
                    'img_id',
                    'img_path',
                    'ori_shape',
                    'img_shape',
                    'scale_factor',
                    'pad_param',
                ),
                type='mmdet.PackDetInputs'),
        ],
        test_mode=True,
        type='sscma.CustomYOLOv5CocoDataset'),
    drop_last=False,
    num_workers=8,
    persistent_workers=True,
    pin_memory=True,
    sampler=dict(shuffle=False, type='DefaultSampler'))
val_evaluator = dict(
    ann_file='Swift-YOLO_192/dataset/valid/_annotations.coco.json',
    metric='bbox',
    proposal_nums=(
        100,
        1,
        10,
    ),
    type='mmdet.CocoMetric')
val_interval = 5
val_workers = 8
vis_backends = [
    dict(type='LocalVisBackend'),
    dict(type='TensorboardVisBackend'),
]
visualizer = dict(
    name='visualizer',
    type='sscma.FomoLocalVisualizer',
    vis_backends=[
        dict(type='LocalVisBackend'),
        dict(type='TensorboardVisBackend'),
    ])
weight_decay = 0.0005
widen_factor = 0.15
width = 192
work_dir = 'Swift-YOLO_192'
workers = 8
