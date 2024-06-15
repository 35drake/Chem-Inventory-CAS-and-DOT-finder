import pyperclip # for reading the SDS text content that we'll put into the Windows clipboard

import time # for pausing
from selenium import webdriver # to launch an automated web browser
from selenium.webdriver.chrome.service import Service as ChromeService # so that Chrome specifically can be used as the browser
from selenium.webdriver import Keys # for backspace key to clear a text box
#from selenium.webdriver.common.action_chains import ActionChains # to send key presses without specifying an HTML element to direct them at

# Basically this is used to tell us when HTML buttons aren't clickable
from selenium.common.exceptions import WebDriverException

# These are to extract text from an online PDF
import io
import requests
import fitz
import wget




# This function finds a chemical's CAS number and DOT hazards. 
# It does this by putting your queried chemical name into Millipore Sigma's search engine then pulling the 1st SDS.
# If MS's website has results for your chemical, then it'll return it as a list of [MS-given chemical name, CAS number, DOT hazards]
def get_chem_info(chemical_name):
	return_GivenName = ""
	return_CAS = ""
	return_DOT = ""
	
	# Make the browser headless and set the URL of some existing chemical search 
	# because for some reason this works better then the general page of https://www.sigmaaldrich.com/US/en/search/
	url = "https://www.sigmaaldrich.com/US/en/search/testosterone?focus=products&page=1&perpage=30&sort=relevance&term=TESTosterone&type=product"
	options = webdriver.ChromeOptions() ; options.headless = True
	
	
	


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
	time.sleep(1)
	driver.find_element("xpath",r"""//*[@id="sds-link-EN"]""").click()

	time.sleep(5)
	# The PDF is now open; switch Selenium's brain to the new window and get the PDF's url
	
	driver.switch_to.window(driver.window_handles[1])
	print(driver.current_url)
	pdf_url = driver.current_url

	driver.close()
	# Save that PDF 
	wget.download(pdf_url)
	exit()





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


	# Grab this chemical's MS-given name. This is so the end user can look at it to make sure it's actually the same chemical they were looking for.
		

	time.sleep(10)
	
	
	return([return_GivenName,return_CAS,return_DOT])





#chemical_name = input("What's your chemical's name? ")
#get_chem_info(chemical_name)

print(get_chem_info("ethanol"))









# Does the chemical (or a similar one) come up on MS's search engine? If not, cancel.
# Pull the SDS. Does the chemical have a CAS number? Does it have DOT info or is it "Not dangerous goods"?