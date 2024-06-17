# Drake Sorkhab, phys152boi@gmail.com
# Chem-Inventory-CAS-and-DOT-finder Python3.12 program for Windows

# This program will help you find the CAS numbers and DOT classes for a list of chemicals. Here's how it works:
# Step 1: You open the "TYPE CHEMICAL LIST HERE" file and type a list of chemicals, with one chemical per line. 
#	You'll likely paste this in from a spreadsheet of chemical inventories.
# Step 2: The program will go through your list, and try to locate an online SDS sheet for each one. It does this
#	By searching the chemical on Sigma Aldrich's website.
# Step 3: The program will attempt to find the chemical's data form the spreadsheet. It will find:
#	A. The CAS number (or "N/A" if there is none) [pulled from website]
#	B. The DOT class and info phrase (or "N/A" if it's not a DOT hazard) [pulled from SDS]
#	C. The name given by Sigma Aldrich for the chemical (I recommend checking this manually to make sure the correct chemical was found).
#	
#	By the way, if the program can't find anything on the chemical, either because Sigma can't find it or similar chemicals or because the contents of my get_chem_info() threw some unexpected error.
#
# Step 4: You go to the RESULTS folder and find 3 text files with all the results. I recommend pasting these contents into your spreadsheet if you have one.



import os # to let me manage files and install packages with pip

import sys # for debug, so you can initiate an exit (and inspect a file such as sds.txt) even when you're inside of a try statement

try:
	from pdfminer.high_level import extract_text # for extracting our SDS pdf into a text string
except:
	os.system("pip install pdfminer.six")
	from pdfminer.high_level import extract_text

try:
	import pyperclip # for reading the SDS text content that we'll put into the Windows clipboard
except:
	os.system("pip install pyperclip")
	import pyperclip

try:
	from selenium import webdriver # to launch an automated web browser
except:
	os.system("pip install selenium")
	from selenium import webdriver # to launch an automated web browser
from selenium.webdriver.chrome.service import Service as ChromeService # so that Chrome specifically can be used as the browser
from selenium.webdriver import Keys # for backspace key to clear a text box
#from selenium.webdriver.common.action_chains import ActionChains # to send key presses without specifying an HTML element to direct them at
from selenium.common.exceptions import WebDriverException # Basically this is used to tell us when HTML buttons aren't clickable

import time # for pausing	

# These are to extract text from an online PDF
#import requests
#import urllib.request

