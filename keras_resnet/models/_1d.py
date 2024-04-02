# -*- coding: utf-8 -*-

"""
Vincenzo Dentamaro
keras_resnet.models._1d
~~~~~~~~~~~~~~~~~~~~~~~

This module implements popular one-dimensional residual models.
"""

import tensorflow.keras.backend
import tensorflow.keras.layers
import tensorflow.keras.models
import tensorflow.keras.regularizers
import tensorflow as tf
import keras_resnet.layers
from tensorflow.keras.layers import Lambda
def audioencoder2_(x):
   
   out_neurons = x.shape.as_list()[-1]

   print('Out Neurons '+str(out_neurons))
   branch_a = tensorflow.keras.layers.Conv1D(int(128), 1,activation='relu',strides=2)(x)
   
   branch_b = tensorflow.keras.layers.Conv1D(int(128), 1,activation='relu')(x)
   branch_b = tensorflow.keras.layers.Conv1D(int(128), 3,activation='relu',strides=2)(branch_b)

   branch_c = tensorflow.keras.layers.AveragePooling1D(3,strides=2)(x)
   branch_c = tensorflow.keras.layers.Conv1D(int(128), 3,activation='relu')(branch_c)

   branch_d = tensorflow.keras.layers.Conv1D(int(128), 1,activation='relu')(x)
   branch_d = tensorflow.keras.layers.Conv1D(int(128), 3,activation='relu')(branch_d)
   branch_d = tensorflow.keras.layers.Conv1D(int(128), 3,activation='relu',strides=2)(branch_d)

   out = tensorflow.keras.layers.concatenate([branch_a,branch_b,branch_c,branch_d],axis=1)
   return out
def audioencoder2(x):
   
   out_neurons = x.shape.as_list()[-1]

   a = x[:,0:5000,:]
   b = x[:,5000:10000,:]
   c = x[:,10000:15000,:]
   d = x[:,15000:20000,:]
   print('Out Neurons '+str(out_neurons))
   
   
   #x = tensorflow.keras.layers.Conv1D(features, 7, strides=2, use_bias=False, name="conv1")(x)

   branch_a = tensorflow.keras.layers.Conv1D(int(16), 7, strides=2, use_bias=False, activation='relu')(a)
   #branch_a = tensorflow.keras.layers.SeparableConv1D(int(32), 3,activation='relu')(branch_a)
   #branch_a = tensorflow.keras.layers.SeparableConv1D(int(32), 3,activation='relu',strides=2)(branch_a)

   branch_b = tensorflow.keras.layers.Conv1D(int(16), 7, strides=2, use_bias=False, activation='relu')(b)
   #branch_b = tensorflow.keras.layers.SeparableConv1D(int(32), 3,activation='relu')(branch_b)
   #branch_b = tensorflow.keras.layers.SeparableConv1D(int(32), 3,activation='relu',strides=2)(branch_b)

   branch_c = tensorflow.keras.layers.Conv1D(int(16), 7, strides=2, use_bias=False,activation='relu')(c)
   #branch_c = tensorflow.keras.layers.SeparableConv1D(int(32), 3,activation='relu')(branch_c)
   #branch_c = tensorflow.keras.layers.SeparableConv1D(int(32), 3,activation='relu',strides=2)(branch_c)

   branch_d = tensorflow.keras.layers.Conv1D(int(16), 7, strides=2, use_bias=False,activation='relu')(d)
   #branch_d = tensorflow.keras.layers.SeparableConv1D(int(32), 3,activation='relu')(branch_d)
   #branch_d = tensorflow.keras.layers.SeparableConv1D(int(32), 3,activation='relu',strides=2)(branch_d)
 
   out = tensorflow.keras.layers.concatenate([branch_a,branch_b,branch_c,branch_d],axis=1)
   return out

def audioencoder(model):
   
   out_neurons = model.shape.as_list()[-1]
   print('Out shape '+str(model.shape))
   print('out neuron '+str(out_neurons))
   x = tensorflow.keras.layers.Conv1D(int(out_neurons*1.0),2, activation='relu', padding='valid')(model)
   x = tensorflow.keras.layers.Dropout(0.5)(x)
   #x = tensorflow.keras.layers.Conv1D(int(out_neurons*0.5),2, activation='relu', padding='valid')(x)
   
   #x = tensorflow.keras.layers.MaxPooling1D(3, strides=2, padding="same")(x)
   return x
        

