import os
import sys
import struct
import ctypes
from ctypes import wintypes
import glob
import shutil

import time
import calendar
from datetime import datetime, timedelta
import pause

import random
from math import modf

import praw
from imgurpython import ImgurClient
import urllib.request
import subprocess
from PIL import Image


# Load the settings
file = open("Settings.txt", "r")
for line in file: 
	lineParts = line.split(':')
	lineParts[0] = lineParts[0].strip()
	
	if len(lineParts) > 1:
		lineParts2 = lineParts[1].split('#')
		lineParts2[0] = lineParts2[0].strip()
	
	
	# Screen settings
	if lineParts[0] == 'imageHeight':
		imageHeight = int(lineParts2[0])
	
	if lineParts[0] == 'imageWidth':
		imageWidth = int(lineParts2[0])
	
	
	# subReddit choice
	if lineParts[0] == 'subRedditChoice':
		subRedditChoice = lineParts2[0]
		
	# Limit the number of images to be set each day	
	if lineParts[0] == 'imageNumLimit':
		imageNumLimit = int(lineParts2[0])  #1 Numeric
	
	
	# When to make the last wallpaper change - 1AM tomorrow
	if lineParts[0] == 'lastImageDay':
		lastImageDay = int(lineParts2[0])  #1 Numeric
	
	if lineParts[0] == 'lastImageHour':
		lastImageHour = lineParts2[0]  #"01" String
	
	if lineParts[0] == 'lastImageMin':
		lastImageMin = lineParts2[0]  #"00" String
	
	
	# When to reset the script - 9AM tomorrow
	if lineParts[0] == 'resetDay':
		resetDay = int(lineParts2[0])  #1 Numeric
	
	if lineParts[0] == 'resetHour':
		resetHour = lineParts2[0]  #"09" String
		
	if lineParts[0] == 'resetMin':
		resetMin = lineParts2[0]  #"00" String
file.close()


# Load the subReddits
file = open("subReddits.txt", "r")
subReddit = []
for line in file:
	lineParts = line.split(',')
	lineParts[0] = lineParts[0].strip()
	lineParts[1] = int(lineParts[1].strip())
	subReddit.append(lineParts)
file.close()


# Load the API credentials
file = open("API Credentials.txt", "r")
for line in file: 
	lineParts = line.split(':')
	lineParts[0] = lineParts[0].strip()
	
	if len(lineParts) > 1:
		lineParts[1] = lineParts[1].strip()
	
	
	# Reddit Credentials
	if lineParts[0] == 'Reddit_client_id':
		Reddit_client_id = lineParts[1]
	
	if lineParts[0] == 'Reddit_client_secret':
		Reddit_client_secret = lineParts[1]

	if lineParts[0] == 'Reddit_password':
		Reddit_password = lineParts[1]

	if lineParts[0] == 'Reddit_user_agent':
		Reddit_user_agent = lineParts[1]
	
	if lineParts[0] == 'Reddit_username':
		Reddit_username = lineParts[1]
	
	
	# Imgur Credentials
	if lineParts[0] == 'Imgur_client_id':
		Imgur_client_id = lineParts[1]
	
	if lineParts[0] == 'Imgur_client_secret':
		Imgur_client_secret = lineParts[1]
file.close()






def test_connection():
	while True:
		output = subprocess.Popen(["ping.exe", '8.8.8.8'],stdout = subprocess.PIPE).communicate()[0]

		if b'(0% loss)' in output:
			print("Connected!!")
			break
		else:
			time.sleep(10)

	return True



def download_reddit(submission):

	# Get the name of the image
	if len(submission.url) > 0 and '/' in submission.url:
		imageName = submission.url.split('/')[-1]
	
	# Generate the image directory including image name 
	imageNameTotal = os.path.join(imageLocation,imageName)
	print("Save location: ",imageNameTotal)

	# Download the image
	urllib.request.urlretrieve(submission.url, imageNameTotal)
	
	# Check image is suitable for a wallpaper
	img = Image.open(imageNameTotal)
	
	print("Image downloaded")
	
	# Not landscape? | Width too small? | Height too small?
	if img.height > img.width or img.width < imageWidth or img.height < imageHeight: 
		remove_image(img,imageNameTotal)
	img.close()

	return