# This function finds the url of chemical's SDS sheet (and if there's none findable, it'll return "NO RESULTS FROM SIGMA").
# It does this by putting your queried chemical name into Millipore Sigma's search engine then pulling the 1st SDS.
# If MS's website has results for your chemical, then it'll return it as a list of [MS-given chemical name, CAS number, DOT hazards]
def get_sds_url(chemical_name):
	
	# THIS was an unnecessary "bug" fix that was only needed when the chemical_name started with a \t (which should be avoided anyway). The tab was being sent as a tab which took you out of the search box till you pressed a space key
	# If there's a space in the chemical name, and that space isn't the final character (so that means the name has 2+ words), then add a sacrificial word to the beginning so that the glitch of sendkeys() doesn't mess things up
	#if " " in chemical_name:	
	#	if chemical_name.index(" ") != len(chemical_name) -1 :
	#		chemical_name = "SACRIFICE " + chemical_name

	# Make the browser headless and set the URL of some existing chemical search 
	# because for some reason this works better then the general page of https://www.sigmaaldrich.com/US/en/search/
	url = "https://www.sigmaaldrich.com/US/en/search/testosterone?focus=products&page=1&perpage=30&sort=relevance&term=TESTosterone&type=product"
	options = webdriver.ChromeOptions() ; options.headless = True

	#options.add_experimental_option('prefs', {"download.default_directory": r"""C:\Users\Bold\CODE\py\Chem-Inventory-CAS-and-DOT-finder""", "download.prompt_for_download": False, "download.directory_upgrade": True, "plugins.always_open_pdf_externally": True })
	#self.driver = webdriver.Chrome(options=options)	

	# Initialise the driver used by Selenium
	driver = webdriver.Chrome()	
	
	# Load the webpage
	driver.get(url)

	# Maximize the window so all clickable buttons (namely the SDS download button) will appear later
	driver.maximize_window()
	
	# Close the cookies statement
	time.sleep(2)
	driver.find_element("xpath",r"""//*[@id="onetrust-accept-btn-handler"]""").click()

	# Clear the search bar of the current word (TESTosterone)
	time.sleep(2)
	for count in range(0,len("TESTosterone")):
		try:
			driver.find_element("xpath",r"""//*[@id="header-search-search-wrapper-input"]""").send_keys(Keys.BACKSPACE)
		except: #The "wrapper" part may or may not be present in the element, depending on your screen size
			driver.find_element("xpath",r"""//*[@id="header-search-search-input"]""").send_keys(Keys.BACKSPACE)
		
		
	# Type in your chemical name
	# print("\n\nSending keys: " + chemical_name + "\n\n")
	time.sleep(2)
	# Bug here, where the first word of a chemical name isn't typed.
	try:
		driver.find_element("xpath",r"""//*[@id="header-search-search-wrapper-input"]""").send_keys(chemical_name)
	except:
		# driver.find_element("xpath",r"""//*[@id="header-search-search-input"]""").click()
		driver.find_element("xpath",r"""//*[@id="header-search-search-input"]""").send_keys(chemical_name)

	
	# Click the "Search" button
	time.sleep(2)
	try:
		driver.find_element("xpath",r"""//*[@id="header-search-submit-search"]""").click()
	except:
		driver.find_element("xpath",r"""//*[@id="header-search-submit-search-wrapper"]""").click()	
	
	# Click the download button for the first SDS. Hopefully this is the chemical we were looking for and not just a similarly-spelled one.
	# We'll do this by extracting the html source, cleaning it through a text file somehow?, then finding the first download button's id from that, 		# then clicking the button.
	
	# driver.find_element("id","sds-MM1.94500").click()
	
	driver.execute_script("document.body.style.zoom='50%'")
	time.sleep(4)
	html_string = driver.page_source

	#delete html_output.txt if it already exists
	try:
	    os.remove("html_output.txt")
	except OSError:
	    pass

	# Create html_output.txt
	with open("html_output.txt", "w", encoding='utf-8') as f:
		f.write(driver.page_source)
	with open("html_output.txt","r", encoding='utf-8') as f:
		html_formatted = f.read()

	# Search the search-string for the download button's ID, which we know always begins with "sds-". If you can't find it in the search-string, you probably got a "No results" page from Sigma.
	search_string = r"""data-testid="sds-"""	
	try:
		spot = html_formatted.index(search_string) # We now know where in our HTML code the clickable button's name is
	except: # You probably got a "No results page" in Sigma's search engine
		return "NO RESULTS FROM SIGMA"
	# print(spot)

	# We'll now find the download button's name
	new_html = html_formatted[spot:spot+100] #This string should contain our button ID
	# print(new_html)

	button_name = new_html[ new_html.index("\"")+1 : new_html.index(" ")-1 ]
	# print(button_name)
	
	time.sleep(5)
	try:
		driver.find_element("id",button_name).click()
	except:
		driver.execute_script("document.body.style.zoom='75%'")
		try:
			driver.find_element("id",button_name).click()
		except:
			driver.execute_script("document.body.style.zoom='100%'")	
			driver.find_element("id",button_name).click()
			
	# click the English button
	time.sleep(4)
	driver.find_element("xpath",r"""//*[@id="sds-link-EN"]""").click()

	time.sleep(6)
	# The PDF is now open; switch Selenium's brain to the new window and get the PDF's url
	
	driver.switch_to.window(driver.window_handles[1])
	pdf_url = driver.current_url
	driver.close()
	print("Successfully found SDS link for ",chemical_name,". It is:\n" , pdf_url)
	return(pdf_url)

