from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense


def create_category_model(input_shape, output_shape):
    """ Use pre-trained vgg19 model and add a custom classification layer """

    feature_input = Input(
        shape=input_shape, name='feature_input'
    )
    topic_output = Dense(output_shape, activation='sigmoid')(feature_input)  # Add the final classification layer

    # Define model
    model = Model(
        inputs=feature_input,
        outputs=topic_output
    )

    # Compile the model
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['binary_accuracy'])

    return model


def load_category_model(input_shape, output_shape, weights_path):
    """ Load topic model with pre-trained weights """

    model = create_category_model(input_shape, output_shape)

    try:
        model.load_weights(weights_path)
        print('Weights loaded.')
    except:
        print('Error trying to load weights.')
        
    return model

