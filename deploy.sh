PI_LOC=ben@192.168.178.41
WHEEL_FILE=ai_image_frame-0.1.0-py3-none-any.whl

## Copy images
#ssh $PI_LOC mkdir -p ai_image_frame
#scp -r images $PI_LOC:ai_image_frame/
#scp -r logs $PI_LOC:ai_image_frame/

# Install the python package
poetry build
scp dist/$WHEEL_FILE $PI_LOC:ai_image_frame/
ssh $PI_LOC pip install ai_image_frame/$WHEEL_FILE
ssh $PI_LOC pip install ai_image_frame/$WHEEL_FILE --force-reinstall --no-deps
ssh $PI_LOC rm ai_image_frame/$WHEEL_FILE