# Download a pdf in the current directory, though we won't know what Selenium has named it
def download_pdf(lnk):
	# remove CurrentSDS/CurrentSDS.pdf if it exists (due to a program running last time)
	try:
		os.remove("CurrentSDS/CurrentSDS.pdf")
	except OSError:
		pass
	
	dir_path = os.path.dirname(os.path.realpath(__file__)) # get current directory

	# Download the pdf with Selenium
	options = webdriver.ChromeOptions()
	options.add_experimental_option('prefs', {
	"download.default_directory": dir_path, #Change default directory for downloads
	#"download.prompt_for_download": False, #To auto download the file
	#"download.directory_upgrade": True,
	"plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome 
	})
	driver = webdriver.Chrome(options=options)
	
	driver.set_page_load_timeout(9) #It always hangs after downloading the PDF, for me. Setting this to only 5 seconds caused problems. Or maybe that wasn't the issue...

	try:
		driver.get(lnk)
	except: # Selenium stalled and timed out, but probably already downloaded the PDF successfully so we can continue with running
		pass
	print("\nPDF has been downloaded successfully.\n")

# Find out what our SDS file, which has been downloaded into the current directory, is named
def rename_and_move_SDS():
	filenames = next(os.walk(os.getcwd()), (None, None, []))[2]  # Get a list of all files
	print(filenames)
	# Go through the list to find the pdf. Hopefully there will be just 1, our SDS's pdf
	for item in filenames:
		# print(item[-3:])
		if item[-3:] == "pdf":
			os.system( "move " + item + " CurrentSDS/CurrentSDS.pdf" )
			# print(item + " just got moved.\n")
	# print("\nPDF has been moved successfully.\n")
	# unused_var = input("\nPause\n")

