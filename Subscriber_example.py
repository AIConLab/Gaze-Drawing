import zmq
ctx = zmq.Context()
# The REQ talks to Pupil remote and receives the session unique IPC SUB PORT
pupil_remote = ctx.socket(zmq.REQ)

ip = 'localhost'  # If you talk to a different machine use its IP.
port = 50020  # The port defaults to 50020. Set in Pupil Capture GUI.

pupil_remote.connect(f'tcp://{ip}:{port}')

# Request 'SUB_PORT' for reading data
pupil_remote.send_string('SUB_PORT')
sub_port = pupil_remote.recv_string()

# Request 'PUB_PORT' for writing data
pupil_remote.send_string('PUB_PORT')
pub_port = pupil_remote.recv_string()

# Assumes `sub_port` to be set to the current subscription port
subscriber = ctx.socket(zmq.SUB)
subscriber.connect(f'tcp://{ip}:{sub_port}')
subscriber.subscribe('surface')  # receive all gaze messages

# we need a serializer
import msgpack

while True:
    topic, payload = subscriber.recv_multipart()
    message = msgpack.loads(payload)
    
    for key, value in message.items():
        if key == 'gaze_on_surfaces':
            for gaze_data in value:
                if 'norm_pos' in gaze_data:
                    x, y = gaze_data['norm_pos']
                    print(f"X: {x}, Y: {y}")