class ResNet1D(tensorflow.keras.Model):
    """
    Constructs a `tensorflow.keras.models.Model` object using the given block count.

    :param inputs: input tensor (e.g. an instance of `tensorflow.keras.layers.Input`)

    :param blocks: the network’s residual architecture

    :param block: a residual block (e.g. an instance of `keras_resnet.blocks.basic_1d`)

    :param include_top: if true, includes classification layers

    :param classes: number of classes to classify (include_top must be true)

    :param freeze_bn: if true, freezes BatchNormalization layers (ie. no updates are done in these layers)

    :param numerical_names: list of bool, same size as blocks, used to indicate whether names of layers should include numbers or letters

    :return model: ResNet model with encoding output (if `include_top=False`) or classification output (if `include_top=True`)

    Usage:

        >>> import keras_resnet.blocks
        >>> import keras_resnet.models

        >>> shape, classes = (224, 224, 3), 1000

        >>> x = tensorflow.keras.layers.Input(shape)

        >>> blocks = [2, 2, 2, 2]

        >>> block = keras_resnet.blocks.basic_1d

        >>> model = keras_resnet.models.ResNet(x, classes, blocks, block, classes=classes)

        >>> model.compile("adam", "categorical_crossentropy", ["accuracy"])
    """
    def __init__(
        self,
        inputs,
        blocks,
        block,
        include_top=True,
        classes=1000,
        freeze_bn=True,
        numerical_names=None,
        batch_norm = True,
        inifinite_training = False,
        *args,
        **kwargs
    ):
        print('modified version of REsnet1d')
        if inifinite_training:
            axis = 2
        else:
            axis = 1

        if numerical_names is None:
            numerical_names = [True] * len(blocks)
        
        
        features = 64#int(20000*0.05)
        
        x = tensorflow.keras.layers.ZeroPadding1D(padding=3, name="padding_conv1")(inputs)
        #x = tensorflow.keras.layers.Lambda(audioencoder2_,name='audioconv')(x)
        x = tensorflow.keras.layers.SeparableConv1D(features, 7, strides=2, use_bias=False, name="conv1")(x)
        if batch_norm:
            x = keras_resnet.layers.BatchNormalization(axis=axis, epsilon=1e-5, freeze=freeze_bn)(x)
        x = tensorflow.keras.layers.Activation("relu", name="conv1_relu")(x)
        
        x = tensorflow.keras.layers.MaxPooling1D(3, strides=2, padding="same", name="pool1")(x)
        outputs = []

        for stage_id, iterations in enumerate(blocks):
            for block_id in range(iterations):
                x = block(
                    features,
                    stage_id,
                    block_id,
                    numerical_name=(block_id > 0 and numerical_names[stage_id]),
                    freeze_bn=freeze_bn
                )(x)

            features *= 2
  
            outputs.append(x)

        if include_top:
            assert classes > 0

            #x = tensorflow.keras.layers.GlobalAveragePooling1D(name="pool5")(x)
            #x = Lambda( lambda v: tf.signal.stft(v,frame_length=1024,frame_step=256,fft_length=1024,), name='gen/FFTLayer')(x)
            #real = Lambda(tf.real)(x)
            #imag = Lambda(tf.imag)(x)
            #x = Lambda(lambda x: tf.complex(x[0], x[1]))([real, imag])

            #x = tensorflow.keras.layers.GlobalAveragePooling1D(name="pool6x")(x)
            #x = tensorflow.keras.layers.Lambda(audioencoder2,name='audioconv-end')(x)
            x = tensorflow.keras.layers.GlobalAveragePooling1D(name="pool5")(x)
            #x = tensorflow.keras.layers.Flatten()(x)
            x = tensorflow.keras.layers.Dense(classes, activation="softmax", name="fc1000")(x)

            super(ResNet1D, self).__init__(inputs=inputs, outputs=x, *args, **kwargs)
        else:
            x = tensorflow.keras.layers.GlobalAveragePooling1D(name="pool5")(x)
            x = tensorflow.keras.layers.Dense(1, activation='linear', name="regressor")(x)

            # Else output each stages features
            super(ResNet1D, self).__init__(inputs=inputs, outputs=x, *args, **kwargs)