# Scrape our downloaded SDS, to get data on the chemical
def extract_our_SDS():
	
	# print("CHECKPOINT 000")

	print("Starting extract_our_SDS().")
	return_GivenName = ""  # The chemical name from the SDS. Let's get this in case we want to manually confirm later that the chemical is actually the one we're looking for, and not just a similar result that Sigma's search engine gave us
	return_CAS = "" # I adjusted the program so that the CAS actually is pulled from the html code and not the SDS anymore. It will still be done inside this function, though.
	return_DOT = ""
	
	# Extract the SDS content as a string
	SDS_content = extract_text("CurrentSDS/CurrentSDS.pdf")

	# print("CHECKPOINT 001")

	# Put the SDS content into a text file, for debug purposes. Call it "sds.txt", but delete the old file if it exists (due to a previous session) first.
	try:
		os.remove("sds.txt")
	except:
		pass


	# Some SDS's have strange characters that can't be written with write(). I should figure out why (ie characters aren't UTF-8), then find a fast way to exclude these characters.
	# For now, I instead append to the file one character at a time, with a try statement. This process takes longer (about 30 seconds), but works.
	for character in SDS_content:
		try:
			with open("sds.txt", "a") as f:
				f.write(character)
		except:
			print("Unwriteable character found in SDS_content string. Skipping to the next character.")



	# print("CHECKPOINT 002")

	try: # I don't care that much about the given name, so if it can't be found I'm just gonna let the program continue.
		# Get the SDS's product name, which should be after the first colon that comes after "Product", and end with a newling, on a standard Sigma SDS.
		myspot1 = SDS_content.index("Product name") #I'm gonna mark two spots in the SDS string, and the string I want is in between spot 1 and spot 2
		myspot1 = myspot1 + SDS_content[myspot1:].index(":") #Move down the start point on the page to the colon that comes eventually after "Product". Note that index() will return the index on your current truncated string and not the original string. So, that's why I had to add myspot1 again; to get the abolute position on SDS_content and not just the relative one. If this is confusing, just rewrite this part of the code, honestly.
		myspot2 = myspot1 + SDS_content[myspot1:].index("\n") #Set the endpoint at the first newline after that colon just found
		return_GivenName = SDS_content[myspot1:myspot2].replace(":","")
	except:
		return_GivenName = "COULD NOT LOCATE NAME FROM SDS."
	# If the chemical name string starts with one or more spaces, delete those initial spaces till they're all gone
	while return_GivenName[0] == " ":
		return_GivenName = return_GivenName[1:] # Delete the first character if it's a space. Don't use strip() to do this, since some chemicals have spaces in the middle of their names that need to not be deleted (i.e. "diethyl ether")

	# THIS SECTION'S NOW COMMENTED OUT CUZ THE SDS IS A NON-UNIFORMLY FORMATTED SOURCE FOR SCRAPING CAS DATA
	# Get the SDS's CAS number if it exists, which should be after a colon and right before the "1.2" section of the SDS
	#if "CAS" in SDS_content:		
	#	myspot2 = SDS_content.index("1.2")
	#	truncated_SDS_content = SDS_content[0:myspot2]
	#	myspot1 = truncated_SDS_content.rfind(":") + 1
	#	return_CAS = SDS_content[myspot1:myspot2].strip()
	#else:
	#	return_CAS = "N/A"

	# Get the CAS number from the webpage's source (which is now stored in our html_output.txt file from before)
	try:
		with open("html_output.txt","r", encoding='utf-8') as f:
			html_formatted = f.read()
		myspot2 = html_formatted.index("-alias-link") #The CAS number is stored in the html right before the first $-alias-link$ and right after a $data-testid="$  (I'm delimiting my phrases with dollar signs here)
		myspot1 = html_formatted[0:myspot2].rfind("data-testid")
		return_CAS = html_formatted[ myspot1 + 13 : myspot2 ]
		if return_CAS.replace("-","").isdigit(): #Make sure the CAS number is an actual CAS number and not nonsense
			pass #it's just digits and dashes, good
		else:
			return_CAS = "Unknown" #it's not digits and dashes and therefore not a CAS number. Probably cuz Sigma didnt have a CAS number for it even though it brought up SDS results (i.e. Bovine Serum), so the html search was garbled
	except:
		return_CAS = "Unknown"

	# print("Checkpoint 003")
	

	# Get the SDS's DOT info (class) IF it exists, which will be after the "Class:" text and before the "Proper" text
	if "Not dangerous goods" in SDS_content:
		return_DOT = "N/A"
	else: # It lacks the "Not dangerous goods" string and therefore DOES have DOT info
		truncated_SDS_content = SDS_content[SDS_content.index("DOT") : SDS_content.index("Proper") ] #This is the entire DOT section, which will be on every SDS even if there's no DOT info (i.e. non-hazardous)	
		return_DOT = truncated_SDS_content[truncated_SDS_content.index("Class") : -1 ].replace(":","") # Exclude the colon and final character which is a newline
		if return_DOT[-1] == " ": 
			return_DOT = return_DOT[:-1] # If the final character is a space, delete that space (but not other spaces in the DOT classification phrase)
	
	# print("Checkpoint 004")


	# print("\nSDS data has been extracted successfully.\n")
	# Return all 3 values to end the function
	print("Finishing extract_our_SDS().")
	return([return_GivenName,return_CAS,return_DOT])

