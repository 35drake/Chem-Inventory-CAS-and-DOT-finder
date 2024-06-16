import os # to let me manage files and install packages with pip

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
	time.sleep(1)
	driver.find_element("xpath",r"""//*[@id="onetrust-accept-btn-handler"]""").click()

	# Clear the search bar of the current word (TESTosterone)
	time.sleep(1)
	for count in range(0,len("TESTosterone")):
		try:
			driver.find_element("xpath",r"""//*[@id="header-search-search-wrapper-input"]""").send_keys(Keys.BACKSPACE)
		except: #The "wrapper" part may or may not be present in the element, depending on your screen size
			driver.find_element("xpath",r"""//*[@id="header-search-search-input"]""").send_keys(Keys.BACKSPACE)
		#
		
	# Type in your chemical name
	time.sleep(1)
	try:
		driver.find_element("xpath",r"""//*[@id="header-search-search-input"]""").send_keys(chemical_name)
	except:
		driver.find_element("xpath",r"""//*[@id="header-search-search-wrapper-input"]""").send_keys(chemical_name)
	
	# Click the "Search" button
	time.sleep(1)
	try:
		driver.find_element("xpath",r"""//*[@id="header-search-submit-search"]""").click()
	except:
		driver.find_element("xpath",r"""//*[@id="header-search-submit-search-wrapper"]""").click()	
	
	# Click the download button for the first SDS. Hopefully this is the chemical we were looking for and not just a similarly-spelled one.
	# We'll do this by extracting the html source, cleaning it through a text file somehow?, then finding the first download button's id from that, 		# then clicking the button.
	
	# driver.find_element("id","sds-MM1.94500").click()
	
	driver.execute_script("document.body.style.zoom='50%'")
	time.sleep(3)
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
	print(spot)

	# We'll now find the download button's name
	new_html = html_formatted[spot:spot+100] #This string should contain our button ID
	print(new_html)

	button_name = new_html[ new_html.index("\"")+1 : new_html.index(" ")-1 ]
	print(button_name)
	
	time.sleep(4)
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
	time.sleep(3)
	driver.find_element("xpath",r"""//*[@id="sds-link-EN"]""").click()

	time.sleep(5)
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
	
	driver.set_page_load_timeout(5) #It always hangs after downloading the PDF, for me

	driver.get(lnk)
	try:
		driver.close()
		# driver.quit()
	except:
		pass #Selenium must already be closed due to timeout being activated

# Find out what our SDS file, which has been downloaded into the current directory, is named
def rename_and_move_SDS():
	filenames = next(os.walk(os.getcwd()), (None, None, []))[2]  # Get a list of all files
	print(filenames)
	# Go through the list to find the pdf. Hopefully there will be just 1, our SDS's pdf
	for item in filenames:
		print(item[-3:])
		if item[-3:] == "pdf":
			os.system( "move " + item + " CurrentSDS/CurrentSDS.pdf" )
	print("There isn't any pdf downloaded into the directory.")

# Scrape our downloaded SDS, to get data on the chemical
def extract_our_SDS():
	return_GivenName = ""  # The chemical name from the SDS. Let's get this in case we want to manually confirm later that the chemical is actually the one we're looking for, and not just a similar result that Sigma's search engine gave us
	return_CAS = ""
	return_DOT = ""
	
	# Extract the SDS content as a string
	SDS_content = extract_text("CurrentSDS/CurrentSDS.pdf")

	# Put the SDS content into a text file, for debug purposes. Call it "SDS.txt", but delete the old file if it exists (due to a previous session) first.
	try:
		os.remove("SDS.txt")
	except OSError:
		pass
	with open("SDS.txt", "w") as f:
		f.write(SDS_content)

	# Get the SDS's product name, which should be after the first colon that comes after "Product", and end with a newling, on a standard Sigma SDS.
	myspot1 = SDS_content.index("Product name") #I'm gonna mark two spots in the SDS string, and the string I want is in between spot 1 and spot 2
	myspot1 = myspot1 + SDS_content[myspot1:].index(":") #Move down the start point on the page to the colon that comes eventually after "Product". Note that index() will return the index on your current truncated string and not the original string. So, that's why I had to add myspot1 again; to get the abolute position on SDS_content and not just the relative one. If this is confusing, just rewrite this part of the code, honestly.
	myspot2 = myspot1 + SDS_content[myspot1:].index("\n") #Set the endpoint at the first newline after that colon just found
	return_GivenName = SDS_content[myspot1:myspot2].replace(":","")

	# If the chemical name string starts with one or more spaces, delete those initial spaces till they're all gone
	while return_GivenName[0] == " ":
		return_GivenName = return_GivenName[1:] # Delete the first character if it's a space. Don't use strip() to do this, since some chemicals have spaces in the middle of their names that need to not be deleted (i.e. "diethyl ether")

	# Get the SDS's CAS number if it exists, which should be after a colon and right before the "1.2" section of the SDS
	if "CAS" in SDS_content:		
		myspot2 = SDS_content.index("1.2")
		truncated_SDS_content = SDS_content[0:myspot2]
		myspot1 = truncated_SDS_content.rfind(":") + 1
		return_CAS = SDS_content[myspot1:myspot2].strip()
	else:
		return_CAS = "N/A"
	
	# Get the SDS's DOT info (class) IF it exists, which will be after the "Class:" text and before the "Proper" text

	truncated_SDS_content = SDS_content[SDS_content.index("DOT") : SDS_content.index("Proper") ] #This is the entire DOT section, which will be on every SDS even if there's no DOT info (i.e. non-hazardous)	
	if "Not dangerous goods" in truncated_SDS_content:
		return_DOT = "N/A"
	else:
		return_DOT = truncated_SDS_content[truncated_SDS_content.index("Class") : -1 ].replace(":","") # Exclude the colon and final character which is a newline
		
	# Return all 3 values to end the function
	return([return_GivenName,return_CAS,return_DOT])




chem_name = input("Chemical name: ")
pdf_url = get_sds_url(chem_name)
if pdf_url == "NO RESULTS FROM SIGMA":
	print("No results, as Sigma doesn't have any chemicals that even sound like this chemical.\n")
else:
	download_pdf(pdf_url)
	rename_and_move_SDS()
	print(extract_our_SDS())
print("Done.")
