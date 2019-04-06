import os
import sys
import argparse
import pickle
import h5py
import numpy as np

from tensorflow.keras import backend as K
from tensorflow.keras.callbacks import ModelCheckpoint, TensorBoard, EarlyStopping, ReduceLROnPlateau

from models.category_model import create_category_model


def load_data(data_type, data_dir):
    # Path for the cache-file.
    feature_cache_path = os.path.join(
        data_dir, 'feature_transfer_values_{}.h5'.format(data_type)
    )
    topics_cache_path = os.path.join(
        data_dir, 'topics_{}.pkl'.format(data_type)
    )

    feature_path_exists = os.path.exists(feature_cache_path)
    topic_path_exists = os.path.exists(topics_cache_path)
    if feature_path_exists and topic_path_exists:
        with h5py.File(feature_cache_path, 'r') as file:
            feature_obj = file['feature_values']
        with open(topics_cache_path, mode='rb') as file:
            topics = pickle.load(file)
    else:
        sys.exit('processed {} data does not exist.'.format(data_type))

    print('{} data loaded from cache-file.'.format(data_type))
    return feature_obj, topics


def train(model, train_data, val_data, args):
    # dataset
    features_train, topics_train = train_data

    # define callbacks
    path_checkpoint = 'weights/topic-weights-{epoch:02d}-{val_loss:.2f}.hdf5'
    callback_checkpoint = ModelCheckpoint(
        filepath=path_checkpoint,
        monitor='val_loss',
        verbose=1,
        save_best_only=True
    )
    callback_tensorboard = TensorBoard(
        log_dir='./weights/topic-logs/',
        histogram_freq=0,
        write_graph=True
    )
    callback_early_stop = EarlyStopping(monitor='val_loss', patience=args.early_stop, verbose=1)
    callback_reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=args.lr_decay, patience=4, verbose=1, min_lr=args.min_lr)
    callbacks = [callback_checkpoint, callback_tensorboard, callback_early_stop, callback_reduce_lr]

    # train model
    model.fit(
        x=features_train,
        y=topics_train,
        batch_size=args.batch_size,
        epochs=args.epochs,
        callbacks=callbacks,
        validation_data=val_data
    )

    print('\n\nModel training finished.')


def main(args):
    # Load pre-processed data
    features_train, topics_train = load_data(
        'train', args.data
    )
    features_val, topics_val = load_data(
        'val', args.data
    )
    print('\nFeatures shape:', features_train.shape)
    print('Topics shape:', topics_train.shape)

    # Create model
    model = create_category_model(features_train.shape[1:], topics_train.shape[1])
    print(model.summary())

    # Train model
    train(model, (features_train, topics_train), (features_val, topics_val), args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--data',
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dataset', 'processed_data'),
        help='Directory containing the processed dataset'
    )
    parser.add_argument(
        '--raw',
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dataset', 'coco_raw.pickle'),
        help='Path to the simplified raw coco file'
    )
    parser.add_argument('--batch_size', default=128, type=int, help='Batch Size')
    parser.add_argument('--epochs', default=100, type=int, help='Epochs')
    args = parser.parse_args()

    main(args)