# This function combines the others and gives you a chemical's Sigma name (or closest one Sigma can find), CAS number (if it exists), or DOT hazards (if there are any).
# If Sigma can't find any SDSs for this chemical, then it'll return all properties as "Unknown" (basically, an error).
# If Sigma finds an SDS but the chemical has no CAS or is non-DOT, then those categories will return as "N/A" (this is good and not an error).
def get_chem_info(chem_name):
	if chem_name.strip() == "": #If the name is just whitespace, return Unknowns (change this to blanks if you prefer). Usually, the input chem name is blank or just whitespace because it's from an empty cell of the spreadsheet the user pasted in to the TYPE CHEMICAL LIST HERE file.
		print("\n\nReturning Unknowns for " + chem_name + " because this line is just whitespace.\n\n")
		return ["Unknown","Unknown","Unknown"]

	# DEBUG LINE BELOW!
	if True: #set this to True if you're done debugging, and want the program to just move on if there's an error for a chemical, instead of stopping. Set this to False if you want the program to end when there's an error in this section, and tell you what the error is.
		try:
			pdf_url = get_sds_url(chem_name)
			if pdf_url == "NO RESULTS FROM SIGMA":
				print("\n\nReturning Unknowns for " + chem_name + "  because no results from Sigma.\n\n")
				return ["Unknown","Unknown","Unknown"]
			else:
				download_pdf(pdf_url)
				rename_and_move_SDS()
				return extract_our_SDS()
		except: # The program can have unexpected failures for various reasons. Most of the time, this is because Sigma gave you an SDS straight from a manufacturer (ie Roche), which isn't in Sigma's standard format
			print("\n\nReturning Unknowns for " + chem_name + "  because of an unexpected failure inside get_chem_info().\n\n")
			return ["Unknown","Unknown","Unknown"]
	else:
		pdf_url = get_sds_url(chem_name)
		if pdf_url == "NO RESULTS FROM SIGMA":
			print("\n\nReturning Unknowns for " + chem_name + "  because no results from Sigma.\n\n")
			return ["Unknown","Unknown","Unknown"]
		else:
			download_pdf(pdf_url)
			rename_and_move_SDS()
			return extract_our_SDS()
	




# The main part of the program will take the user's lits of chemicals, and one-by-one find the data on them. 
# In the end, the data will be written into the "RESULTS" text files.

# Take the user's list into a string
with open("TYPE CHEMICAL LIST HERE.txt" , "r") as f:
	chem_list = f.read()

# Delete any newlines at the end of the string. You don't want to delete all newlines, because any accidental newlines in the middle of the user's text file shouldn't be deleted. Thats because, if the user is copy-pasting from a spreadsheet, you want the results to also contain that accidental newline so that alignment is conserved.
while chem_list[-1] == "\n":
	chem_list = chem_list[:-1]

# Delete any tabs
chem_list = chem_list.replace("\t","")

# Convert the string into a list of the chemicals
chem_list = chem_list.split("\n") #separate each line of the user's text file as one chemical

# Delete the previous RESULTS files, if they exist
for filename in ["RESULTS/Sigma Names.txt", "RESULTS/CAS Numbers.txt", "RESULTS/DOT infos.txt"]:
	try:
	    os.remove(filename)
	except OSError:
	    pass

# Fill all 3 of the lists of data, one chemical at a time
for item in chem_list:
	print("$"+item+"$")
	chem_data = get_chem_info(item)
	with open("RESULTS/Sigma Names.txt", "a") as myfile:
		myfile.write(chem_data[0])
		myfile.write("\n")
	with open("RESULTS/CAS Numbers.txt", "a") as myfile:
		myfile.write(chem_data[1])
		myfile.write("\n")
	with open("RESULTS/DOT infos.txt", "a") as myfile:
		myfile.write(chem_data[2])	
		myfile.write("\n")

print("\n\n\n\n\nDone.")



# DEBUG NOTE
# - When you're giving the program to an inexperienced user, or are processing a large amount of chemicals, or just need the program to not stall at any error -- set the debug line in get_chem_info() to True!

# CURRENT ISSUES
# - Occasionally chemicals will give errors, which can also depend on their position in the input file. I increased sleep() times and it seems to have fixed this. Try increasing them even more if you experience issues.


# SUGGESTED IMPROVEMENTS
# - If a CAS number received isn't just digits and dashes, then that's definitely an error so just change it to "Unknown"
# - Grab the CAS number from the Sigma website html directly, instead of the SDS which can be formatted in ways that show up on the text file inconsistently
# - If the input text file has blank lines, their output should be blanks instead of "Unknown"s
# - If there's no SDS results on Sigma, but there is a "Did you mean [this chemical]" suggestion link, that should be automatically clicked and the program moves on to grab the SDS

# LESS GOOD SUGGESTED IDEAS
# - If it works and would be clickable in an Excel cell, when a chemical produces an SDS with Sigma but glitches, the final output should be a link to the Sigma SDS
# - And if there's no Sigma result at all, then the final output could be a google link that searches for the chemical?