class ResNet1D18(ResNet1D):
    """
    Constructs a `tensorflow.keras.models.Model` according to the ResNet18 specifications.

    :param inputs: input tensor (e.g. an instance of `tensorflow.keras.layers.Input`)

    :param blocks: the network’s residual architecture

    :param include_top: if true, includes classification layers

    :param classes: number of classes to classify (include_top must be true)

    :param freeze_bn: if true, freezes BatchNormalization layers (ie. no updates are done in these layers)

    :return model: ResNet model with encoding output (if `include_top=False`) or classification output (if `include_top=True`)

    Usage:

        >>> import keras_resnet.models

        >>> shape, classes = (224, 224, 3), 1000

        >>> x = tensorflow.keras.layers.Input(shape)

        >>> model = keras_resnet.models.ResNet18(x, classes=classes)

        >>> model.compile("adam", "categorical_crossentropy", ["accuracy"])
    """
    def __init__(self, inputs, blocks=None, include_top=True, classes=1000, freeze_bn=False, *args, **kwargs):
        if blocks is None:
            blocks = [2, 2, 2, 2]

        super(ResNet1D18, self).__init__(
            inputs,
            blocks,
            block=keras_resnet.blocks.basic_1d,
            include_top=include_top,
            classes=classes,
            freeze_bn=freeze_bn,
            *args,
            **kwargs
        )


class ResNet1D34(ResNet1D):
    """
    Constructs a `tensorflow.keras.models.Model` according to the ResNet34 specifications.

    :param inputs: input tensor (e.g. an instance of `tensorflow.keras.layers.Input`)

    :param blocks: the network’s residual architecture

    :param include_top: if true, includes classification layers

    :param classes: number of classes to classify (include_top must be true)

    :param freeze_bn: if true, freezes BatchNormalization layers (ie. no updates are done in these layers)

    :return model: ResNet model with encoding output (if `include_top=False`) or classification output (if `include_top=True`)

    Usage:

        >>> import keras_resnet.models

        >>> shape, classes = (224, 224, 3), 1000

        >>> x = tensorflow.keras.layers.Input(shape)

        >>> model = keras_resnet.models.ResNet34(x, classes=classes)

        >>> model.compile("adam", "categorical_crossentropy", ["accuracy"])
    """
    def __init__(self, inputs, blocks=None, include_top=True, classes=1000, freeze_bn=False, *args, **kwargs):
        if blocks is None:
            blocks = [3, 4, 6, 3]

        super(ResNet1D34, self).__init__(
            inputs,
            blocks,
            block=keras_resnet.blocks.basic_1d,
            include_top=include_top,
            classes=classes,
            freeze_bn=freeze_bn,
            *args,
            **kwargs
        )


class ResNet1D50(ResNet1D):
    """
    Constructs a `tensorflow.keras.models.Model` according to the ResNet50 specifications.

    :param inputs: input tensor (e.g. an instance of `tensorflow.keras.layers.Input`)

    :param blocks: the network’s residual architecture

    :param include_top: if true, includes classification layers

    :param classes: number of classes to classify (include_top must be true)

    :param freeze_bn: if true, freezes BatchNormalization layers (ie. no updates are done in these layers)

    :return model: ResNet model with encoding output (if `include_top=False`) or classification output (if `include_top=True`)

    Usage:

        >>> import keras_resnet.models

        >>> shape, classes = (224, 224, 3), 1000

        >>> x = tensorflow.keras.layers.Input(shape)

        >>> model = keras_resnet.models.ResNet50(x)

        >>> model.compile("adam", "categorical_crossentropy", ["accuracy"])
    """
    def __init__(self, inputs, blocks=None, include_top=True, classes=1000, freeze_bn=False, *args, **kwargs):
        if blocks is None:
            blocks = [3, 4, 6, 3]

        numerical_names = [False, False, False, False]

        super(ResNet1D50, self).__init__(
            inputs,
            blocks,
            numerical_names=numerical_names,
            block=keras_resnet.blocks.bottleneck_1d,
            include_top=include_top,
            classes=classes,
            freeze_bn=freeze_bn,
            *args,
            **kwargs
        )


