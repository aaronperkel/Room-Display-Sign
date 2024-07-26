from flask import Flask, request, render_template, redirect, url_for
# import spidev
# import RPi.GPIO as GPIO
# from PIL import Image, ImageDraw, ImageFont
# import epd2in7  # Import your specific E Ink display library

app = Flask(__name__)

current_status_line_one = "Not Set"
current_status_line_two = "Not Set"
current_status_line_three = "Not Set"

# # Initialize the display
# epd = epd2in7.EPD()
# epd.init()
# epd.Clear(0xFF)
# width, height = epd.width, epd.height
# image = Image.new('1', (width, height), 255)  # 255: clear the frame
# font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)

# def display_message(message):
#     draw = ImageDraw.Draw(image)
#     draw.rectangle((0, 0, width, height), fill=255)  # Clear image
#     draw.text((10, 10), message, font=font, fill=0)
#     epd.display(epd.getbuffer(image))
#     epd.sleep()

@app.route('/')
def index():
	return render_template('index.html', 
    status_line_one=current_status_line_one,
    status_line_two=current_status_line_two,
    status_line_three=current_status_line_three)

@app.route('/set_status', methods=['POST'])
def set_status():
    global current_status_line_one, current_status_line_two, current_status_line_three
    current_status_line_one = request.form['line_one']
    current_status_line_two = request.form['line_two']
    current_status_line_three = request.form['line_three']
	# display_message(status)
    return redirect(url_for('index'))

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080)