def download_imgur(submission):

	# Image or album/gallery?
	if submission.url.find(".com/a/") == -1 & submission.url.find(".com/gallery/") == -1 : # Image
		
		# Get the image ID token
		splitA,splitB = submission.url.split(".com/")
		
		if splitB.find(".") == -1: # Name has an extension?
			token = splitB #No
		else:
			splitC,splitD = splitB.split(".") # Yes
			token = splitC
			
		img = imgur.get_image(token) # Get the info of the image
		imgur_download_image(img) # Download the image

	else: # Album/Gallery

		# Get the image ID token
		if submission.url.find(".com/a/") > -1: # Album
			splitA,splitB = submission.url.split("/a/")
		else: # Gallery
			splitA,splitB = submission.url.split("/gallery/")
		
		if splitB.find("#") == -1: # Album ID has image ID too?
			token = splitB # No
		else:
			splitC,splitD = splitB.split("#") # Yes
			token = splitC
		
		for img in imgur.get_album_images(token):
			imgur_download_image(img) # Download every image in the album

	print("Image downloaded")
	return



def imgur_download_image(img):
	imageType = img.type.split("/") # Grab the type of the image
	imageName = img.id + '.' + imageType[1] # Create the image name
	imageNameTotal = os.path.join(imageLocation,imageName)
	print("Save location: ",imageNameTotal)

	# Landscape? & Width big enough? & Height big enough?
	if img.height < img.width and img.width >= imageWidth and img.height >= imageHeight:
		try:
			urllib.request.urlretrieve(img.link, imageNameTotal) # Download image
		except Exception as e:
			print(type(e))
			print(e)
	return



def remove_image(img,imageNameTotal):
	img.close() # Close the image	
	time.sleep(1) # Wait for second to allow the image to close
	
	count = 0
	while True:
		try:
			os.remove(imageNameTotal) # Remove image if it's not correct
			print("Image deleted")
			break
		except IOError as e:
			print(count,"-- WinError",e.errno,": " ,e.strerror)
			img.close() # Attempt to close the image again
			time.sleep(1) # Wait for a second to allow the image to close
			count += 1
	return



def copy_windows_spotlight():

	print(" ")
	print(" ")
	print(" ")
	print("Windows Spotlight images")
	print("-----------------------------------------------------")
	print(" ")
	
	# Windows Spotlight directory
	spotlightPath = os.path.expanduser('~') + '\\AppData\\Local\\Packages\\Microsoft.Windows.ContentDeliveryManager_cw5n1h2txyewy\\LocalState\\Assets\\'
	
	# Generate a nice image name to replace the original. aa-az, ba-bz, ca-cz, da-dz
	az = []
	for letter in range(97,101):
		for letter2 in range(97,123):
			az.append(chr(letter)+chr(letter2))
		
	# Get a list of all of the photos
	imageSpotlightList = (sorted(glob.glob(spotlightPath + "\\*"), key=os.path.getmtime, reverse=True))

	# Change the wallpaper if the image is for a desktop
	for i, imSpotFile in enumerate(imageSpotlightList):
		print("i: ", i)
		# Generate the image directory including image name 
		imageNameTotal = os.path.join(imageLocation, az[i]  + '.jpg')
		print("Source:  ",imSpotFile)
		print("Save location:  ",imageNameTotal)
		
		shutil.copy2(imSpotFile, imageNameTotal)
		img = Image.open(imageNameTotal)

		# Not landscape? | Width too small? | Height too small?
		if img.height > img.width or img.width < imageWidth or img.height < imageHeight: 
			remove_image(img,imageNameTotal)
		img.close()
		print(" ")
		i += 1
	
	return



def process_images(imageLocation):

	print(" ")
	print(" ")
	print(" ")
	print("Processing images")
	print("-----------------------------------------------------")
	print(" ")
	
	aspectRatio = imageWidth/imageHeight	
	
	# Get images for today
	images = []
	for im in os.listdir(imageLocation):
		if os.path.isfile(imageLocation + im):
			images.append(im)
	imageNumber = len(images)

	
	
	# Crop all images that don't have the correct aspect ratio
	for i in range(imageNumber):
		print("Image " + str(i) + ": ",images[i])
		img = Image.open(imageLocation + images[i])

		print("Width: ",img.width, "  Height: ",img.height)
		print('Aspect ratio: %.5f' % (img.width/img.height))
		
		# Correct aspect ratio?
		if img.width/img.height != aspectRatio: # No
		
			if not os.path.exists(imageLocation + 'Originals/'):
				os.makedirs(imageLocation + 'Originals/')
			
			# Save an original copy - just in case this screws up the original.
			shutil.copy2(imageLocation + images[i], imageLocation + 'Originals/Original_' + images[i])
			
			# Does the width or height need trimming?
			if img.width/img.height < aspectRatio: # Too tall
				heightSlackHalf = (img.height - img.width / aspectRatio)/2
				temp = img.crop([0, heightSlackHalf, img.width, img.height-heightSlackHalf])
			else: # Too wide
				widthSlackHalf = (img.width - img.height * aspectRatio)/2
				temp = img.crop([widthSlackHalf, 0, img.width-widthSlackHalf, img.height])
			
			print('New aspect ratio: %.5f' % (temp.width/temp.height))
			temp.save(imageLocation+images[i],img.format)
			img.close()
			
		print(" ")
		
	return images, imageNumber



