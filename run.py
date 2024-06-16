import os # to let me manage files and install packages with pip

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

# This function finds a chemical's CAS number and DOT hazards. 
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

	#delete output.txt if it already exists
	try:
	    os.remove("output.txt")
	except OSError:
	    pass

	# Create output.txt
	with open("output.txt", "w", encoding='utf-8') as f:
		f.write(driver.page_source)
	with open("output.txt","r", encoding='utf-8') as f:
		html_formatted = f.read()

	search_string = r"""data-testid="sds-"""	
	spot = html_formatted.index(search_string)
	print(spot)
	
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

# Download a pdf in the current directory, as "1.pdf"
def download_pdf(lnk):
	# remove 1.pdf if it exists (possibly due to program ending unexpectedly last time)
	try:
		os.remove("1.pdf")
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
	driver.get(lnk)
	driver.close

def get_info_from_pdf():
	
	return_GivenName = ""
	return_CAS = ""
	return_DOT = ""
	
	for myline in SDS_content:
		if myline[0:3] == "CAS":
			return_CAS = myline
			print(myline)
			break
	for myline in SDS_content:
		if myline[0:12] == "Product name":
			return_GivenName = myline[15:]
			print(myline)
			break
	DOT_info = SDS_content[SDS_content.index("DOT") : SDS_content.index("IMDG") ]
	
	if "Not dangerous goods" in DOT_info:
		return_DOT = "NA"
	else:
		DOT_class = DOT_info[DOT_info.index("Class") : DOT_info.index("Packing group")]
		print(DOT_class)
		return_DOT = DOT_class

	return([return_GivenName,return_CAS,return_DOT])






#pdf_url = get_sds_url("ethanolf")
#get_info_from_pdf(pdf_url)
download_pdf("https://www.sigmaaldrich.com/US/en/sds/mm/1.00967?userType=anonymous")









# Does the chemical (or a similar one) come up on MS's search engine? If not, cancel.
# Pull the SDS. Does the chemical have a CAS number? Does it have DOT info or is it "Not dangerous goods"?