# RS-Desktop-Wallpapers
Downloads images from Reddit, copies the current Windows Spotlight images, and sets them as the desktop wallpapers.





## Collecting Reddit images

It selects different sub Reddits depending on the day of the month or by a random number generated.

Only images uploaded to Reddit's service and Imgur are currently supported.
- i.redd.it links
- Any imgur links

### Day of the month

##### Change *subRedditChoice* to *oddEven*

If the day of the month is even, Eg. 2nd, 4th, 6th, etc, etc, it will collect images from the first sub Reddit specified in *subReddits.txt*.

If the day of the month is odd, Eg. 1st, 3rd, 5th, etc, etc, it will collect images from all of the sub Reddits specified in *subReddits.txt*, except for the first sub Reddit.

### Random

##### Change *subRedditChoice* to *random*

It will randomly choose between collecting images from the first sub Reddit specified in *subReddits.txt* and all of the other sub Reddits.

*subReddits.txt* is baised towards collecting images just from r/wallpapers because the images posted there are generally better for desktop wallpapers. Change and set the sub Reddits that you would like to collect images from in this file.



## Collecting Windows Spotlight images

It copies all of the current Windows Spotlight images that are landscape.


## Image processing

It checks to make sure that all images are in landscape and have a resolution that matches what is specified in *Settings.txt* or greater. If an image is protrait or doesn't have a suitable resolution, it deletes the image.

If the image doesn't have the correct aspect ratio, it will crop the centre of the image to match the resolution you've specified. If it does this, it copies the original image in to the folder *Originals* - just in case it crops out something important and you would like to use the image again. 

The resolution is chosen by entering a value for *imageHeight* and *imageWidth* in *Settings.txt*.

## Setting the desktop wallpapers

You set the time and date of the last image to be set. This is done in *Settings.txt*. 

- *lastImageDay* = This is added to todays date. Eg. 1 is tomrrow, 2 is the day after tomorrow, etc.
- *lastImageHour* and *lastImageMin* = This is the time of day. Eg.*lastImageHour : 01* and *lastImageMin : 00* is 1AM.


You set the time and date that it will restart the whole process again and start to collect new images. This is also done in *Settings.txt*. 

- *resetDay* = This is added to todays date. Eg. 1 is tomrrow, 2 is the day after tomorrow, etc.
- *resetHour* and *resetMin* = This is the time of day. Eg.*resetHour : 09* and *resetMin : 00* is 9AM.


It calculates the length of time between the first image to be set as a desktop wallpaper and the last image to be set. It then equally divides the time between the number of images and sets each image for that length of time. Eg. If there are 10 images, and the length of time between the first image and the last image to be set is 10 hours, each image is a desktop wallpaper for 1 hour. 

Just in case it downloads a large album or gallery, set *imageNumLimit* to the total number of images you would like it to set for the period of time you've set. Eg, if the period is 12 hours, and the maximum frequency of images to be set is one every 5 minutes, set this to 144. If there are more than 144 images, it will ignore the rest.

Once the last image is set or the limit is reached, it will wait until the reset time has been reached.

If the computer is put in to hibernation or sleep, this will just advance to the correct image that it had already allocated for the time slot. If the computer is shutdown or restarted, it will restart from the beginning. 

## Getting this project up and running

**Running the executable** - Jump to API keys

**Using the Python script** - You will need to install a number of Python modules, which can be easily installed using:

- `$ pip install praw`

- `$ pip install imgurpython'

- '$ pip install Image'

- '$ pip install subprocess'

- '$ pip install urllib'

### API keyss

You need to create apps for Reddit and Imgur and save their credentials in to *API Credentials.txt*. 

You can create the apps from here:
- Reddit API https://www.reddit.com/prefs/apps/
- Imgur API https://imgur.com/account/settings/apps


### Inputting the options in the the text files

Input settings and credentials into *Settings.txt* and *API Credentials.txt* by putting the data after the colon (:). Antyhing after a hash (#) will be ignored. Anthing on a separate line will also be ignored. No single or double quotes is required.

Only put one sub Reddit on each line of *subReddits.txt*. The name of the sub Reddit is first, followed by the number of images you want it to look at. The name of the sub Reddit and the number of images needs to be seperated by a comma (,). 