def set_wallpapers(images, imageNumber):

	print(" ")
	print(" ")
	print(" ")
	print("Setting wallpapers")
	print("-----------------------------------------------------")
	print(" ")
	
	# Limit the number of images per day. Just to stop the desktop from changing an unreasonable amount.
	# Just in case a large album is downloaded.
	# 15 hours. 200 images. 4Mins 30Secs per image
	if imageNumber > imageNumLimit:
		imageNumber = imageNumLimit

	

	# Get the epoch time for the last image change
	timeAddDays = datetime.now() + timedelta(days=lastImageDay)
	timeAddDaysFormatted = timeAddDays.strftime("%Y-%m-%d")
	timeLastImageString = timeAddDaysFormatted + "T" + lastImageHour + ":" + lastImageMin + ":00Z"
	timeLastImageEpoch = calendar.timegm(time.strptime(timeLastImageString, "%Y-%m-%dT%H:%M:%SZ"))
	print("Last change (GMT +0):",time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timeLastImageEpoch))," - Epoch:",timeLastImageEpoch)
	
	
	# Get the epoch time for the reset time - aka start the script again.
	timeAddDays = datetime.now() + timedelta(days=resetDay)
	timeAddDaysFormatted = timeAddDays.strftime("%Y-%m-%d")
	timeResetString = timeAddDaysFormatted + "T" + resetHour + ":" + resetMin + ":00Z"
	timeResetEpoch = calendar.timegm(time.strptime(timeResetString, "%Y-%m-%dT%H:%M:%SZ"))
	print("Reset time (GMT +0):",time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timeResetEpoch))," - Epoch:",timeResetEpoch)
	
	

	# Get the time of when this is started
	timeStartEpoch = calendar.timegm(time.gmtime())

	# Calculate the period for all wallpapers
	timeDiffEpoch = timeLastImageEpoch - timeStartEpoch		
	diffSplit = modf(timeDiffEpoch/60)
	diffSplit2 = modf(diffSplit[1]/60)
	print('{:d}:{:02d}:{:02d} to display all images  - Epoch: {:.0f}'.format(int(diffSplit2[1]),round(60 * diffSplit2[0]),round(60 * diffSplit[0]),timeDiffEpoch))
	
	# Calculate the period for each wallpaper
	timePerImage = timeDiffEpoch/imageNumber
	diffSplit = modf(timePerImage/60)
	diffSplit2 = modf(diffSplit[1]/60)
	print('{:d}:{:02d}:{:02d} time per image  - Epoch: {:.0f}'.format(int(diffSplit2[1]),round(60 * diffSplit2[0]),round(60 * diffSplit[0]),timePerImage))
	print(" ")
	
	print("Start time (GMT +0):",time.strftime('%H:%M:%S', time.localtime(timeStartEpoch))," - Epoch:",timeStartEpoch)
	
	
	
	
	# Update the desktop wallpaper	
	for i, image in enumerate(images):
		print("Wallpaper: ", i+1, " of ", imageNumber)
		
		# Change wallpaper
		user32 = ctypes.WinDLL('user32')
		SystemParametersInfo = user32.SystemParametersInfoW
		SystemParametersInfo.argtypes = ctypes.c_uint,ctypes.c_uint,ctypes.c_void_p,ctypes.c_uint
		SystemParametersInfo.restype = wintypes.BOOL
		SystemParametersInfo(0x0014, 0, imageLocation + image, 0x0001 | 0x0002)
		
		
		timeNowEpoch = calendar.timegm(time.gmtime())
		print("Changed at (GMT +0):",time.strftime('%H:%M:%S', time.localtime(timeNowEpoch))," - Epoch:",timeNowEpoch)
		print(" ")
		
		# Limit the number of images per day. Just to stop the desktop from changing an unreasonable amount.
		# Just in case a large album is downloaded.
		# 15 hours. 200 images. 4Mins 30Secs per image
		if i > imageNumLimit:
			break
		

		# Pause the script for a length of time until it's time to update the wallpaper
		pause.until(timeStartEpoch + (timePerImage*(i+1)))

	
	# Last image has been set until the reset time
	print("Final image set")
	print("Hibernating until (GMT +0):",time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timeResetEpoch))," - Epoch:",timeResetEpoch)
	pause.until(timeResetEpoch  + 2) # Plus 2 seconds to ensure a race condition doesn't happen with the next statment
	
	print("Pause until finished")
	while True:
	
		timeNowEpoch = calendar.timegm(time.gmtime())
	
		# Time to restart the script? 9am the following day.
		if timeNowEpoch > timeResetEpoch:
			print(" ")
			print(" ")
			print("Resetting time...!")
			print(" ")
			print(" ")
			break
		
		print("While True")
		time.sleep(5) # Sleep for 5 seconds if the time to restart hasn't been met yet.
	
	return

	







