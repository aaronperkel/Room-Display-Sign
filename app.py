from flask import Flask, request, render_template, redirect, url_for
import spidev
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd4in2_V2
from datetime import datetime

app = Flask(__name__)

epd = epd4in2_V2.EPD()
epd.init()
epd.Clear()
width, height = epd.width, epd.height
image = Image.new('1', (width, height), 255)
font18 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 18)
font24 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
font32 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 38)

current_status_line_one = "Not Set"
current_status_line_two = "Not Set"
current_status_line_three = "Not Set"

def display_message(line1, line2, line3):
    try:
        epd.init()
        epd.Clear()
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, width, height), fill=255)  # Clear the image

        # Calculate the width and height of each line of text
        line1_width, line1_height = draw.textsize(line1, font=font32)
        line2_width, line2_height = draw.textsize(line2, font=font24)
        line3_width, line3_height = draw.textsize(line3, font=font24)

        # Calculate the positions to center the text
        line1_x = (width - line1_width) // 2
        line2_x = (width - line2_width) // 2
        line3_x = (width - line3_width) // 2

        # Set the vertical positions with some spacing between lines
        line1_y = 80  # You can adjust this as needed
        line2_y = line1_y + line1_height + 29
        line3_y = line2_y + line2_height + 32

        # Draw the text
        draw.text((line1_x, line1_y), line1, font=font32, fill=0)
        draw.text((line2_x, line2_y), line2, font=font24, fill=0)
        draw.text((line3_x, line3_y), line3, font=font24, fill=0)

        date = datetime.today().strftime('%B %d, %Y')
        draw.text((5, 10), date, font=font18, fill=0)

        epd.display(epd.getbuffer(image))
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        epd.sleep()


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
    display_message(current_status_line_one, current_status_line_two, current_status_line_three)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)