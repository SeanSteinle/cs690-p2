import tensorflow as tf

# List all physical devices
physical_devices = tf.config.experimental.list_physical_devices('GPU')
print("Physical GPUs: ", physical_devices)

# Check if TensorFlow is using the GPU
if physical_devices:
    print("TensorFlow is using the GPU")
else:
    print("TensorFlow is not using the GPU")