if __name__ == '__main__':
	
	while True: 

		# If connected to the internet. Continue.
		if test_connection():
			
			# Check for today's wallpapers directory and create if needed
			imageLocation = "D:/Dropbox/Current/Documents/Wallpapers/" + time.strftime("%Y-%m-%d", time.gmtime()) + "/"
			print("imageLocation:  ",imageLocation)
			if not os.path.exists(imageLocation):
				os.makedirs(imageLocation)

			
			# Connect to the APIs
			# -------------------
			# Reddit API
			reddit = praw.Reddit(client_id=Reddit_client_id,
								 client_secret=Reddit_client_secret,
								 password=Reddit_password,
								 user_agent=Reddit_user_agent,
								 username=Reddit_username)
			# Imgur API
			imgur = ImgurClient(Imgur_client_id, Imgur_client_secret)
			
		
			# Choose how to select a subReddit		
			# --------------------------------
			# Pick subReddit based on whether the day is an odd or even number
			if subRedditChoice == 'oddEven':
			
				oddEvenDay = modf(int(datetime.now().strftime("%d"))/2)
				if oddEvenDay == 0:
					subRedditPick = 0
				else:
					subRedditPick = 1
			
			# Pick subReddit based on a random number
			elif subRedditChoice == 'random':
			
				subRedditPick = random.randint(0,1)
			
			subRedditPick = 0
		

			# If 'wallpapers' ( == 0), get all photos from that subReddit
			# Otherwise, choose a few photos from the other subReddits
			if subRedditPick != 0:
				subRedditPick = list(range(1, len(subReddit)-1))

			
			# Get the number of subReddits selected
			# And set the first subReddit to collect from
			if type(subRedditPick) is list:
				subRedditLength = len(subRedditPick)
				subRedditCurrent = subRedditPick[0]
			else:
				subRedditLength = 0 # 0 is actually 1
				subRedditCurrent = 0
			
			
			# Cycle through the selected subReddits
			while subRedditCurrent <= subRedditLength:

				# Set the name and limit of the subReddit
				subRedditName,imageLimit = subReddit[subRedditCurrent]			
				subRedditCurrent += 1
				
				
				print(" ")
				print(" ")
				print(" ")
				print("subRedditName: ",subRedditName, " - imageLimit: ",imageLimit)
				print("-----------------------------------------------------")
				print(" ")

			
				# Get image links from Reddit's subReddit of choice
				for i, submission in enumerate(reddit.subreddit(subRedditName).hot(limit=imageLimit)):
					print('i: ',i)
					print('Title: ',submission.title)
					print('URL: ',submission.url)
					print('Created: ',time.strftime("%Y/%m/%d, %H:%M:%S", time.gmtime(submission.created)))
					

					# Download the image from the source?
					if submission.url.find("imgur") > -1:
						print("Source: Imgur")
						download_imgur(submission)
					elif submission.url.find("i.redd.it") > -1:
						print("Source: Reddit")
						download_reddit(submission)
					else: # Image source currently not supported
						imageSource = "N/A"
						print("Source: ",imageSource)
					
					print(" ")
				
				
			# Copy the Windows Spotlight images
			copy_windows_spotlight()
			
			# Process the imaages
			images, imageNumber = process_images(imageLocation)
			
			# Set the wallpapers
			set_wallpapers(images, imageNumber)
		
		