class ResNet1D101(ResNet1D):
    """
    Constructs a `tensorflow.keras.models.Model` according to the ResNet101 specifications.

    :param inputs: input tensor (e.g. an instance of `tensorflow.keras.layers.Input`)

    :param blocks: the network’s residual architecture

    :param include_top: if true, includes classification layers

    :param classes: number of classes to classify (include_top must be true)

    :param freeze_bn: if true, freezes BatchNormalization layers (ie. no updates are done in these layers)

    :return model: ResNet model with encoding output (if `include_top=False`) or classification output (if `include_top=True`)

    Usage:

        >>> import keras_resnet.models

        >>> shape, classes = (224, 224, 3), 1000

        >>> x = tensorflow.keras.layers.Input(shape)

        >>> model = keras_resnet.models.ResNet101(x, classes=classes)

        >>> model.compile("adam", "categorical_crossentropy", ["accuracy"])
    """
    def __init__(self, inputs, blocks=None, include_top=True, classes=1000, freeze_bn=False, *args, **kwargs):
        if blocks is None:
            blocks = [3, 4, 23, 3]

        numerical_names = [False, True, True, False]

        super(ResNet1D101, self).__init__(
            inputs,
            blocks,
            numerical_names=numerical_names,
            block=keras_resnet.blocks.bottleneck_1d,
            include_top=include_top,
            classes=classes,
            freeze_bn=freeze_bn,
            *args,
            **kwargs
        )


class ResNet1D152(ResNet1D):
    """
    Constructs a `tensorflow.keras.models.Model` according to the ResNet152 specifications.

    :param inputs: input tensor (e.g. an instance of `tensorflow.keras.layers.Input`)

    :param blocks: the network’s residual architecture

    :param include_top: if true, includes classification layers

    :param classes: number of classes to classify (include_top must be true)

    :param freeze_bn: if true, freezes BatchNormalization layers (ie. no updates are done in these layers)

    :return model: ResNet model with encoding output (if `include_top=False`) or classification output (if `include_top=True`)

    Usage:

        >>> import keras_resnet.models

        >>> shape, classes = (224, 224, 3), 1000

        >>> x = tensorflow.keras.layers.Input(shape)

        >>> model = keras_resnet.models.ResNet152(x, classes=classes)

        >>> model.compile("adam", "categorical_crossentropy", ["accuracy"])
    """
    def __init__(self, inputs, blocks=None, include_top=True, classes=1000, freeze_bn=False, *args, **kwargs):
        if blocks is None:
            blocks = [3, 8, 36, 3]

        numerical_names = [False, True, True, False]

        super(ResNet1D152, self).__init__(
            inputs,
            blocks,
            numerical_names=numerical_names,
            block=keras_resnet.blocks.bottleneck_1d,
            include_top=include_top,
            classes=classes,
            freeze_bn=freeze_bn,
            *args,
            **kwargs
        )


class ResNet1D200(ResNet1D):
    """
    Constructs a `tensorflow.keras.models.Model` according to the ResNet200 specifications.

    :param inputs: input tensor (e.g. an instance of `tensorflow.keras.layers.Input`)

    :param blocks: the network’s residual architecture

    :param include_top: if true, includes classification layers

    :param classes: number of classes to classify (include_top must be true)

    :param freeze_bn: if true, freezes BatchNormalization layers (ie. no updates are done in these layers)

    :return model: ResNet model with encoding output (if `include_top=False`) or classification output (if `include_top=True`)

    Usage:

        >>> import keras_resnet.models

        >>> shape, classes = (224, 224, 3), 1000

        >>> x = tensorflow.keras.layers.Input(shape)

        >>> model = keras_resnet.models.ResNet200(x, classes=classes)

        >>> model.compile("adam", "categorical_crossentropy", ["accuracy"])
    """
    def __init__(self, inputs, blocks=None, include_top=True, classes=1000, freeze_bn=False, *args, **kwargs):
        if blocks is None:
            blocks = [3, 24, 36, 3]

        numerical_names = [False, True, True, False]

        super(ResNet1D200, self).__init__(
            inputs,
            blocks,
            numerical_names=numerical_names,
            block=keras_resnet.blocks.bottleneck_1d,
            include_top=include_top,
            classes=classes,
            freeze_bn=freeze_bn,
            *args,
            **kwargs
        )
